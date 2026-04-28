from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConditionSpec:
    name: str
    source_agent: str
    target_agent: str
    protocol: str
    copied_payload: tuple[str, ...] = ()
    trainable_parts: tuple[str, ...] = ()
    adaptation_steps: int = 0
    notes: str = ""


@dataclass(frozen=True)
class MetricSpec:
    name: str
    family: str
    primary: bool
    higher_is_better: bool = True
    description: str = ""


@dataclass(frozen=True)
class BenchmarkSpec:
    study_id: str
    master_seed: int
    n_train_seeds: int
    n_eval_episodes: int
    conditions: tuple[ConditionSpec, ...] = field(default_factory=tuple)
    metrics: tuple[MetricSpec, ...] = field(default_factory=tuple)


AST_V0_CONDITIONS = (
    ConditionSpec(
        name="source_full",
        source_agent="ast_a",
        target_agent="ast_a",
        protocol="source_reference",
        notes="Original source agent.",
    ),
    ConditionSpec(
        name="source_attention_ablated",
        source_agent="ast_a",
        target_agent="ast_a",
        protocol="source_ablation",
        copied_payload=("attention",),
    ),
    ConditionSpec(
        name="source_schema_ablated",
        source_agent="ast_a",
        target_agent="ast_a",
        protocol="source_ablation",
        copied_payload=("schema",),
    ),
    ConditionSpec(
        name="source_self_model_ablated",
        source_agent="ast_a",
        target_agent="ast_a",
        protocol="source_ablation",
        copied_payload=("self_model",),
    ),
    ConditionSpec(
        name="a_to_a_copy",
        source_agent="ast_a",
        target_agent="ast_a_prime",
        protocol="architecture_matched_copy",
        copied_payload=("schema", "self_model", "memory"),
    ),
    ConditionSpec(
        name="b_frozen_copy",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="frozen_direct_transfer",
        copied_payload=("schema", "self_model", "memory"),
    ),
    ConditionSpec(
        name="b_adapter_repair_copy",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="adapter_only_repair",
        copied_payload=("schema", "self_model", "memory"),
        trainable_parts=("attention", "adapters", "policy_head"),
        adaptation_steps=10000,
        notes="Copied schema and self-model stay frozen while target interfaces are repaired.",
    ),
    ConditionSpec(
        name="b_source_align_repair_copy",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="source_alignment_repair",
        copied_payload=("schema", "self_model", "memory"),
        trainable_parts=("attention", "adapters", "policy_head"),
        adaptation_steps=10000,
        notes="Copied schema and self-model stay frozen while target interfaces align to source traces.",
    ),
    ConditionSpec(
        name="b_source_align_repair_copy_long",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="source_alignment_repair_long",
        copied_payload=("schema", "self_model", "memory"),
        trainable_parts=("attention", "adapters", "policy_head"),
        adaptation_steps=40000,
        notes="Longer source-alignment repair with matched initialization and finetune seeds.",
    ),
    ConditionSpec(
        name="b_source_align_policy_copy_long",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="source_alignment_policy_copy_long",
        copied_payload=("schema", "self_model", "memory", "policy_head"),
        trainable_parts=("attention", "adapters"),
        adaptation_steps=40000,
        notes="Longer source-alignment repair with copied frozen policy head.",
    ),
    ConditionSpec(
        name="b_source_align_attention_copy_long",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="source_alignment_attention_copy_long",
        copied_payload=("attention", "schema", "self_model", "memory"),
        trainable_parts=("adapters", "policy_head"),
        adaptation_steps=40000,
        notes="Longer source-alignment repair with copied frozen source attention and identity-initialized adapters.",
    ),
    ConditionSpec(
        name="b_source_align_attention_copy_trainable_long",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="source_alignment_attention_copy_trainable_long",
        copied_payload=("attention", "schema", "self_model", "memory"),
        trainable_parts=("attention", "adapters", "policy_head"),
        adaptation_steps=40000,
        notes="Copied source attention starts trainable, with identity-initialized adapters.",
    ),
    ConditionSpec(
        name="b_source_align_attention_adapter_long",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="source_alignment_attention_adapter_long",
        copied_payload=("schema", "self_model", "memory"),
        trainable_parts=("attention", "source_interface_adapter", "policy_head"),
        adaptation_steps=40000,
        notes="Target transformer attention with a residual source-facing interface adapter.",
    ),
    ConditionSpec(
        name="b_source_align_control_adapter_long",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="source_alignment_control_adapter_long",
        copied_payload=("schema", "self_model", "memory"),
        trainable_parts=("attention", "source_interface_adapter", "policy_head"),
        adaptation_steps=40000,
        notes="Source-facing interface adapter with explicit action, TD, and goal-attention control losses.",
    ),
    ConditionSpec(
        name="b_source_align_attention_copy_random_adapter_long",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="source_alignment_attention_copy_random_adapter_long",
        copied_payload=("attention", "schema", "self_model", "memory"),
        trainable_parts=("adapters", "policy_head"),
        adaptation_steps=40000,
        notes="Copied frozen source attention with randomly initialized adapters.",
    ),
    ConditionSpec(
        name="b_source_align_identity_adapter_long",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="source_alignment_identity_adapter_long",
        copied_payload=("schema", "self_model", "memory"),
        trainable_parts=("attention", "adapters", "policy_head"),
        adaptation_steps=40000,
        notes="Target attention with identity-initialized adapters, isolating adapter initialization.",
    ),
    ConditionSpec(
        name="b_trainable_copy",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="copied_trainable_repair",
        copied_payload=("schema", "self_model", "memory"),
        trainable_parts=("adapters", "copied_payload"),
    ),
    ConditionSpec(
        name="b_frozen_random",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="freeze_matched_random",
    ),
    ConditionSpec(
        name="b_trainable_random",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="trainable_random_control",
        trainable_parts=("adapters", "random_payload"),
    ),
    ConditionSpec(
        name="b_behavior_distill",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="behavior_only_distillation",
        trainable_parts=("target_agent",),
    ),
    ConditionSpec(
        name="b_full_retrain",
        source_agent="ast_a",
        target_agent="ast_b",
        protocol="full_retrain",
        trainable_parts=("target_agent",),
    ),
)


AST_V0_METRICS = (
    MetricSpec(
        name="reward",
        family="competence",
        primary=True,
        description="Mean episode return.",
    ),
    MetricSpec(
        name="goals_found",
        family="competence",
        primary=True,
        description="Mean goals found per episode.",
    ),
    MetricSpec(
        name="distractor_capture_rate",
        family="attention",
        primary=True,
        higher_is_better=False,
        description="Distractor captures per step or per episode.",
    ),
    MetricSpec(
        name="goal_attention_mass",
        family="attention_control",
        primary=False,
        description="Mean visible goal mass under the agent's attention map.",
    ),
    MetricSpec(
        name="distractor_attention_mass",
        family="attention_control",
        primary=False,
        higher_is_better=False,
        description="Mean visible distractor mass under the agent's attention map.",
    ),
    MetricSpec(
        name="source_attention_l1",
        family="source_similarity",
        primary=False,
        higher_is_better=False,
        description="Mean L1 distance from source attention on matched observations.",
    ),
    MetricSpec(
        name="source_feature_mse",
        family="source_similarity",
        primary=False,
        higher_is_better=False,
        description="Mean squared distance from source attended features on matched observations.",
    ),
    MetricSpec(
        name="source_action_agreement",
        family="source_similarity",
        primary=False,
        description="Fraction of matched observations where greedy action equals the source action.",
    ),
    MetricSpec(
        name="self_report_corr",
        family="report",
        primary=True,
        description="Correlation between report vector and attention state.",
    ),
    MetricSpec(
        name="identity_probe_accuracy",
        family="identity",
        primary=True,
        description="Source-specific fingerprint probe accuracy.",
    ),
    MetricSpec(
        name="adaptation_steps_to_threshold",
        family="transfer_cost",
        primary=True,
        higher_is_better=False,
        description="Steps needed to recover a preregistered performance level.",
    ),
    MetricSpec(
        name="other_report_corr",
        family="social",
        primary=False,
        description="Partner attention report correlation if source validation passes.",
    ),
    MetricSpec(
        name="memory_overlap",
        family="identity",
        primary=False,
        description="Diagnostic hash overlap with source memory store.",
    ),
)


AST_V0_SPEC = BenchmarkSpec(
    study_id="preservation_bench_ast_v0",
    master_seed=20260424,
    n_train_seeds=20,
    n_eval_episodes=200,
    conditions=AST_V0_CONDITIONS,
    metrics=AST_V0_METRICS,
)
