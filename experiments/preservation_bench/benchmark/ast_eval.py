import torch

from .episode_logs import EpisodeLog, StepLog, safe_corr


def run_ast_episode_log(
    agent,
    env,
    cfg,
    study_id: str,
    condition: str,
    training_seed_index: int,
    eval_episode_index: int,
    eval_seed: int,
    source_reference_agent=None,
) -> EpisodeLog:
    env.set_curriculum_phase(3)
    obs = env.reset(seed=eval_seed)
    agent.reset_episode(batch_size=1, device=cfg.device)
    if source_reference_agent is not None and source_reference_agent is not agent:
        source_reference_agent.reset_episode(batch_size=1, device=cfg.device)

    total_reward = 0.0
    goals_found = 0
    distractor_captures = 0
    step_logs: list[StepLog] = []

    while True:
        obs_t = torch.tensor(obs, dtype=torch.float32, device=cfg.device).unsqueeze(0)
        action, out = agent.select_action(obs_t, epsilon=0.0)
        attention = out.attention_weights.squeeze(0).detach().cpu().numpy()

        source_attention_l1 = None
        source_feature_mse = None
        source_action_match = None
        if source_reference_agent is agent:
            source_attention_l1 = 0.0
            source_feature_mse = 0.0
            source_action_match = 1.0
        elif source_reference_agent is not None:
            with torch.no_grad():
                source_out = source_reference_agent(obs_t)
                source_action = source_out.q_values.argmax(dim=-1).item()
                source_attention_l1 = float(
                    torch.mean(
                        torch.abs(out.attention_weights.detach() - source_out.attention_weights)
                    ).item()
                )
                source_feature_mse = float(
                    torch.mean(
                        (out.attended_features.detach() - source_out.attended_features) ** 2
                    ).item()
                )
                source_action_match = 1.0 if int(action.item()) == int(source_action) else 0.0

        result = env.step(action.item(), attention_weights=attention)

        total_reward += float(result.reward)
        if result.info["goal_found"]:
            goals_found += 1

        distractor_capture = any(env.agent_pos == dp for dp in env.distractor_positions)
        if distractor_capture:
            distractor_captures += 1

        self_corr = None
        if result.info["query_self"]:
            predicted = out.schema.self_report.squeeze(0).detach().cpu().numpy()
            self_corr = safe_corr(attention, predicted)

        other_corr = None
        if result.info["query_other"] and result.info["partner_attn"] is not None:
            predicted = out.schema.other_report.squeeze(0).detach().cpu().numpy()
            other_corr = safe_corr(result.info["partner_attn"], predicted)

        step_logs.append(
            StepLog(
                step=int(result.info["step"]),
                action=int(action.item()),
                reward=float(result.reward),
                goal_found=bool(result.info["goal_found"]),
                distractor_capture=bool(distractor_capture),
                query_self=bool(result.info["query_self"]),
                query_other=bool(result.info["query_other"]),
                self_report_corr=self_corr,
                other_report_corr=other_corr,
                goal_attention_mass=float(result.info.get("goal_attention_mass", 0.0)),
                distractor_attention_mass=float(
                    result.info.get("distractor_attention_mass", 0.0)
                ),
                source_attention_l1=source_attention_l1,
                source_feature_mse=source_feature_mse,
                source_action_match=source_action_match,
            )
        )

        obs = result.obs
        if result.done:
            break

    return EpisodeLog(
        study_id=study_id,
        condition=condition,
        training_seed_index=training_seed_index,
        eval_episode_index=eval_episode_index,
        eval_seed=eval_seed,
        total_reward=total_reward,
        goals_found=goals_found,
        steps=len(step_logs),
        distractor_captures=distractor_captures,
        step_logs=step_logs,
    )
