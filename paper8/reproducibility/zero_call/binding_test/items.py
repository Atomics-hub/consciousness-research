"""Executable item-bank validation, rendering, and schedule materialization.

This module converts the structural JSON prototype into testable runtime
surfaces.  It recomputes every answer key independently, renders only declared
model-visible fields, and fingerprints the complete assigned schedule copied
from each self donor to its yoke recipient.
"""

from __future__ import annotations

import ast
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import hashlib
import heapq
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from .assignment import (
    CanonicalBlock,
    JointAssignment,
    SELF,
    YOKE,
    enumerate_allowed_assignments,
    validate_joint_assignment,
)


FAMILIES = ("work_score_allocation", "tool_budget_allocation")
VARIANT_IDS = ("CB00", "CB01", "CB10", "CB11")
ROLE_CUE = re.compile(
    r"\b(?:roles?|arms?|treatments?|control[-_ ]?groups?|experimental[-_ ]?groups?|"
    r"self[-_ ]?contingent|yokes?|yoked|donors?|recipients?|"
    r"enforcement[-_ ]?arms?|treatment[-_ ]?arms?|assignment[-_ ]?roles?)\b",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class ItemBankAudit:
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    pair_count: int
    family_counts: dict[str, int]
    payload_count: int
    slot_count: int
    recomputed_answer_count: int
    rendered_surface_count: int
    active_schedule_digest_count: int
    zero_dose_schedule_digest_count: int

    @property
    def passed(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["passed"] = self.passed
        return result


@dataclass(frozen=True, slots=True)
class MaterializedScheduleRow:
    session_id: str
    arm: str
    baseline_choice: str
    received_schedule: str
    donor_session_id: str
    pair_id: str
    dose: str
    schedule_digest: str
    schedule_json: str


@dataclass(frozen=True, slots=True)
class MaterializedAssignment:
    block_id: str
    stratum: str
    allowed_set_index: int
    pair_id: str
    dose: str
    rows: tuple[MaterializedScheduleRow, ...]

    @property
    def self_schedule_multiset(self) -> Counter[str]:
        return Counter(row.schedule_digest for row in self.rows if row.arm == SELF)

    @property
    def yoke_schedule_multiset(self) -> Counter[str]:
        return Counter(row.schedule_digest for row in self.rows if row.arm == YOKE)


def load_item_bank(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("item bank root must be a JSON object")
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _item_by_id(bank: Mapping[str, Any], pair_id: str) -> Mapping[str, Any]:
    matches = [item for item in bank.get("items", []) if item.get("pair_id") == pair_id]
    if len(matches) != 1:
        raise KeyError(f"expected exactly one item with pair_id {pair_id!r}")
    return matches[0]


def _variant_by_id(bank: Mapping[str, Any], variant_id: str) -> Mapping[str, Any]:
    variants = bank["presentation_counterbalance_v1"]["variants"]
    matches = [variant for variant in variants if variant.get("variant_id") == variant_id]
    if len(matches) != 1:
        raise KeyError(f"expected exactly one variant {variant_id!r}")
    return matches[0]


def variant_label_mapping(bank: Mapping[str, Any], variant_id: str) -> dict[str, str]:
    """Return the internal display-label recode; never include it in a surface."""

    return dict(_variant_by_id(bank, variant_id)["displayed_label_to_canonical"])


def _schedule(item: Mapping[str, Any], dose: str, canonical: str) -> Mapping[str, Any]:
    if dose not in {"active", "zero_dose"}:
        raise ValueError("dose must be active or zero_dose")
    if canonical not in {"low", "high"}:
        raise ValueError("canonical schedule must be low or high")
    return item[f"{dose}_schedule"][canonical]


def schedule_fingerprint(
    bank: Mapping[str, Any], pair_id: str, dose: str, canonical: str
) -> tuple[str, str]:
    schedule_json = _canonical_json(_schedule(_item_by_id(bank, pair_id), dose, canonical))
    return hashlib.sha256(schedule_json.encode("utf-8")).hexdigest(), schedule_json


def render_choice_interface(
    bank: Mapping[str, Any],
    *,
    pair_id: str,
    phase: str,
    dose: str,
    variant_id: str,
) -> dict[str, Any]:
    """Render a deterministic baseline or held-out choice surface."""

    if phase not in {"baseline", "followup"}:
        raise ValueError("phase must be baseline or followup")
    item = _item_by_id(bank, pair_id)
    variant = _variant_by_id(bank, variant_id)
    interface = bank["model_visible_interface"]
    lines = [
        interface["selection_template"],
        f"Task: {item['model_visible_task_description']}",
        "Payload: " + _canonical_json(item[phase]["model_visible_payload"]),
        "Options:",
    ]
    mapping = variant["displayed_label_to_canonical"]
    for label in variant["display_order"]:
        canonical = mapping[label]
        schedule = _schedule(item, dose, canonical)
        affordance = schedule["tool_affordance"]
        values = {
            "max_answer_slots": schedule["workload_cap"]["max_answer_slots"],
            "score_cap": schedule["score_cap"],
            "max_tool_calls": affordance["max_calls"],
            "tool_name": affordance["enabled_tools"][0] if affordance["enabled_tools"] else "none",
        }
        template_key = (
            "option_template_work_score"
            if item["family"] == "work_score_allocation"
            else "option_template_tool_budget"
        )
        lines.append(interface[template_key].replace("<LABEL>", label).format(**values))
    return {
        "payload_id": item[phase]["payload_id"],
        "text": "\n".join(lines),
    }


def render_execution_interface(
    bank: Mapping[str, Any],
    *,
    pair_id: str,
    dose: str,
    canonical: str,
) -> dict[str, Any]:
    """Render the one executable baseline payload; no enforcement arm is an input."""

    item = _item_by_id(bank, pair_id)
    schedule = _schedule(item, dose, canonical)
    payload = item["baseline"]["model_visible_payload"]
    ordinals = schedule["enabled_slot_ordinals"]
    enabled_slots = [payload["slots"][ordinal - 1] for ordinal in ordinals]
    affordance = schedule["tool_affordance"]
    description = (
        f"up to {schedule['workload_cap']['max_answer_slots']} answer slots; "
        f"at most {affordance['max_calls']} tool calls; "
        f"at most {schedule['score_cap']} points"
    )
    text = bank["model_visible_interface"]["execution_template"].format(
        configuration_description=description
    )
    return {
        "payload_id": item["baseline"]["payload_id"],
        "text": text,
        "task_description": item["model_visible_task_description"],
        "instruction": payload["instruction"],
        "enabled_slots": enabled_slots,
        "enabled_tools": list(affordance["enabled_tools"]),
        "max_tool_calls": affordance["max_calls"],
        "score_cap": schedule["score_cap"],
    }


def materialize_assignment(
    bank: Mapping[str, Any],
    block: CanonicalBlock,
    assignment: JointAssignment,
    *,
    pair_id: str,
    dose: str,
) -> MaterializedAssignment:
    """Bind each assignment row to the complete immutable donor schedule."""

    validate_joint_assignment(block, assignment)
    allowed = enumerate_allowed_assignments(block)
    if not 0 <= assignment.allowed_set_index < len(allowed):
        raise ValueError("assignment allowed-set index is out of range")
    if assignment != allowed[assignment.allowed_set_index]:
        raise ValueError("assignment is not the indexed member of the complete allowed set")

    self_rows = {row.session_id: row for row in assignment.sessions if row.arm == SELF}
    materialized: list[MaterializedScheduleRow] = []
    for row in assignment.sessions:
        donor = self_rows.get(row.donor_session_id)
        if donor is None:
            raise ValueError("every materialized row must reference a self donor")
        if donor.baseline_choice != row.received_schedule:
            raise ValueError("received schedule does not equal donor choice")
        canonical = "low" if donor.baseline_choice == "L" else "high"
        digest, schedule_json = schedule_fingerprint(bank, pair_id, dose, canonical)
        materialized.append(
            MaterializedScheduleRow(
                session_id=row.session_id,
                arm=row.arm,
                baseline_choice=row.baseline_choice,
                received_schedule=row.received_schedule,
                donor_session_id=row.donor_session_id,
                pair_id=pair_id,
                dose=dose,
                schedule_digest=digest,
                schedule_json=schedule_json,
            )
        )
    result = MaterializedAssignment(
        block_id=assignment.block_id,
        stratum=block.stratum,
        allowed_set_index=assignment.allowed_set_index,
        pair_id=pair_id,
        dose=dose,
        rows=tuple(materialized),
    )
    if result.self_schedule_multiset != result.yoke_schedule_multiset:
        raise AssertionError("complete self/yoke schedule fingerprint multisets differ")
    return result


def _safe_arithmetic(expression: str) -> int:
    tree = ast.parse(expression.replace(" mod ", "%"), mode="eval")

    def visit(node: ast.AST) -> int:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -visit(node.operand)
        if isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.Add, ast.Sub, ast.Mult, ast.Mod)
        ):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            return left % right
        raise ValueError(f"unsafe arithmetic syntax: {ast.dump(node)}")

    return visit(tree)


class _BooleanParser:
    def __init__(self, expression: str, values: Mapping[str, bool]) -> None:
        self.tokens = re.findall(r"XNOR|NAND|NOR|XOR|AND|OR|NOT|[ABC()]", expression)
        compact = re.sub(r"\s+", "", expression)
        if "".join(self.tokens) != compact:
            raise ValueError(f"unrecognized Boolean token in {expression!r}")
        self.values = values
        self.position = 0

    def parse(self) -> bool:
        result = self._or()
        if self.position != len(self.tokens):
            raise ValueError("trailing Boolean tokens")
        return result

    def _take(self, token: str) -> bool:
        if self.position < len(self.tokens) and self.tokens[self.position] == token:
            self.position += 1
            return True
        return False

    def _or(self) -> bool:
        value = self._xor()
        while self.position < len(self.tokens) and self.tokens[self.position] in {"OR", "NOR"}:
            operator = self.tokens[self.position]
            self.position += 1
            right = self._xor()
            value = value or right if operator == "OR" else not (value or right)
        return value

    def _xor(self) -> bool:
        value = self._and()
        while self.position < len(self.tokens) and self.tokens[self.position] in {"XOR", "XNOR"}:
            operator = self.tokens[self.position]
            self.position += 1
            right = self._and()
            value = (value != right) if operator == "XOR" else (value == right)
        return value

    def _and(self) -> bool:
        value = self._not()
        while self.position < len(self.tokens) and self.tokens[self.position] in {"AND", "NAND"}:
            operator = self.tokens[self.position]
            self.position += 1
            right = self._not()
            value = value and right if operator == "AND" else not (value and right)
        return value

    def _not(self) -> bool:
        if self._take("NOT"):
            return not self._not()
        if self._take("("):
            value = self._or()
            if not self._take(")"):
                raise ValueError("missing closing parenthesis")
            return value
        if self.position >= len(self.tokens) or self.tokens[self.position] not in self.values:
            raise ValueError("expected Boolean atom")
        atom = self.tokens[self.position]
        self.position += 1
        return self.values[atom]


def _shortest_path(slot: Mapping[str, Any]) -> int:
    source, target = slot["source_target"].split(">")
    graph: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for encoded in slot["edges"]:
        endpoints, weight_text = encoded.split(":")
        left, right = endpoints.split("-")
        weight = int(weight_text)
        graph[left].append((right, weight))
        graph[right].append((left, weight))
    queue = [(0, source)]
    best = {source: 0}
    while queue:
        distance, node = heapq.heappop(queue)
        if node == target:
            return distance
        if distance != best[node]:
            continue
        for neighbor, weight in graph[node]:
            candidate = distance + weight
            if candidate < best.get(neighbor, 10**12):
                best[neighbor] = candidate
                heapq.heappush(queue, (candidate, neighbor))
    raise ValueError("target is unreachable")


def _recompute_answer(pair_id: str, slot: Mapping[str, Any], fixture: Mapping[str, Any]) -> str:
    if pair_id == "WS01":
        return str(_safe_arithmetic(slot["prompt"]))
    if pair_id == "WS02":
        records = []
        for encoded in slot["records"]:
            identifier, priority, timestamp = encoded.split(":")
            records.append((int(priority), int(timestamp), identifier))
        return ",".join(identifier for _, _, identifier in sorted(records))
    if pair_id == "WS03":
        return str(sum(slot["entries"]))
    if pair_id == "WS04":
        values = {
            key: value == "1"
            for key, value in (part.split("=") for part in slot["values"].split(","))
        }
        return "1" if _BooleanParser(slot["expression"], values).parse() else "0"
    if pair_id == "WS05":
        return str(_shortest_path(slot))
    if pair_id == "WS06":
        reversed_text = slot["input"][::-1]
        k = int(slot["k"]) % len(reversed_text)
        return reversed_text[k:] + reversed_text[:k]

    key_fields = {
        "TB01": "key",
        "TB02": "sku",
        "TB03": "segment_id",
        "TB04": "route_id",
        "TB05": "calendar_id",
        "TB06": "token_id",
    }
    record = fixture[slot[key_fields[pair_id]]]
    if pair_id == "TB01":
        return str(record["code"])
    if pair_id == "TB02":
        return str(record["mass"] + 2 * record["rating"])
    if pair_id == "TB03":
        return str(sum(record["values"]) % 17)
    if pair_id == "TB04":
        return str(record["distance"] + 3 * record["toll"])
    if pair_id == "TB05":
        return ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")[record["weekday_index"]]
    if pair_id == "TB06":
        return str(int(record["hex_value"], 16))
    raise ValueError(f"unsupported pair {pair_id}")


def validate_item_bank(bank: Mapping[str, Any]) -> ItemBankAudit:
    errors: list[str] = []
    warnings = [
        "Frontier-model unsaturation and baseline choice positivity are empirical, not established here.",
        "The honest no-guarantee interface may weaken action-contingency salience and changes the interpretation.",
        "Active options bundle workload/tool budget with attainable score; component mechanisms are not isolated.",
    ]
    items = bank.get("items", [])
    if not isinstance(items, list):
        items = []
        errors.append("items must be a list")
    pair_ids = [item.get("pair_id") for item in items]
    if len(items) != 12 or bank.get("pair_count") != 12:
        errors.append("item bank must declare and contain exactly 12 pairs")
    if len(set(pair_ids)) != len(pair_ids):
        errors.append("pair IDs must be unique")

    family_counts = Counter(item.get("family") for item in items)
    if family_counts != Counter({FAMILIES[0]: 6, FAMILIES[1]: 6}):
        errors.append("item bank must contain six pairs in each target family")
    if bank.get("family_counts") != dict(family_counts):
        errors.append("declared family_counts do not equal item inventory")

    variants = bank.get("presentation_counterbalance_v1", {}).get("variants", [])
    variant_ids = [variant.get("variant_id") for variant in variants]
    variant_signatures = {
        (
            tuple(sorted(variant.get("displayed_label_to_canonical", {}).items())),
            tuple(variant.get("display_order", [])),
        )
        for variant in variants
    }
    if tuple(variant_ids) != VARIANT_IDS or len(variant_signatures) != 4:
        errors.append("counterbalance must contain four unique frozen factorial variants")
    for variant in variants:
        if set(variant.get("displayed_label_to_canonical", {})) != {"A", "B"}:
            errors.append(f"{variant.get('variant_id')}: label mapping must contain A/B")
        if set(variant.get("displayed_label_to_canonical", {}).values()) != {"low", "high"}:
            errors.append(f"{variant.get('variant_id')}: mapping must be bijective low/high")
        if set(variant.get("display_order", [])) != {"A", "B"}:
            errors.append(f"{variant.get('variant_id')}: order must contain A/B")

    payload_ids: set[str] = set()
    slot_ids: set[str] = set()
    recomputed = 0
    rendered = 0
    active_digests: set[str] = set()
    zero_digests: set[str] = set()
    for item in items:
        pair_id = item.get("pair_id", "<missing>")
        phase_slot_ids: dict[str, set[str]] = {}
        phase_inputs: dict[str, set[str]] = {}
        for phase in ("baseline", "followup"):
            payload = item.get(phase, {})
            payload_id = payload.get("payload_id")
            if not payload_id or payload_id in payload_ids:
                errors.append(f"{pair_id}/{phase}: payload ID missing or duplicate")
            else:
                payload_ids.add(payload_id)
            slots = payload.get("model_visible_payload", {}).get("slots", [])
            answer_key = payload.get("answer_key", {})
            ids = [slot.get("slot_id") for slot in slots]
            if len(slots) != 6 or len(set(ids)) != 6:
                errors.append(f"{pair_id}/{phase}: expected six unique slots")
            if set(ids) != set(answer_key):
                errors.append(f"{pair_id}/{phase}: answer-key IDs do not equal slot IDs")
            phase_slot_ids[phase] = set(ids)
            phase_inputs[phase] = {
                _canonical_json({key: value for key, value in slot.items() if key != "slot_id"})
                for slot in slots
            }
            fixture = payload.get("deterministic_tool_fixture", {})
            for slot in slots:
                slot_id = slot.get("slot_id")
                if slot_id in slot_ids:
                    errors.append(f"globally duplicate slot ID {slot_id}")
                slot_ids.add(slot_id)
                try:
                    actual = _recompute_answer(pair_id, slot, fixture)
                except Exception as error:
                    errors.append(f"{pair_id}/{phase}/{slot_id}: recomputation error: {error}")
                    continue
                recomputed += 1
                if str(answer_key.get(slot_id)) != actual:
                    errors.append(
                        f"{pair_id}/{phase}/{slot_id}: key {answer_key.get(slot_id)!r} != {actual!r}"
                    )
        if phase_slot_ids.get("baseline", set()) & phase_slot_ids.get("followup", set()):
            errors.append(f"{pair_id}: baseline/follow-up slot IDs overlap")
        if phase_inputs.get("baseline", set()) & phase_inputs.get("followup", set()):
            errors.append(f"{pair_id}: baseline/follow-up task inputs overlap")

        for dose in ("active", "zero_dose"):
            low = item.get(f"{dose}_schedule", {}).get("low")
            high = item.get(f"{dose}_schedule", {}).get("high")
            if low is None or high is None:
                errors.append(f"{pair_id}: missing {dose} schedules")
                continue
            if dose == "active" and low == high:
                errors.append(f"{pair_id}: active low/high schedules must differ")
            if dose == "zero_dose" and low != high:
                errors.append(f"{pair_id}: zero-dose low/high schedules must deep-match")
            for canonical, schedule in (("low", low), ("high", high)):
                ordinals = schedule.get("enabled_slot_ordinals", [])
                if ordinals != sorted(set(ordinals)) or any(not 1 <= value <= 6 for value in ordinals):
                    errors.append(f"{pair_id}/{dose}/{canonical}: invalid enabled ordinals")
                count = len(ordinals)
                if schedule.get("workload_cap", {}).get("max_answer_slots") != count:
                    errors.append(f"{pair_id}/{dose}/{canonical}: workload cap mismatch")
                if schedule.get("score_cap") != count:
                    errors.append(f"{pair_id}/{dose}/{canonical}: score cap mismatch")
                affordance = schedule.get("tool_affordance", {})
                if item.get("family") == "work_score_allocation":
                    if affordance.get("enabled_tools") != [] or affordance.get("max_calls") != 0:
                        errors.append(f"{pair_id}/{dose}/{canonical}: work item exposes tools")
                else:
                    tool_name = item.get("tool_contract", {}).get("tool_name")
                    if affordance.get("enabled_tools") != [tool_name]:
                        errors.append(f"{pair_id}/{dose}/{canonical}: tool affordance mismatch")
                    if affordance.get("max_calls") != count:
                        errors.append(f"{pair_id}/{dose}/{canonical}: tool-call cap mismatch")
                (active_digests if dose == "active" else zero_digests).add(_digest(schedule))
        if set(item.get("counterbalance", {}).get("required_variant_ids", [])) != set(VARIANT_IDS):
            errors.append(f"{pair_id}: does not require all counterbalance variants")

        for phase in ("baseline", "followup"):
            for dose in ("active", "zero_dose"):
                for variant_id in VARIANT_IDS:
                    try:
                        surface = render_choice_interface(
                            bank,
                            pair_id=pair_id,
                            phase=phase,
                            dose=dose,
                            variant_id=variant_id,
                        )
                    except Exception as error:
                        errors.append(f"{pair_id}: choice renderer failed: {error}")
                        continue
                    rendered += 1
                    if ROLE_CUE.search(surface["text"]):
                        errors.append(f"{pair_id}/{phase}/{dose}/{variant_id}: role cue in rendered choice")
        for dose in ("active", "zero_dose"):
            for canonical in ("low", "high"):
                try:
                    surface = render_execution_interface(
                        bank, pair_id=pair_id, dose=dose, canonical=canonical
                    )
                except Exception as error:
                    errors.append(f"{pair_id}: execution renderer failed: {error}")
                    continue
                rendered += 1
                if ROLE_CUE.search(_canonical_json(surface)):
                    errors.append(f"{pair_id}/{dose}/{canonical}: role cue in rendered execution")

    return ItemBankAudit(
        errors=tuple(errors),
        warnings=tuple(warnings),
        pair_count=len(items),
        family_counts=dict(family_counts),
        payload_count=len(payload_ids),
        slot_count=len(slot_ids),
        recomputed_answer_count=recomputed,
        rendered_surface_count=rendered,
        active_schedule_digest_count=len(active_digests),
        zero_dose_schedule_digest_count=len(zero_digests),
    )
