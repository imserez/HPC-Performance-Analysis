import os
import matplotlib.pyplot as plt

# ==========================================
# GLOBAL CONFIGURATION PANEL
# ==========================================
RAW_DATA_FOLDER = 'xeon_results'
CSV_DATA_FOLDER = 'xeon_csv'
PLOTS_FOLDER = 'plots'
RYZEN_RAW_FOLDER = 'ryzen_results/perf_results'
RYZEN_CSV_FOLDER = 'ryzen_csv'

CLASS_COLORS = {'S': 'tab:blue', 'W': 'tab:orange', 'A': 'tab:green', 'B': 'tab:red'}
CLASS_MARKERS = {'S': 'o', 'W': 's', 'A': '^', 'B': 'D'}
CLASS_AMAT_HATCHES = {'S': '///', 'W': '...', 'A': 'xxx', 'B': '|||'}

THREAD_COUNTS = [1, 2, 4, 8, 12, 16] # Ampliado para Ryzen
THREAD_HATCHES = {1: '///', 2: '...', 4: 'xxx', 8: '---', 12: '\\\\\\', 16: '+++'}

HATCH_LINEWIDTH = 1.5
HATCH_COLOR = 'black'

# ==========================================
# LOGIC & DICTIONARY GENERATION
# ==========================================
def get_project_paths(target_app):
    target = target_app.lower()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    paths = {
        'base': os.path.join(project_root, 'data', RAW_DATA_FOLDER, target),
        'csv': os.path.join(project_root, 'data', CSV_DATA_FOLDER, target),
        # DESDOBLAMOS LOS PLOTS:
        'plots_xeon': os.path.join(project_root, PLOTS_FOLDER, 'xeon', target),
        'plots_comp': os.path.join(project_root, PLOTS_FOLDER, 'comparison', target),

        'ryzen_base': os.path.join(project_root, 'data', 'ryzen_results/perf_results', target),
        'ryzen_csv': os.path.join(project_root, 'data', 'ryzen_csv', target)
    }
    return paths

def apply_global_styles(target_app):
    target = target_app.lower()
    style = {
        'threads': THREAD_COUNTS,
        'benchmarks': [f'{target}.{c}' for c in CLASS_COLORS.keys()],
        'colors': {f'{target}.{c}': color for c, color in CLASS_COLORS.items()},
        'markers': {f'{target}.{c}': marker for c, marker in CLASS_MARKERS.items()},
        'amat_hatches': {f'{target}.{c}': hatch for c, hatch in CLASS_AMAT_HATCHES.items()},
        'hatches': THREAD_HATCHES,
        'hatch_linewidth': HATCH_LINEWIDTH,
        'hatch_color': HATCH_COLOR
    }
    plt.rcParams['hatch.linewidth'] = style['hatch_linewidth']
    plt.rcParams['hatch.color'] = style['hatch_color']
    return style