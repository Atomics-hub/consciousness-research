import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path


MAX_NUMPY_SEED = 2**32 - 1


@dataclass(frozen=True)
class SeedRecord:
    study_id: str
    role: str
    condition: str
    training_seed_index: int
    eval_episode_index: int | None
    seed: int
    extra: str = ""


def stable_seed(
    study_id: str,
    master_seed: int,
    role: str,
    condition: str = "",
    training_seed_index: int = 0,
    eval_episode_index: int | None = None,
    extra: str = "",
) -> int:
    parts = (
        study_id,
        str(master_seed),
        role,
        condition,
        str(training_seed_index),
        "" if eval_episode_index is None else str(eval_episode_index),
        extra,
    )
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % MAX_NUMPY_SEED


def build_seed_registry(
    study_id: str,
    master_seed: int,
    conditions: list[str],
    n_train_seeds: int,
    n_eval_episodes: int,
    source_train_seed_override: int | None = None,
    condition_seed_aliases: dict[str, str] | None = None,
) -> list[SeedRecord]:
    records: list[SeedRecord] = []
    aliases = condition_seed_aliases or {}

    for train_idx in range(n_train_seeds):
        source_seed = stable_seed(
            study_id,
            master_seed,
            "source_train_seed",
            "source",
            train_idx,
        )
        if source_train_seed_override is not None and train_idx == 0:
            source_seed = int(source_train_seed_override)

        records.append(
            SeedRecord(
                study_id=study_id,
                role="source_train_seed",
                condition="source",
                training_seed_index=train_idx,
                eval_episode_index=None,
                seed=source_seed,
            )
        )
        records.append(
            SeedRecord(
                study_id=study_id,
                role="identity_probe_seed",
                condition="source",
                training_seed_index=train_idx,
                eval_episode_index=None,
                seed=stable_seed(
                    study_id,
                    master_seed,
                    "identity_probe_seed",
                    "source",
                    train_idx,
                ),
            )
        )

        for condition in conditions:
            seed_condition = aliases.get(condition, condition)
            extra = "" if seed_condition == condition else f"seed_condition={seed_condition}"
            records.append(
                SeedRecord(
                    study_id=study_id,
                    role="target_init_seed",
                    condition=condition,
                    training_seed_index=train_idx,
                    eval_episode_index=None,
                    seed=stable_seed(
                        study_id,
                        master_seed,
                        "target_init_seed",
                        seed_condition,
                        train_idx,
                    ),
                    extra=extra,
                )
            )
            records.append(
                SeedRecord(
                    study_id=study_id,
                    role="finetune_env_seed",
                    condition=condition,
                    training_seed_index=train_idx,
                    eval_episode_index=None,
                    seed=stable_seed(
                        study_id,
                        master_seed,
                        "finetune_env_seed",
                        seed_condition,
                        train_idx,
                    ),
                    extra=extra,
                )
            )

            for eval_idx in range(n_eval_episodes):
                # Evaluation episodes are condition-independent so paired contrasts
                # compare every condition on the same environment sequence.
                records.append(
                    SeedRecord(
                        study_id=study_id,
                        role="eval_episode_seed",
                        condition=condition,
                        training_seed_index=train_idx,
                        eval_episode_index=eval_idx,
                        seed=stable_seed(
                            study_id,
                            master_seed,
                            "eval_episode_seed",
                            "paired_eval",
                            train_idx,
                            eval_idx,
                        ),
                    )
                )

    return records


def write_seed_registry(path: Path, records: list[SeedRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "study_id",
                "role",
                "condition",
                "training_seed_index",
                "eval_episode_index",
                "seed",
                "extra",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "study_id": record.study_id,
                    "role": record.role,
                    "condition": record.condition,
                    "training_seed_index": record.training_seed_index,
                    "eval_episode_index": record.eval_episode_index,
                    "seed": record.seed,
                    "extra": record.extra,
                }
            )
