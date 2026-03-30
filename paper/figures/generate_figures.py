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


# ============================================================
# FIGURE 6: Theory Decision Tree
# ============================================================
def figure6():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')

    box_style = dict(boxstyle='round,pad=0.4', linewidth=1.2)
    question_style = dict(fontsize=10, ha='center', va='center', fontweight='bold',
                          bbox=dict(facecolor='#f0f0f0', edgecolor='#555555', **box_style))
    theory_fontsize = 9.5

    def draw_theory_box(ax, x, y, text, color, width=1.6, height=0.55):
        rect = mpatches.FancyBboxPatch((x - width/2, y - height/2), width, height,
                                        boxstyle='round,pad=0.15', facecolor=color,
                                        edgecolor='#333333', linewidth=1.0, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', fontsize=theory_fontsize,
                fontweight='bold', color='white')

    def draw_arrow(ax, x1, y1, x2, y2, label='', label_side='left'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#555555', lw=1.5,
                                    connectionstyle='arc3,rad=0'))
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            offset = (-0.35, 0) if label_side == 'left' else (0.35, 0)
            ax.text(mx + offset[0], my + offset[1], label, fontsize=9, ha='center',
                    va='center', color='#444444', fontstyle='italic')

    # Root question
    ax.text(7, 8.2, 'Is consciousness\nsubstrate-independent?', **question_style)

    # YES branch (left)
    draw_arrow(ax, 5.5, 7.85, 3.5, 7.15, 'Yes', 'left')
    ax.text(3.5, 6.85, 'Is functional organization\nsufficient?', **question_style)

    draw_arrow(ax, 2.2, 6.5, 1.5, 5.85, 'Yes', 'left')
    draw_theory_box(ax, 1.5, 5.4, 'GNWT', SUBSTRATE_INDEP)
    draw_theory_box(ax, 3.3, 5.4, 'HOT', SUBSTRATE_INDEP)
    draw_theory_box(ax, 5.1, 5.4, 'AST', SUBSTRATE_INDEP)
    draw_theory_box(ax, 6.9, 5.4, 'RPT', SUBSTRATE_INDEP)
    draw_arrow(ax, 3.5, 6.5, 3.3, 5.85, '', 'left')
    draw_arrow(ax, 4.8, 6.5, 5.1, 5.85, '', 'right')
    draw_arrow(ax, 4.8, 6.5, 6.9, 5.85, '', 'right')

    # NO branch (right)
    draw_arrow(ax, 8.5, 7.85, 10.5, 7.15, 'No', 'right')
    ax.text(10.5, 6.85, 'Does it require biological\ncomputation?', **question_style)

    draw_arrow(ax, 10.5, 6.5, 10.5, 5.85, 'Yes', 'left')
    draw_theory_box(ax, 10.5, 5.4, 'Bio. Comp.', SUBSTRATE_DEP, width=1.8)

    draw_arrow(ax, 11.8, 6.5, 12.5, 5.85, 'No', 'right')
    ax.text(12.5, 5.55, 'Does it require specific\ncausal architecture?', **question_style)

    draw_arrow(ax, 12.5, 5.2, 11.5, 4.5, 'Yes', 'left')
    draw_theory_box(ax, 11.5, 4.0, 'IIT 4.0', SUBSTRATE_DEP)

    draw_arrow(ax, 13.0, 5.2, 13.0, 4.5, 'No', 'right')
    ax.text(13.0, 4.2, 'Does it require\nquantum processes?', **question_style)

    draw_arrow(ax, 13.0, 3.85, 13.0, 3.2, 'Yes', 'left')
    draw_theory_box(ax, 13.0, 2.7, 'Orch OR', SUBSTRATE_DEP)

    # Unclear branch (middle-bottom)
    draw_arrow(ax, 7, 7.85, 7, 4.2, 'Unclear', 'right')
    ax.text(7, 3.9, 'Depends on whether\nembodiment is required', **question_style)
    draw_arrow(ax, 7, 3.55, 7, 2.9, '', 'left')
    draw_theory_box(ax, 7, 2.5, 'Pred. Proc.', SUBSTRATE_UNCLEAR, width=1.8)

    # Legend
    legend_handles = [
        mpatches.Patch(color=SUBSTRATE_INDEP, label='Substrate-independent'),
        mpatches.Patch(color=SUBSTRATE_UNCLEAR, label='Unclear'),
        mpatches.Patch(color=SUBSTRATE_DEP, label='Substrate-dependent'),
    ]
    ax.legend(handles=legend_handles, loc='lower left', fontsize=9, frameon=True,
              facecolor='white', edgecolor='#cccccc', bbox_to_anchor=(0.0, -0.02), ncol=3)

    ax.set_title('Figure 6. Theory Decision Tree: Where Does Each Theory Fall?',
                 fontsize=13, fontweight='bold', pad=15)

    fig.tight_layout()
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig6_theory_decision_tree.png')
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig6_theory_decision_tree.pdf')
    plt.close(fig)
    print("Figure 6 saved.")


# ============================================================
# FIGURE 7: Information Requirements Pyramid
# ============================================================
def figure7():
    fig, ax = plt.subplots(figsize=(12, 8))

    layers = [
        ('Quantum state\n(tubulin superpositions)', 0.22),
        ('Molecular state\n(ion channels, protein conformations)', 0.35),
        ('Dendritic morphology\n(spatial integration properties)', 0.48),
        ('Neuromodulatory state\n(precision weights, receptor densities)', 0.61),
        ('Temporal dynamics\n(firing rates, time constants)', 0.74),
        ('Synaptic weights\n(connection strengths)', 0.87),
        ('Functional connectivity\n(which connects to which)', 1.0),
    ]

    # Theories that require up to each level (index 0=quantum at top, 6=connectivity at bottom)
    theory_max_level = {
        'Orch OR': 0,
        'Bio. Comp.': 1,
        'IIT 4.0': 2,
        'Pred. Proc.': 3,
        'HOT': 4,
        'GNWT': 4,
        'RPT': 4,
        'AST': 5,
    }

    pyramid_bottom = 0.5
    pyramid_top = 7.8
    pyramid_left_base = 1.0
    pyramid_right_base = 11.0
    pyramid_center = 6.0
    layer_height = (pyramid_top - pyramid_bottom) / len(layers)

    grad_colors = ['#9e3333', '#c45b5b', '#c98a3a', '#d4a843', '#6ab880', '#4a9e6e', '#3a8a5c']

    for i, (label, _) in enumerate(layers):
        y_bottom = pyramid_bottom + (len(layers) - 1 - i) * layer_height
        y_top = y_bottom + layer_height
        y_mid = (y_bottom + y_top) / 2

        frac_bottom = (y_bottom - pyramid_bottom) / (pyramid_top - pyramid_bottom)
        frac_top = (y_top - pyramid_bottom) / (pyramid_top - pyramid_bottom)
        x_left_bottom = pyramid_center - (pyramid_center - pyramid_left_base) * (1 - frac_bottom)
        x_right_bottom = pyramid_center + (pyramid_right_base - pyramid_center) * (1 - frac_bottom)
        x_left_top = pyramid_center - (pyramid_center - pyramid_left_base) * (1 - frac_top)
        x_right_top = pyramid_center + (pyramid_right_base - pyramid_center) * (1 - frac_top)

        trapezoid = plt.Polygon([
            (x_left_bottom, y_bottom), (x_right_bottom, y_bottom),
            (x_right_top, y_top), (x_left_top, y_top)
        ], facecolor=grad_colors[i], edgecolor='white', linewidth=2, alpha=0.9)
        ax.add_patch(trapezoid)

        ax.text(pyramid_center, y_mid, label, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color='white')

    # Theory markers on the right side (matching new order: 0=quantum top, 6=connectivity bottom)
    theory_display = [
        ('Orch OR', 0, SUBSTRATE_DEP),
        ('Bio. Comp.', 1, SUBSTRATE_DEP),
        ('IIT 4.0', 2, SUBSTRATE_DEP),
        ('Pred. Proc.', 3, SUBSTRATE_UNCLEAR),
        ('HOT', 4, SUBSTRATE_INDEP),
        ('GNWT', 4, SUBSTRATE_INDEP),
        ('RPT', 4, SUBSTRATE_INDEP),
        ('AST', 5, SUBSTRATE_INDEP),
    ]

    # Group theories by level for label positioning
    from collections import defaultdict
    level_theories = defaultdict(list)
    for name, level, color in theory_display:
        level_theories[level].append((name, color))

    for level, theories_at_level in level_theories.items():
        y_layer_bottom = pyramid_bottom + (len(layers) - 1 - level) * layer_height
        y_mid = y_layer_bottom + layer_height / 2

        frac = (y_mid - pyramid_bottom) / (pyramid_top - pyramid_bottom)
        x_right = pyramid_center + (pyramid_right_base - pyramid_center) * (1 - frac)

        label_text = ', '.join([t[0] for t in theories_at_level])
        theory_color = theories_at_level[0][1]

        ax.annotate(label_text, xy=(x_right + 0.1, y_mid),
                    xytext=(x_right + 1.2, y_mid),
                    fontsize=9, fontweight='bold', color=theory_color, va='center',
                    arrowprops=dict(arrowstyle='->', color=theory_color, lw=1.2))

    # Data volume annotation on the left (top=quantum/impossible, bottom=connectivity/least)
    data_labels = [
        (0, 'Impossible'),
        (1, '~1 ZB'),
        (2, '~100 PB'),
        (3, '~5 PB'),
        (4, '~2 PB'),
        (5, '~2 TB'),
        (6, '~100 GB'),
    ]
    for level, data_text in data_labels:
        y_layer_bottom = pyramid_bottom + (len(layers) - 1 - level) * layer_height
        y_mid = y_layer_bottom + layer_height / 2
        frac = (y_mid - pyramid_bottom) / (pyramid_top - pyramid_bottom)
        x_left = pyramid_center - (pyramid_center - pyramid_left_base) * (1 - frac)

        ax.text(x_left - 0.3, y_mid, data_text, ha='right', va='center',
                fontsize=8.5, color='#555555', fontstyle='italic')

    ax.text(0.3, 4.2, 'Approx. data\nvolume', ha='center', va='center',
            fontsize=9, color='#555555', fontweight='bold', rotation=90)

    # Vertical arrow showing increasing demands (bottom=least, top=most)
    ax.annotate('', xy=(0.7, pyramid_top - 0.3), xytext=(0.7, pyramid_bottom + 0.3),
                arrowprops=dict(arrowstyle='->', color='#888888', lw=1.5))
    ax.text(0.7, pyramid_top + 0.1, 'Most\ndemanding', ha='center', va='bottom',
            fontsize=8, color='#888888')
    ax.text(0.7, pyramid_bottom - 0.1, 'Least\ndemanding', ha='center', va='top',
            fontsize=8, color='#888888')

    ax.set_xlim(-0.5, 14)
    ax.set_ylim(-0.3, 8.8)
    ax.axis('off')
    ax.set_title('Figure 7. Information Requirements Pyramid',
                 fontsize=13, fontweight='bold', pad=15)

    fig.tight_layout()
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig7_information_pyramid.png')
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig7_information_pyramid.pdf')
    plt.close(fig)
    print("Figure 7 saved.")


# ============================================================
# FIGURE 8: Preservation Strategy Landscape
# ============================================================
def figure8():
    fig, ax = plt.subplots(figsize=(10, 7))

    strategies = {
        'Digital\nemulation':         (0.65, 4/8),
        'Gradual silicon\nreplacement': (0.25, 5/8),
        'Biological\npreservation\n(cryonics)': (0.50, 8/8),
        'Gradual\nbio-hybrid':        (0.15, 7/8),
    }

    strategy_colors = {
        'Digital\nemulation':         '#5b8abf',
        'Gradual silicon\nreplacement': '#7b6bbd',
        'Biological\npreservation\n(cryonics)': '#4a9e6e',
        'Gradual\nbio-hybrid':        '#c98a3a',
    }

    compatibility_labels = {
        'Digital\nemulation':         '4/8 theories',
        'Gradual silicon\nreplacement': '5/8 theories',
        'Biological\npreservation\n(cryonics)': '8/8 theories',
        'Gradual\nbio-hybrid':        '7/8 theories',
    }

    for name, (x, y) in strategies.items():
        color = strategy_colors[name]
        ax.scatter(x, y, s=400, c=color, edgecolors='#333333', linewidth=1.2, zorder=5)
        offset_x = 0.06
        offset_y = 0.04
        if 'bio-hybrid' in name:
            offset_x = 0.08
        if 'cryonics' in name:
            offset_y = 0.05
        if 'Digital' in name:
            offset_x = 0.07
        ax.annotate(f'{name}\n({compatibility_labels[name]})',
                    (x + offset_x, y + offset_y), fontsize=10, fontweight='bold',
                    color=color, va='bottom')

    # Mark ideal corner
    ax.scatter(0.95, 0.95, s=300, marker='*', c='gold', edgecolors='#333333',
               linewidth=1.0, zorder=5)
    ax.annotate('Ideal\n(no strategy\nreaches here)', (0.95, 0.95), fontsize=9,
                ha='center', va='bottom', xytext=(0.82, 1.02),
                color='#888888', fontstyle='italic',
                arrowprops=dict(arrowstyle='->', color='#aaaaaa', lw=1.0))

    # Shade the ideal quadrant lightly
    ax.axhspan(0.75, 1.05, xmin=0.7/1.1, xmax=1.0, alpha=0.05, color='green')

    # Quadrant labels
    ax.text(0.9, 0.15, 'Feasible but\nnarrow coverage', fontsize=9, ha='center',
            va='center', color='#aaaaaa', fontstyle='italic')
    ax.text(0.1, 0.9, 'Broad coverage\nbut infeasible', fontsize=9, ha='center',
            va='center', color='#aaaaaa', fontstyle='italic')
    ax.text(0.1, 0.15, 'Neither feasible\nnor compatible', fontsize=9, ha='center',
            va='center', color='#aaaaaa', fontstyle='italic')

    # Dashed lines for quadrants
    ax.axhline(0.5, color='#dddddd', linestyle='--', linewidth=0.8, zorder=0)
    ax.axvline(0.5, color='#dddddd', linestyle='--', linewidth=0.8, zorder=0)

    ax.set_xlabel('Technical Feasibility (current technology)', fontsize=12)
    ax.set_ylabel('Cross-Theory Compatibility', fontsize=12)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(0.0, 1.1)

    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(['Impossible', '', 'Challenging', '', 'Achievable'], fontsize=10)
    ax.set_yticks([0, 1/8, 2/8, 3/8, 4/8, 5/8, 6/8, 7/8, 1.0])
    ax.set_yticklabels(['0/8', '1/8', '2/8', '3/8', '4/8', '5/8', '6/8', '7/8', '8/8'], fontsize=9)

    ax.set_title('Figure 8. The Preservation Strategy Landscape',
                 fontsize=13, fontweight='bold', pad=15)

    fig.tight_layout()
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig8_strategy_landscape.png')
    fig.savefig('/Users/guts/Documents/consciousness-research/paper/figures/fig8_strategy_landscape.pdf')
    plt.close(fig)
    print("Figure 8 saved.")


if __name__ == '__main__':
    figure1()
    figure2()
    figure3()
    figure4()
    figure5()
    figure6()
    figure7()
    figure8()
    print("\nAll figures generated successfully.")
