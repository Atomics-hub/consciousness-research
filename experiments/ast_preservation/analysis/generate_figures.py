#!/usr/bin/env python3
"""Generate all figures for Paper 2."""

import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path

matplotlib.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ast_preservation.config import Config

RESULTS_DIR = Path(__file__).parent.parent / "results"
FIGURES_DIR = Path(__file__).parent.parent.parent.parent / "paper2" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def load_json(name):
    with open(RESULTS_DIR / name) as f:
        return json.load(f)


def fig1_architecture():
    """Architecture diagram showing three modules and data flow."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.set_aspect('equal')
    ax.axis('off')

    boxes = {
        'Observation': (0.5, 3, 1.8, 1.2, '#e8e8e8'),
        'Attention\nMechanism': (3, 4.5, 2, 1.2, '#a8d8ea'),
        'Attention\nSchema': (3, 2.5, 2, 1.2, '#ffb347'),
        'Self-Model': (6.5, 2.5, 1.8, 1.2, '#98d4a6'),
        'DQN Head': (6.5, 4.5, 1.8, 1.2, '#d4a6d4'),
        'Action': (9, 3, 1, 1.2, '#e8e8e8'),
    }

    for label, (x, y, w, h, color) in boxes.items():
        rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor='black', linewidth=1.5, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=10, fontweight='bold', zorder=3)

    arrows = [
        ((2.3, 3.6), (3, 5.1), 'obs'),
        ((5, 5.1), (6.5, 5.1), 'attended\nfeatures'),
        ((4, 4.5), (4, 3.7), 'attn\nweights'),
        ((3, 3.1), (3, 4.5), 'modulation', True),  # feedback arrow
        ((5, 3.1), (6.5, 3.1), 'schema\nstate'),
        ((7.4, 3.7), (7.4, 4.5), 'identity'),
        ((8.3, 5.1), (9, 3.6), 'Q-values'),
    ]

    for arrow in arrows:
        if len(arrow) == 4:
            (x1, y1), (x2, y2), label, feedback = *arrow[:3], arrow[3]
        else:
            (x1, y1), (x2, y2), label = arrow[:3]
            feedback = False

        style = 'fancy,head_width=6,head_length=4'
        color = '#cc4444' if feedback else '#333333'
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my + 0.2, label, ha='center', va='bottom', fontsize=7, color=color)

    # Ablation markers
    for label_text, (cx, cy) in [("Ablate schema", (4, 2.2)), ("Ablate attention", (4, 5.9)),
                                  ("Ablate self-model", (7.4, 2.2))]:
        ax.text(cx, cy, label_text, ha='center', fontsize=8, color='red', style='italic')

    ax.set_title("Agent Architecture with Separable Components", pad=15)
    fig.savefig(FIGURES_DIR / "fig1_architecture.png")
    fig.savefig(FIGURES_DIR / "fig1_architecture.pdf")
    plt.close()
    print("  fig1_architecture saved")


def fig2_protocol():
    """Experimental protocol and transplant conditions."""
    fig, ax = plt.subplots(1, 1, figsize=(11, 5.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')

    def box(x, y, w, h, text, color, fontsize=9):
        rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor='#222222',
                             linewidth=1.2, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', zorder=3)

    def arrow(x1, y1, x2, y2, label=None):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#333333', lw=1.4))
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.15, label,
                    ha='center', va='bottom', fontsize=7, color='#333333')

    box(0.3, 3.6, 2.2, 1.1, "Train source\nSubstrate A", '#a8d8ea')
    box(3.0, 4.3, 2.2, 1.0, "Ablation\ncontrols", '#f7d794')
    box(3.0, 2.7, 2.2, 1.0, "Extract schema\n+ self-model", '#98d4a6')
    box(5.8, 2.7, 2.2, 1.0, "Insert into\nSubstrate B", '#d4a6d4')
    box(8.6, 2.7, 2.6, 1.0, "Freeze copied state;\nfine-tune interface", '#f5b7b1')

    arrow(2.5, 4.15, 3.0, 4.8, "Phase 2")
    arrow(2.5, 4.15, 3.0, 3.2, "Phase 3")
    arrow(5.2, 3.2, 5.8, 3.2)
    arrow(8.0, 3.2, 8.6, 3.2)

    control_y = 0.8
    box(0.6, control_y, 2.2, 0.8, "Random B\ntrainable", '#eeeeee', fontsize=8)
    box(3.4, control_y, 2.2, 0.8, "Full B\nretrain", '#eeeeee', fontsize=8)
    box(6.2, control_y, 2.5, 0.8, "A-body\ncopied state", '#eeeeee', fontsize=8)
    box(9.3, control_y, 2.2, 0.8, "A→B\ntransplant", '#eeeeee', fontsize=8)
    ax.text(6.0, 2.0, "Transplant-condition comparisons", ha='center',
            va='center', fontsize=9, color='#444444')

    for x in [1.7, 4.5, 7.45, 10.4]:
        arrow(x, 1.6, x, 2.5)

    ax.set_title("Experimental Protocol and Transplant Controls", pad=12)
    fig.savefig(FIGURES_DIR / "fig2_protocol.png")
    fig.savefig(FIGURES_DIR / "fig2_protocol.pdf")
    plt.close()
    print("  fig2_protocol saved")


def fig3_training_curves():
    """Training reward curves."""
    try:
        data = load_json("training_curve.json")
    except FileNotFoundError:
        print("  fig3: training_curve.json not found, skipping")
        return

    rewards = data["episode_rewards"]
    window = 50
    smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
    cfg = Config()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(smoothed, color='#2c3e50', linewidth=1)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Episode Reward")
    ax.set_title("Training Curve: Full Agent, 50-Episode Moving Average")
    ax.axvline(
        x=len(rewards) * cfg.curriculum_phase1_steps / data["total_steps"],
        color='gray',
        linestyle='--',
        alpha=0.5,
        label='Phase 2 start',
    )
    ax.axvline(
        x=len(rewards) * cfg.curriculum_phase2_steps / data["total_steps"],
        color='gray',
        linestyle=':',
        alpha=0.5,
        label='Phase 3 start',
    )
    ax.legend()
    fig.savefig(FIGURES_DIR / "fig3_training_curves.png")
    fig.savefig(FIGURES_DIR / "fig3_training_curves.pdf")
    plt.close()
    print("  fig3_training_curves saved")


def fig4_ablation_results():
    """Per-metric ablation plots with separate y-axes."""
    try:
        data = load_json("ablation_results.json")
    except FileNotFoundError:
        print("  fig4: ablation_results.json not found, skipping")
        return

    conditions = list(data.keys())
    metrics = [
        ("mean_reward", "Reward"),
        ("mean_goals_found", "Goals Found"),
        ("distractor_suppression_rate", "Distractor Suppression"),
        ("mean_self_report_corr", "Self-Report Correlation"),
        ("mean_other_report_corr", "ToM Correlation"),
    ]
    colors = ['#2c3e50', '#e74c3c', '#f39c12', '#27ae60']
    label_map = {
        "full": "Full",
        "schema_ablated": "Schema",
        "attention_ablated": "Attention",
        "self_model_ablated": "Self-model",
    }
    labels = [label_map.get(cond, cond.replace('_', ' ').title()) for cond in conditions]

    fig, axes = plt.subplots(2, 3, figsize=(11, 7))
    axes_flat = axes.ravel()
    for ax, (metric, title) in zip(axes_flat, metrics):
        vals = [data[cond][metric] for cond in conditions]
        ax.bar(range(len(conditions)), vals, color=colors[:len(conditions)], alpha=0.85)
        ax.set_title(title, fontsize=10)
        ax.set_xticks(range(len(conditions)))
        ax.set_xticklabels(labels, rotation=20, ha='right', fontsize=8)
        ax.grid(axis='y', alpha=0.15)

        if metric == "mean_reward":
            lo = min(vals) - 1.0
            hi = max(vals) + 1.0
            ax.set_ylim(lo, hi)
        elif metric == "mean_goals_found":
            ax.set_ylim(0, max(0.05, max(vals) + 0.02))
        elif metric == "mean_other_report_corr":
            lo = min(-0.002, min(vals) - 0.002)
            hi = max(0.012, max(vals) + 0.002)
            ax.set_ylim(lo, hi)
            ax.text(0.5, 0.92, "probe failed", transform=ax.transAxes,
                    ha='center', va='top', fontsize=8, color='#666666')
        else:
            lo = min(0.0, min(vals) - 0.05)
            hi = max(1.0, max(vals) + 0.05)
            ax.set_ylim(lo, hi)

    axes_flat[-1].axis('off')
    fig.suptitle("Ablation Results", y=0.98)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig4_ablation_results.png")
    fig.savefig(FIGURES_DIR / "fig4_ablation_results.pdf")
    plt.close()
    print("  fig4_ablation_results saved")


def fig5_transplant_results():
    """Transplant condition comparison with separate metric axes."""
    try:
        data = load_json("transplant_results.json")
    except FileNotFoundError:
        print("  fig5: transplant_results.json not found, skipping")
        return

    conditions = list(data.keys())
    identity_metric = "identity_probe_accuracy" if "identity_probe_accuracy" in data[conditions[0]] else "memory_retention"
    metrics = [
        ("mean_reward", "Reward"),
        ("mean_self_report_corr", "Self-Report"),
        ("mean_other_report_corr", "ToM"),
        (identity_metric, "Fingerprint Probes" if identity_metric == "identity_probe_accuracy" else "Memory Retention"),
    ]
    colors = ['#2c3e50', '#e74c3c', '#3498db', '#27ae60']
    label_map = {
        "transplant": "A->B",
        "random_control": "Random",
        "arch_matched": "A->A'",
        "full_retrain": "B retrain",
    }
    labels = [label_map.get(cond, cond.replace('_', ' ').title()) for cond in conditions]

    fig, axes = plt.subplots(2, 2, figsize=(9, 6.8))
    for ax, (metric, title) in zip(axes.ravel(), metrics):
        vals = [data[cond].get(metric, 0) for cond in conditions]
        ax.bar(range(len(conditions)), vals, color=colors[:len(conditions)], alpha=0.85)
        ax.set_title(title, fontsize=10)
        ax.set_xticks(range(len(conditions)))
        ax.set_xticklabels(labels, rotation=20, ha='right', fontsize=8)
        ax.grid(axis='y', alpha=0.15)

        if metric == "mean_reward":
            lo = min(vals) - 1.0
            hi = max(vals) + 1.0
            ax.set_ylim(lo, hi)
        elif metric == "mean_other_report_corr":
            lo = min(-0.006, min(vals) - 0.002)
            hi = max(0.016, max(vals) + 0.002)
            ax.set_ylim(lo, hi)
            ax.text(0.5, 0.92, "probe failed", transform=ax.transAxes,
                    ha='center', va='top', fontsize=8, color='#666666')
        else:
            lo = min(-0.1, min(vals) - 0.05)
            hi = max(1.0, max(vals) + 0.05)
            ax.set_ylim(lo, hi)

    fig.suptitle("Transplant Results: Exploratory Transfer Assay", y=0.98)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig5_transplant_results.png")
    fig.savefig(FIGURES_DIR / "fig5_transplant_results.pdf")
    plt.close()
    print("  fig5_transplant_results saved")


def fig6_phi_contrast():
    """Phi-star vs exploratory behavioral proxy scatter."""
    try:
        iit_data = load_json("iit_contrast.json")
        ablation_data = load_json("ablation_results.json")
    except FileNotFoundError:
        print("  fig6: result files not found, skipping")
        return

    fig, ax = plt.subplots(figsize=(7, 5))

    for name in ["full", "schema_ablated"]:
        phi = iit_data[name]["phi"]
        abl = ablation_data.get(name, ablation_data.get("full"))
        self_report = abl["mean_self_report_corr"]

        color = '#2c3e50' if name == "full" else '#e74c3c'
        marker = 'o' if name == "full" else 's'
        ax.scatter(phi, self_report, c=color, s=150, marker=marker, zorder=5,
                   label=name.replace('_', ' ').title())
        if name == "full":
            label = "Full"
            offset = (18, -18)
            va = 'top'
        else:
            label = "Schema\nAblated"
            offset = (18, 12)
            va = 'bottom'
        ax.annotate(
            label,
            (phi, self_report),
            textcoords="offset points",
            xytext=offset,
            ha='left',
            va=va,
            fontsize=9,
            arrowprops=dict(arrowstyle='-', lw=0.8, color=color, alpha=0.7),
        )

    full_phi = iit_data["full"]["phi"]
    schema_phi = iit_data["schema_ablated"]["phi"]
    full_cov = iit_data["full"]["details"].get("state_coverage", 0.0)
    schema_cov = iit_data["schema_ablated"]["details"].get("state_coverage", 0.0)
    ax.set_xlabel(f"Φ* approximation (full {full_phi:.3f}, schema ablated {schema_phi:.3f})")
    ax.set_ylabel("Self-report correlation")
    ax.set_title("Exploratory Φ* Side Analysis")
    ax.legend()
    ax.grid(alpha=0.15)
    ax.margins(x=0.2, y=0.18)
    ax.text(0.03, 0.04,
            f"State coverage: full {full_cov:.1%}, schema ablated {schema_cov:.1%}",
            transform=ax.transAxes, fontsize=8, color='#555555')

    fig.savefig(FIGURES_DIR / "fig6_phi_contrast.png")
    fig.savefig(FIGURES_DIR / "fig6_phi_contrast.pdf")
    plt.close()
    print("  fig6_phi_contrast saved")


def fig7_butlin_heatmap():
    """Butlin-Chalmers indicator heatmap across conditions."""
    try:
        data = load_json("butlin_indicators.json")
    except FileNotFoundError:
        print("  fig7: butlin_indicators.json not found, skipping")
        return

    conditions = list(data.keys())
    indicators = list(data[conditions[0]].keys())

    matrix = np.array([[data[c][ind] for ind in indicators] for c in conditions])

    fig, ax = plt.subplots(figsize=(10, 4.8))
    cmap = matplotlib.colors.ListedColormap(['#d73027', '#fee08b', '#1a9850'])
    norm = matplotlib.colors.BoundaryNorm([-0.01, 0.25, 0.75, 1.01], cmap.N)
    ax.imshow(matrix, cmap=cmap, norm=norm, aspect='auto')

    ax.set_xticks(range(len(indicators)))
    ax.set_xticklabels([i.replace('_', ' ') for i in indicators], fontsize=8, rotation=35, ha='right')
    ax.set_yticks(range(len(conditions)))
    ax.set_yticklabels([c.replace('_', ' ').title() for c in conditions])

    for i in range(len(conditions)):
        for j in range(len(indicators)):
            val = matrix[i, j]
            color = 'white' if val < 0.3 or val > 0.7 else 'black'
            ax.text(j, i, f"{val:.1f}", ha='center', va='center', fontsize=9, color=color)

    legend_items = [
        matplotlib.patches.Patch(facecolor='#d73027', edgecolor='none', label='0 absent'),
        matplotlib.patches.Patch(facecolor='#fee08b', edgecolor='none', label='0.5 partial'),
        matplotlib.patches.Patch(facecolor='#1a9850', edgecolor='none', label='1 present'),
    ]
    ax.legend(handles=legend_items, loc='upper center', bbox_to_anchor=(0.5, -0.24),
              ncol=3, frameon=False, fontsize=8)
    ax.set_title("Exploratory Butlin et al. Indicator Heuristics")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig7_butlin_heatmap.png")
    fig.savefig(FIGURES_DIR / "fig7_butlin_heatmap.pdf")
    plt.close()
    print("  fig7_butlin_heatmap saved")


def fig8_transplant_tradeoff():
    """Self-report vs copied-state fingerprint tradeoff in transplant conditions."""
    try:
        data = load_json("transplant_results.json")
    except FileNotFoundError:
        print("  fig8: transplant_results.json not found, skipping")
        return

    label_map = {
        "transplant": "A→B transplant",
        "random_control": "Random control",
        "arch_matched": "A-body copied state",
        "full_retrain": "B full retrain",
    }
    colors = {
        "transplant": '#2c3e50',
        "random_control": '#e74c3c',
        "arch_matched": '#3498db',
        "full_retrain": '#27ae60',
    }
    markers = {
        "transplant": 'o',
        "random_control": 's',
        "arch_matched": '^',
        "full_retrain": 'D',
    }
    offsets = {
        "transplant": (12, -12),
        "random_control": (-10, 12),
        "arch_matched": (10, -18),
        "full_retrain": (12, 10),
    }

    fig, ax = plt.subplots(figsize=(7, 5))
    for name, values in data.items():
        x = values["mean_self_report_corr"]
        y = values["identity_probe_accuracy"]
        ax.scatter(x, y, s=140, color=colors.get(name, '#555555'),
                   marker=markers.get(name, 'o'), zorder=4)
        ox, oy = offsets.get(name, (10, 10))
        ax.annotate(
            label_map.get(name, name.replace('_', ' ').title()),
            (x, y),
            textcoords="offset points",
            xytext=(ox, oy),
            ha='right' if ox < 0 else 'left',
            va='bottom' if oy > 0 else 'top',
            fontsize=8,
            arrowprops=dict(arrowstyle='-', lw=0.7, color=colors.get(name, '#555555'), alpha=0.7),
        )

    ax.set_xlim(-0.12, 0.62)
    ax.set_ylim(-0.12, 1.12)
    ax.set_xlabel("Self-report correlation")
    ax.set_ylabel("Self-model fingerprint accuracy")
    ax.set_title("Transfer Tradeoff: Self-Report vs Copied State")
    ax.grid(alpha=0.2)
    fig.savefig(FIGURES_DIR / "fig8_transplant_tradeoff.png")
    fig.savefig(FIGURES_DIR / "fig8_transplant_tradeoff.pdf")
    plt.close()
    print("  fig8_transplant_tradeoff saved")


def main():
    print("Generating Paper 2 figures...")
    print(f"  Results dir: {RESULTS_DIR}")
    print(f"  Figures dir: {FIGURES_DIR}")

    fig1_architecture()
    fig2_protocol()
    fig3_training_curves()
    fig4_ablation_results()
    fig5_transplant_results()
    fig6_phi_contrast()
    fig7_butlin_heatmap()
    fig8_transplant_tradeoff()

    print("\nDone. Figures saved to", FIGURES_DIR)


if __name__ == "__main__":
    main()
