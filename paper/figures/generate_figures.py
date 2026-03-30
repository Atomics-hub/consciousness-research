import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 12,
    'axes.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})

SUBSTRATE_INDEP = '#4a9e6e'
SUBSTRATE_DEP = '#c45b5b'
SUBSTRATE_UNCLEAR = '#d4a843'

THEORY_COLORS = {
    'AST': SUBSTRATE_INDEP,
    'HOT': SUBSTRATE_INDEP,
    'GNWT': SUBSTRATE_INDEP,
    'RPT': SUBSTRATE_INDEP,
    'Pred. Proc.': SUBSTRATE_UNCLEAR,
    'IIT 4.0': SUBSTRATE_DEP,
    'Bio. Comp.': SUBSTRATE_DEP,
    'Orch OR': SUBSTRATE_DEP,
}

THEORIES_ORDERED = ['AST', 'HOT', 'GNWT', 'RPT', 'Pred. Proc.', 'IIT 4.0', 'Bio. Comp.', 'Orch OR']
VERDICTS = {'AST': 5, 'HOT': 5, 'GNWT': 4, 'RPT': 4, 'Pred. Proc.': 3, 'IIT 4.0': 1, 'Bio. Comp.': 1, 'Orch OR': 0}


# ============================================================
# FIGURE 1: The Substrate Independence Fault Line
# ============================================================
def figure1():
    fig, ax = plt.subplots(figsize=(10, 5))

    colors = [THEORY_COLORS[t] for t in THEORIES_ORDERED]
    scores = [VERDICTS[t] for t in THEORIES_ORDERED]
    x = np.arange(len(THEORIES_ORDERED))

    bars = ax.bar(x, scores, color=colors, width=0.65, edgecolor='white', linewidth=0.5)

    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.12,
                str(score), ha='center', va='bottom', fontsize=13, fontweight='bold')

    # Dividing lines between groups
    ax.axvline(3.5, color='#888888', linestyle='--', linewidth=0.8, alpha=0.6)
    ax.axvline(4.5, color='#888888', linestyle='--', linewidth=0.8, alpha=0.6)

    # Group labels
    ax.text(1.5, 5.7, 'Substrate-Independent', ha='center', fontsize=11, fontstyle='italic', color=SUBSTRATE_INDEP)
    ax.text(4.0, 5.7, 'Unclear', ha='center', fontsize=11, fontstyle='italic', color=SUBSTRATE_UNCLEAR)
    ax.text(6.0, 5.7, 'Substrate-Dependent', ha='center', fontsize=11, fontstyle='italic', color=SUBSTRATE_DEP)

    ax.set_xticks(x)
    ax.set_xticklabels(THEORIES_ORDERED, fontsize=11, rotation=25, ha='right')
    ax.set_ylabel('Preservation Favorability (0\u20135)', fontsize=12)
    ax.set_ylim(0, 6.2)
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.set_title('Figure 1. The Substrate Independence Fault Line', fontsize=13, fontweight='bold', pad=15)

    legend_handles = [
        mpatches.Patch(color=SUBSTRATE_INDEP, label='Substrate-independent (4 theories)'),
        mpatches.Patch(color=SUBSTRATE_UNCLEAR, label='Unclear (1 theory)'),
        mpatches.Patch(color=SUBSTRATE_DEP, label='Substrate-dependent (3 theories)'),
    ]
    ax.legend(handles=legend_handles, loc='upper center', fontsize=9, frameon=False,
              bbox_to_anchor=(0.5, -0.18), ncol=3)

    fig.tight_layout()
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig1_substrate_fault_line.png')
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig1_substrate_fault_line.pdf')
    plt.close(fig)
    print("Figure 1 saved.")


# ============================================================
# FIGURE 2: Engineering Requirements Span
# ============================================================
def figure2():
    fig, axes = plt.subplots(1, 3, figsize=(16, 7), sharey=False)

    theories = ['AST', 'HOT', 'GNWT', 'RPT', 'Pred.\nProc.', 'IIT 4.0', 'Bio.\nComp.', 'Orch OR']
    colors = [THEORY_COLORS[t] for t in THEORIES_ORDERED]
    y_pos = np.arange(len(theories))

    # Panel A: Data Size (bytes)
    # AST: 1-10 TB, HOT: 500 TB, GNWT: 2 PB, RPT: 2 PB, PP: 5 PB, IIT: 100 EB, Bio: 10-100 PB, Orch: inf
    data_low =  [1e12,  5e14,  2e15,  2e15,  5e15,  1e20,  1e16,  None]
    data_high = [1e13,  5e14,  2e15,  2e15,  5e15,  1e20,  1e17,  None]

    ax = axes[0]
    for i in range(len(theories)):
        if data_low[i] is not None:
            ax.barh(i, np.log10(data_high[i]) - np.log10(data_low[i]) if data_high[i] != data_low[i] else 0.3,
                    left=np.log10(data_low[i]) if data_high[i] != data_low[i] else np.log10(data_low[i]) - 0.15,
                    color=colors[i], height=0.6, edgecolor='white', linewidth=0.5)
        else:
            ax.annotate('Physically\nimpossible', xy=(23, i), fontsize=10, ha='center', va='center',
                       color=SUBSTRATE_DEP, fontweight='bold', fontstyle='italic')

    # Current capability line: ~EB scale
    ax.axvline(np.log10(1e18), color='#333333', linestyle=':', linewidth=1.2, alpha=0.7)
    ax.text(np.log10(1e18) + 0.3, 7.4, 'Current storage\nfrontier (~1 EB)', fontsize=9, va='top', color='#333333')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(theories, fontsize=10)
    ax.set_xlabel('Data Size (log$_{10}$ bytes)', fontsize=11)
    ax.set_xlim(11, 25)
    ax.set_title('A. Data Requirements', fontsize=12, fontweight='bold')
    ax.invert_yaxis()

    # Panel B: Compute (FLOPS)
    # AST: 1e15-1e18, HOT: 1e17-1e20, GNWT: 1e18-1e22, RPT: 1e18-1e20, PP: 1e18-1e21, IIT sim: 1e22 (verif: uncomputable), Bio: 1e25, Orch: uncomputable
    compute_low =  [1e15,  1e17,  1e18,  1e18,  1e18,  1e22,  1e25,  None]
    compute_high = [1e18,  1e20,  1e22,  1e20,  1e21,  1e22,  1e25,  None]

    ax = axes[1]
    for i in range(len(theories)):
        if compute_low[i] is not None:
            low_log = np.log10(compute_low[i])
            high_log = np.log10(compute_high[i])
            width = max(high_log - low_log, 0.3)
            left = low_log if high_log != low_log else low_log - 0.15
            ax.barh(i, width, left=left, color=colors[i], height=0.6, edgecolor='white', linewidth=0.5)
        else:
            ax.annotate('Uncomputable', xy=(27, i), fontsize=10, ha='center', va='center',
                       color=SUBSTRATE_DEP, fontweight='bold', fontstyle='italic')

    # Current exascale
    ax.axvline(np.log10(2e18), color='#333333', linestyle=':', linewidth=1.2, alpha=0.7)
    ax.text(np.log10(2e18) + 0.3, 7.4, 'Current exascale\n(~2$\\times$10$^{18}$)', fontsize=9, va='top', color='#333333')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(['' for _ in theories])
    ax.set_xlabel('Compute (log$_{10}$ FLOPS)', fontsize=11)
    ax.set_xlim(14, 30)
    ax.set_title('B. Compute Requirements', fontsize=12, fontweight='bold')
    ax.invert_yaxis()

    # Panel C: Feasibility Timeline
    timeline_start = [2040, 2055, 2060, 2060, 2060, 2100, 2080, None]
    timeline_end =   [2060, 2075, 2080, 2080, 2080, 2150, 2110, None]

    ax = axes[2]
    for i in range(len(theories)):
        if timeline_start[i] is not None:
            ax.barh(i, timeline_end[i] - timeline_start[i],
                    left=timeline_start[i], color=colors[i], height=0.6, edgecolor='white', linewidth=0.5)
        else:
            ax.annotate('Never', xy=(2095, i), fontsize=10, ha='center', va='center',
                       color=SUBSTRATE_DEP, fontweight='bold', fontstyle='italic')

    # Current year
    ax.axvline(2026, color='#333333', linestyle=':', linewidth=1.2, alpha=0.7)
    ax.text(2028, 7.4, '2026 (now)', fontsize=9, va='top', color='#333333')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(['' for _ in theories])
    ax.set_xlabel('Year', fontsize=11)
    ax.set_xlim(2020, 2160)
    ax.set_title('C. Feasibility Timeline', fontsize=12, fontweight='bold')
    ax.invert_yaxis()

    fig.suptitle('Figure 2. Engineering Requirements Span Across Theories', fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig2_engineering_requirements.png')
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig2_engineering_requirements.pdf')
    plt.close(fig)
    print("Figure 2 saved.")


# ============================================================
# FIGURE 3: Preservation Strategy Risk Matrix
# ============================================================
def figure3():
    strategies = [
        'Digital emulation',
        'Gradual silicon\nreplacement',
        'Biological preservation\n(cryonics)',
        'Gradual bio-hybrid\nreplacement',
    ]
    theories_short = ['AST', 'HOT', 'GNWT', 'RPT', 'Pred.\nProc.', 'IIT\n4.0', 'Bio.\nComp.', 'Orch\nOR']

    # 0 = fails (red), 0.5 = conditional (yellow), 1 = works (green)
    matrix = np.array([
        # AST  HOT  GNWT RPT  PP   IIT  Bio  Orch
        [1.0, 1.0, 1.0, 1.0, 0.5, 0.0, 0.0, 0.0],  # Digital emulation
        [1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.0, 0.0],  # Gradual silicon
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],  # Biological preservation
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],  # Gradual bio-hybrid
    ])

    cmap = LinearSegmentedColormap.from_list('risk', [SUBSTRATE_DEP, SUBSTRATE_UNCLEAR, SUBSTRATE_INDEP])

    fig, ax = plt.subplots(figsize=(10, 4.5))
    im = ax.imshow(matrix, cmap=cmap, aspect='auto', vmin=0, vmax=1)

    ax.set_xticks(np.arange(8))
    ax.set_xticklabels(theories_short, fontsize=10)
    ax.set_yticks(np.arange(4))
    ax.set_yticklabels(strategies, fontsize=11)
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    labels_map = {0.0: 'Fails', 0.5: 'Conditional', 1.0: 'Works'}
    for i in range(4):
        for j in range(8):
            val = matrix[i, j]
            text_color = 'white' if val < 0.3 else ('black' if val > 0.7 else '#333333')
            ax.text(j, i, labels_map[val], ha='center', va='center', fontsize=9, color=text_color, fontweight='bold')

    # Grid lines
    for i in range(5):
        ax.axhline(i - 0.5, color='white', linewidth=2)
    for j in range(9):
        ax.axvline(j - 0.5, color='white', linewidth=2)

    # Substrate independence dividers
    ax.axvline(3.5, color='#333333', linewidth=2.5, linestyle='-')
    ax.axvline(4.5, color='#333333', linewidth=2.5, linestyle='-')

    legend_handles = [
        mpatches.Patch(color=SUBSTRATE_INDEP, label='Works'),
        mpatches.Patch(color=SUBSTRATE_UNCLEAR, label='Conditional'),
        mpatches.Patch(color=SUBSTRATE_DEP, label='Fails'),
    ]
    ax.legend(handles=legend_handles, loc='lower right', fontsize=9, frameon=True,
              facecolor='white', edgecolor='#cccccc', bbox_to_anchor=(1.0, -0.25), ncol=3)

    ax.set_title('Figure 3. Preservation Strategy Risk Matrix', fontsize=13, fontweight='bold', pad=20)
    fig.tight_layout()
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig3_risk_matrix.png')
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig3_risk_matrix.pdf')
    plt.close(fig)
    print("Figure 3 saved.")


# ============================================================
# FIGURE 4: The Deflation Paradox
# ============================================================
def figure4():
    fig, ax = plt.subplots(figsize=(8, 6))

    # X: How seriously the theory takes phenomenal consciousness (1-10 scale)
    # Y: Preservation favorability (0-5)
    theories_data = {
        'AST':        (1.5, 5),
        'HOT':        (2.5, 5),
        'GNWT':       (4.5, 4),
        'RPT':        (5.0, 4),
        'Pred. Proc.':(5.5, 3),
        'IIT 4.0':    (8.0, 1),
        'Bio. Comp.': (8.5, 1),
        'Orch OR':    (9.5, 0),
    }

    for theory, (x, y) in theories_data.items():
        color = THEORY_COLORS[theory]
        ax.scatter(x, y, s=220, c=color, edgecolors='#333333', linewidth=0.8, zorder=5)
        offset_y = 0.25
        offset_x = 0
        if theory == 'RPT':
            offset_y = -0.35
        if theory == 'Bio. Comp.':
            offset_y = -0.35
        if theory == 'HOT':
            offset_x = 0.3
        ax.annotate(theory, (x + offset_x, y + offset_y), fontsize=10, ha='center', va='bottom')

    # Trend line
    xs = np.array([v[0] for v in theories_data.values()])
    ys = np.array([v[1] for v in theories_data.values()])
    z = np.polyfit(xs, ys, 1)
    p = np.poly1d(z)
    x_line = np.linspace(1, 10, 100)
    ax.plot(x_line, p(x_line), '--', color='#999999', linewidth=1.5, alpha=0.7, zorder=1)

    ax.set_xlabel('Seriousness About Phenomenal Consciousness', fontsize=12)
    ax.set_ylabel('Preservation Favorability (0\u20135)', fontsize=12)
    ax.set_xlim(0.5, 10.5)
    ax.set_ylim(-0.7, 6.5)
    ax.set_yticks([0, 1, 2, 3, 4, 5])

    ax.annotate('', xy=(1.2, 6.0), xytext=(9.8, 6.0),
                arrowprops=dict(arrowstyle='<->', color='#aaaaaa', lw=1.2))
    ax.text(3.0, 6.15, 'Deflates consciousness,\neasy to preserve', fontsize=9, ha='center', color='#666666', va='bottom')
    ax.text(8.0, 6.15, 'Takes consciousness seriously,\nhard/impossible to preserve', fontsize=9, ha='center', color='#666666', va='bottom')

    ax.set_title('Figure 4. The Deflation Paradox', fontsize=13, fontweight='bold', pad=15)
    fig.tight_layout()
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig4_deflation_paradox.png')
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig4_deflation_paradox.pdf')
    plt.close(fig)
    print("Figure 4 saved.")


# ============================================================
# FIGURE 5: Timeline to Feasibility
# ============================================================
def figure5():
    fig, ax = plt.subplots(figsize=(11, 5))

    entries = [
        ('AST', 2040, 2060, SUBSTRATE_INDEP),
        ('HOT', 2055, 2075, SUBSTRATE_INDEP),
        ('GNWT', 2060, 2080, SUBSTRATE_INDEP),
        ('RPT', 2060, 2080, SUBSTRATE_INDEP),
        ('Pred. Proc.', 2060, 2080, SUBSTRATE_UNCLEAR),
        ('Bio. Comp.', 2080, 2110, SUBSTRATE_DEP),
        ('IIT 4.0\n(verification)', 2100, 2160, SUBSTRATE_DEP),
        ('Orch OR', None, None, SUBSTRATE_DEP),
    ]

    y_positions = list(range(len(entries)))
    y_positions.reverse()

    for i, (label, start, end, color) in enumerate(entries):
        y = y_positions[i]
        if start is not None:
            ax.barh(y, end - start, left=start, color=color, height=0.55, edgecolor='white', linewidth=0.5)
            ax.text(start + (end - start) / 2, y, f'{start}\u2013{end}',
                    ha='center', va='center', fontsize=9, fontweight='bold',
                    color='white' if color != SUBSTRATE_UNCLEAR else '#333333')
        else:
            ax.text(2090, y, 'Physically impossible', ha='center', va='center',
                    fontsize=11, color=SUBSTRATE_DEP, fontweight='bold', fontstyle='italic')

    ax.set_yticks(y_positions)
    ax.set_yticklabels([e[0] for e in entries], fontsize=11)

    # Current year marker
    ax.axvline(2026, color='#333333', linewidth=2, linestyle='-', zorder=10)
    ax.text(2026, len(entries) - 0.3, '2026', ha='center', va='bottom', fontsize=11,
            fontweight='bold', color='#333333',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#333333', linewidth=1))

    # Shade the past
    ax.axvspan(2020, 2026, alpha=0.06, color='black')

    ax.set_xlim(2020, 2170)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_title('Figure 5. Estimated Timeline to Preservation Feasibility', fontsize=13, fontweight='bold', pad=15)

    legend_handles = [
        mpatches.Patch(color=SUBSTRATE_INDEP, label='Substrate-independent'),
        mpatches.Patch(color=SUBSTRATE_UNCLEAR, label='Unclear'),
        mpatches.Patch(color=SUBSTRATE_DEP, label='Substrate-dependent'),
    ]
    ax.legend(handles=legend_handles, loc='lower right', fontsize=9, frameon=False)

    fig.tight_layout()
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig5_timeline.png')
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig5_timeline.pdf')
    plt.close(fig)
    print("Figure 5 saved.")


if __name__ == '__main__':
    figure1()
    figure2()
    figure3()
    figure4()
    figure5()
    print("\nAll figures generated successfully.")
