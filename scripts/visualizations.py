import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import EngFormatter, ScalarFormatter
from matplotlib.patches import Patch
from matplotlib.lines import Line2D


# =========================================================
# Title helpers
# =========================================================

def extract_class_from_benchmark(benchmark):
    if isinstance(benchmark, str) and '.' in benchmark:
        return benchmark.split('.')[-1]
    return 'Unknown'

def detect_class_from_df(df):
    if 'Benchmark' in df.columns:
        classes = df['Benchmark'].astype(str).str.split('.').str[-1].unique()
        return classes[0] if len(classes) == 1 else "Mixed"
    return "Unknown"


def plot_triple_axis(df, target_app, style, plot_dir, interactive=False):
    problems = style['benchmarks']

    class_label = detect_class_from_df(df)
    available_threads = df['Threads'].unique()
    threads_interest = [t for t in style['threads'] if t in available_threads]
    width = 0.18

    fig, ax1 = plt.subplots(figsize=(15, 8))
    ax2, ax3 = ax1.twinx(), ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))

    for i, prob in enumerate(problems):
        subset = df[(df['Benchmark'] == prob) & (df['Threads'].isin(threads_interest))].sort_values('Threads')
        t_pos, t_vals, i_vals = [], [], []

        for j, t_count in enumerate(threads_interest):
            row = subset[subset['Threads'] == t_count]
            if not row.empty:
                pos = i + (j - 1.5) * width
                t_pos.append(pos)
                ax1.bar(pos, row['Mops_Total'].values[0], width=width, color=style['colors'][prob], hatch=style['hatches'][t_count], edgecolor='black', alpha=0.6)
                t_vals.append(row['Time_s'].values[0])
                if 'Total_Instructions' in row: i_vals.append(row['Total_Instructions'].values[0])

        if t_vals: ax2.plot(t_pos, t_vals, marker=style['markers'][prob], color='black', linewidth=1.5, markersize=7)
        if i_vals: ax3.plot(t_pos, i_vals, marker='x', linestyle=':', color='black', linewidth=1.2, markersize=6, alpha=0.9)

    ax1.set_ylabel('Throughput (Mop/s)', fontweight='bold')
    ax2.set_ylabel('Execution Time (s) [LOG]', fontweight='bold')
    ax3.set_ylabel('Total Instructions [LOG]', fontweight='bold')
    ax2.set_yscale('log'); ax3.set_yscale('log')
    ax1.set_xticks(np.arange(len(problems))); ax1.set_xticklabels(problems, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.3)

    plt.suptitle(
        f'{target_app.upper()} - Class {class_label}\n'
        f'Performance Overview (Throughput / Time / Instructions)',
        fontsize=16,
        fontweight='bold'
    )
    out_file = os.path.join(plot_dir, f'{target_app}_triple_axis_performance.png')
    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches='tight')

    if interactive: plt.show()
    else: plt.close()
    print(f"[*] Chart Generated: {out_file}")

def plot_2x2_grid(df, target_app, style, plot_dir, interactive=False):
    problems = style['benchmarks']
    # FILTRO DINÁMICO
    available_threads = df['Threads'].unique()
    threads_interest = [t for t in style['threads'] if t in available_threads]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    width = 0.6

    for idx, prob in enumerate(problems):
        ax1 = axes[idx]
        ax2 = ax1.twinx()
        subset = df[(df['Benchmark'] == prob) & (df['Threads'].isin(threads_interest))].sort_values('Threads')
        x_pos, time_vals = np.arange(len(threads_interest)), []

        for i, t_count in enumerate(threads_interest):
            row = subset[subset['Threads'] == t_count]
            if not row.empty:
                inst_val = row['Total_Instructions'].values[0] if 'Total_Instructions' in row else 0
                ax1.bar(i, inst_val, color=style['colors'][prob], hatch=style['hatches'][t_count], edgecolor='black', width=width, alpha=0.7)
                time_vals.append(row['Time_s'].values[0])
            else: time_vals.append(None)

        ax1.set_title(f'Benchmark Class: {prob.upper()}', fontsize=16, fontweight='bold', pad=15)
        ax1.set_ylabel('Total Instructions Executed', fontweight='bold')
        ax1.yaxis.set_major_formatter(EngFormatter(unit='i'))
        ax2.plot(x_pos, time_vals, color='black', marker=style['markers'][prob], linewidth=2.5, markersize=8)
        ax2.set_ylabel('Execution Time (seconds)', fontweight='bold', color='black')
        ax2.yaxis.set_major_formatter(ScalarFormatter())
        ax2.ticklabel_format(style='plain', axis='y')

        valid_times = [t for t in time_vals if t is not None]
        if valid_times: ax2.set_ylim(0, max(valid_times) * 1.2)
        ax1.set_xticks(x_pos); ax1.set_xticklabels([f'{t}T' for t in threads_interest], fontweight='bold')
        ax1.grid(axis='y', linestyle='--', alpha=0.3)

    legend_elements = [Patch(facecolor='lightgray', hatch=style['hatches'][t], label=f'{t} Threads') for t in threads_interest]
    legend_elements.append(Line2D([0], [0], color='black', marker='o', label='Execution Time (s)'))
    fig.legend(handles=legend_elements, loc='lower center', ncol=5, bbox_to_anchor=(0.5, 0.02))
    plt.suptitle(f'NPB-{target_app.upper()}: Instruction Overhead vs Execution Time', fontsize=20, fontweight='bold', y=0.98)

    out_file = os.path.join(plot_dir, f'{target_app}_instructions_vs_time.png')
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig(out_file, dpi=300)

    if interactive: plt.show()
    else: plt.close()
    print(f"[*] Chart Generated: {out_file}")

def plot_amat(df, target_app, style, plot_dir, interactive=False):
    if 'load-misses_rate' not in df.columns:
        print("Warning: AMAT data not available in dataframe.")
        return

    df = df.copy()
    df['AMAT'] = 4 + (df['load-misses_rate'] / 100 * 200)
    fig, ax = plt.subplots(figsize=(12, 7))

    # FILTRO DINÁMICO
    available_threads = df['Threads'].unique()
    threads_interest = [t for t in style['threads'] if t in available_threads]

    x_amat, width = np.arange(len(threads_interest)), 0.25
    valid_bench = [b for b in style['benchmarks'] if b != f'{target_app}.B']

    for i, bench in enumerate(valid_bench):
        subset = df[df['Benchmark'] == bench].set_index('Threads').reindex(threads_interest).reset_index()
        bars = ax.bar(x_amat + (i * width), subset['AMAT'], width=width, label=bench.upper(), color=style['colors'].get(bench, 'white'), hatch=style['amat_hatches'].get(bench, ''), edgecolor='black', alpha=0.6, linewidth=1.5)
        for bar in bars:
            y = bar.get_height()
            if not np.isnan(y): ax.text(bar.get_x() + bar.get_width()/2, y + 1, f'{y:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_ylabel('AMAT (cycles per access)', fontweight='bold')
    ax.set_title(f'AMAT Analysis - {target_app.upper()}\nMemory Wall Evidence', fontweight='bold')
    ax.set_xticks(x_amat + width); ax.set_xticklabels([f'{t} Threads' for t in threads_interest])
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    out_file = os.path.join(plot_dir, f'{target_app}_amat_analysis.png')
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)

    if interactive: plt.show()
    else: plt.close()
    print(f"[*] Chart Generated: {out_file}")






def plot_speedup(df, target_app, style, plot_dir, interactive=False):
    """
    Analyzes Parallel Speedup: T1 / Tn.
    Shows how close the scaling is to the theoretical ideal.
    """
    problems = style['benchmarks']
    available_threads = df['Threads'].unique()
    threads_interest = [t for t in style['threads'] if t in available_threads]

    fig, ax = plt.subplots(figsize=(12, 7))

    # Draw Ideal Speedup Line
    ax.plot(threads_interest, threads_interest, linestyle='--', color='gray', alpha=0.7, label='Ideal (Linear) Speedup')

    for prob in problems:
        subset = df[
            (df['Benchmark'] == prob) &
            (df['Threads'].isin(threads_interest))
        ].sort_values('Threads')
        if subset.empty: continue

        # Calculate Speedup: T(1 thread) / T(n threads)
        t1_row = subset[subset['Threads'] == 1]
        if t1_row.empty: continue

        t1 = t1_row['Time_s'].values[0]
        speedup = t1 / subset['Time_s']

        ax.plot(subset['Threads'], speedup, marker=style['markers'][prob],
                color=style['colors'][prob], linewidth=2, label=f'Speedup {prob.upper()}')

    ax.set_xlabel('Number of Threads', fontweight='bold')
    ax.set_ylabel('Speedup Factor (x)', fontweight='bold')
    ax.set_title(f'NPB-{target_app.upper()}: Scalability & Parallel Efficiency', fontsize=14, fontweight='bold')
    ax.set_xticks(threads_interest)
    ax.set_yticks(np.arange(len(threads_interest) + 1))
    ax.grid(axis='both', linestyle='--', alpha=0.3)
    ax.legend()

    out_file = os.path.join(plot_dir, f'{target_app}_parallel_speedup.png')
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)

    if interactive: plt.show()
    else: plt.close()
    print(f"[*] Speedup Chart Generated: {out_file}")

def plot_memory_saturation(df, target_app, style, plot_dir, interactive=False):
    """
    Generates a 2x2 grid correlating Throughput and Cache Miss Rate for all benchmark classes.
    Proves the "Memory Wall" across different problem sizes.
    """
    if 'load-misses_rate' not in df.columns:
        print("[-] Skipping Saturation Grid: No cache data found.")
        return

    problems = style['benchmarks']
    available_threads = df['Threads'].unique()
    threads_interest = [t for t in style['threads'] if t in available_threads]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for idx, prob in enumerate(problems):
        ax1 = axes[idx]
        ax2 = ax1.twinx()

        # Filter data for this specific problem class
        subset = df[
            (df['Benchmark'] == prob) &
            (df['Threads'].isin(threads_interest))
        ].sort_values('Threads')

        if subset.empty or subset['load-misses_rate'].isnull().all():
            ax1.text(0.5, 0.5, f"No cache data for {prob.upper()}",
                     ha='center', va='center', fontsize=12, color='gray')
            ax1.set_title(f"Class: {prob.upper()}", fontweight='bold')
            continue

        x_labels = [f"{t}T" for t in subset['Threads']]

        # --- PRIMARY AXIS: Throughput (Bars) ---
        ax1.bar(x_labels, subset['Mops_Total'], color='silver', alpha=0.4, label='Throughput (Mop/s)')

        # --- SECONDARY AXIS: L1 Miss Rate (Line) ---
        ax2.plot(x_labels, subset['load-misses_rate'],
                 marker='x', color='red', linewidth=2.5, markersize=10, label='L1 Miss Rate %')

        # Formatting each subplot
        ax1.set_title(f"Benchmark Class: {prob.upper()}", fontsize=14, fontweight='bold', pad=10)
        ax1.set_ylabel('Total Mop/s', fontweight='bold')
        ax2.set_ylabel('L1 Miss Rate (%)', fontweight='bold', color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        # Set a reasonable limit for miss rate to compare across plots if desired
        # or let it scale automatically to see the trend
        ax1.grid(axis='y', linestyle='--', alpha=0.3)

    # Global Legend
    lines_labels = [axes[0].get_legend_handles_labels(), axes[0].get_legend_handles_labels()] # Proxy
    # Simplified manual legend
    legend_elements = [
        Patch(facecolor='silver', alpha=0.4, label='Throughput (Mop/s)'),
        Line2D([0], [0], color='red', marker='x', linewidth=2.5, label='L1 Cache Miss Rate (%)')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=2, bbox_to_anchor=(0.5, 0.02), fontsize=12)

    plt.suptitle(f'NPB-{target_app.upper()}: Memory Saturation Analysis (Throughput vs. Cache Inefficiency)',
                 fontsize=20, fontweight='bold', y=0.98)

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    out_file = os.path.join(plot_dir, f'{target_app}_memory_saturation_grid.png')
    plt.savefig(out_file, dpi=300)

    if interactive: plt.show()
    else: plt.close()
    print(f"[*] Saturation Grid Generated: {out_file}")



def plot_ipc_efficiency(df, target_app, style, plot_dir, interactive=False):
    """
    Correlation between IPC (Instructions Per Cycle) and L1 Miss Rate.
    Proves that as cache misses increase, the processor efficiency (IPC) drops.
    Requires 'Total_Instructions', 'Time_s' and 'load-misses_rate'.
    Note: IPC calculation here is simplified as (Instructions / Time) normalized
    by a constant frequency (approx 2.4GHz for Xeon E5603).
    """
    if 'load-misses_rate' not in df.columns or 'Total_Instructions' not in df.columns:
        return

    problems = style['benchmarks']
    available_threads = df['Threads'].unique()
    threads_interest = [t for t in style['threads'] if t in available_threads]

    # Assume 2.4 GHz constant for Xeon E5603 to calculate a "Relative IPC"
    FREQ_GHZ = 2.4

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for idx, prob in enumerate(problems):
        ax1 = axes[idx]
        ax2 = ax1.twinx()

        subset = df[
            (df['Benchmark'] == prob) &
            (df['Threads'].isin(threads_interest))
        ].sort_values('Threads')
        if subset.empty: continue

        # Calculate Relative IPC: Instructions / (Time * Frequency)
        # We use instructions per second / frequency to get a proxy of IPC
        ipc_proxy = (subset['Total_Instructions'] / subset['Time_s']) / (FREQ_GHZ * 1e9)

        x_labels = [f"{t}T" for t in subset['Threads']]

        # --- EJE 1: IPC (Línea Azul con Marcador de la clase) ---
        ax1.plot(x_labels, ipc_proxy, marker=style['markers'][prob], color='tab:blue',
                 linewidth=3, markersize=10, label='Relative IPC')

        # --- EJE 2: Miss Rate (Área sombreada Roja) ---
        ax2.fill_between(x_labels, subset['load-misses_rate'], color='tab:red', alpha=0.2, label='L1 Miss Rate %')
        ax2.plot(x_labels, subset['load-misses_rate'], color='tab:red', linestyle='--', alpha=0.6)

        ax1.set_title(f"Efficiency Analysis: {prob.upper()}", fontsize=14, fontweight='bold')
        ax1.set_ylabel('Relative IPC (Efficiency)', color='tab:blue', fontweight='bold')
        ax2.set_ylabel('L1 Miss Rate (%)', color='tab:red', fontweight='bold')
        ax1.set_ylim(0, max(ipc_proxy) * 1.3 if not ipc_proxy.empty else 1)
        ax1.grid(axis='y', linestyle=':', alpha=0.5)

    legend_elements = [
        Line2D([0], [0], color='tab:blue', marker='o', linewidth=3, label='IPC (Processor Efficiency)'),
        Patch(facecolor='tab:red', alpha=0.2, label='Cache Misses (Memory Wall Weight)')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=2, bbox_to_anchor=(0.5, 0.02), fontsize=12)

    plt.suptitle(f'NPB-{target_app.upper()}: Processor Efficiency vs. Memory Latency Stalls',
                 fontsize=20, fontweight='bold', y=0.98)

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    out_file = os.path.join(plot_dir, f'{target_app}_ipc_efficiency_grid.png')
    plt.savefig(out_file, dpi=300)

    if interactive: plt.show()
    else: plt.close()
    print(f"[*] IPC Efficiency Grid Generated: {out_file}")

def plot_parallel_efficiency(df, target_app, style, plot_dir, interactive=False):
    """
    Efficiency = Speedup / Threads
    Shows how much useful work each additional core contributes.
    """

    problems = style['benchmarks']
    threads = sorted(df['Threads'].unique())

    fig, ax = plt.subplots(figsize=(10, 6))

    for prob in problems:
        subset = df[df['Benchmark'] == prob].sort_values('Threads')
        t1_row = subset[subset['Threads'] == 1]
        if t1_row.empty:
            continue

        t1 = t1_row['Time_s'].values[0]
        speedup = t1 / subset['Time_s']
        efficiency = speedup / subset['Threads']

        ax.plot(subset['Threads'], efficiency,
                marker=style['markers'][prob],
                label=f'{prob.upper()}',
                linewidth=2)

    ax.axhline(1.0, linestyle='--', color='gray', label='Ideal Efficiency')
    ax.set_xlabel('Threads')
    ax.set_ylabel('Parallel Efficiency')
    ax.set_title(f'{target_app.upper()} - Parallel Efficiency')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend()

    out_file = os.path.join(plot_dir, f'{target_app}_efficiency.png')
    plt.savefig(out_file, dpi=300)
    plt.close()


def plot_throughput_vs_time(df, target_app, style, plot_dir, interactive=False):
    fig, ax = plt.subplots(figsize=(10, 6))

    for prob in style['benchmarks']:
        subset = df[df['Benchmark'] == prob]
        if subset.empty:
            continue

        ax.scatter(subset['Time_s'], subset['Mops_Total'],
                   label=prob.upper(),
                   s=80)

        for _, row in subset.iterrows():
            ax.annotate(f"{int(row['Threads'])}T",
                        (row['Time_s'], row['Mops_Total']),
                        fontsize=8)

    ax.set_xlabel('Execution Time (s)')
    ax.set_ylabel('Throughput (Mop/s)')
    ax.set_title('Throughput vs Execution Time Trade-off')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend()

    out_file = os.path.join(plot_dir, f'{target_app}_throughput_vs_time.png')
    plt.savefig(out_file, dpi=300)
    plt.close()

def plot_cpu_vs_memory_bound(df, target_app, style, plot_dir, interactive=False):
    if 'load-misses_rate' not in df.columns:
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    for prob in style['benchmarks']:
        subset = df[df['Benchmark'] == prob]
        if subset.empty:
            continue

        ax.scatter(subset['load-misses_rate'], subset['Mops_Total'],
                   label=prob.upper(), s=80)

    ax.set_xlabel('L1 Miss Rate (%)')
    ax.set_ylabel('Throughput (Mop/s)')
    ax.set_title('CPU-bound vs Memory-bound Behavior')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend()

    out_file = os.path.join(plot_dir, f'{target_app}_cpu_vs_memory.png')
    plt.savefig(out_file, dpi=300)
    plt.close()
# ARCHITECTURE COMPARISONS:


def plot_architecture_comparison(df_ryzen, df_xeon, target_app, plot_dir, target_class='A'):
    """
    Generates a single comparative chart (Ryzen vs Xeon) for a specific benchmark class.
    """
    HIT_TIME, MISS_PENALTY = 4, 200
    fig, ax1 = plt.subplots(figsize=(15, 8))
    ax2, ax3 = ax1.twinx(), ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))

    # Para la comparativa, nos limitamos al máximo común divisor de ambas arquitecturas (8 hilos)
    threads = [1, 2, 4, 8]
    x = np.arange(len(threads))
    width = 0.25

    r_times, x_times, r_l1_misses, x_l1_misses, r_l3_misses, r_amat, x_amat = [], [], [], [], [], [], []

    for t in threads:
        r_row = df_ryzen[(df_ryzen['class'] == target_class) & (df_ryzen['threads'] == t)]
        if not r_row.empty:
            r_times.append(r_row['time'].iloc[0])
            m_l1_r = r_row['percent_l1_Misses'].iloc[0]
            r_l1_misses.append(m_l1_r)
            r_l3_misses.append(r_row['percent_L3_Miss-Rate'].iloc[0])
            r_amat.append(HIT_TIME + (m_l1_r / 100 * MISS_PENALTY))
        else:
            r_times.append(None); r_l1_misses.append(0); r_l3_misses.append(0); r_amat.append(None)

        x_row = df_xeon[(df_xeon['Benchmark'] == f'{target_app}.{target_class}') & (df_xeon['Threads'] == t)]
        if not x_row.empty:
            x_times.append(x_row['Time_s'].iloc[0])
            m_l1_x = x_row['load-misses_rate'].iloc[0] if 'load-misses_rate' in x_row else 0
            x_l1_misses.append(m_l1_x)
            x_amat.append(HIT_TIME + (m_l1_x / 100 * MISS_PENALTY))
        else:
            x_times.append(None); x_l1_misses.append(0); x_amat.append(None)

    b1 = ax1.bar(x - width, r_l1_misses, width, label='Ryzen: L1 Miss %', hatch='///', color='#CCE5FF', edgecolor='black', alpha=0.4)
    b2 = ax1.bar(x, x_l1_misses, width, label='Xeon: L1 Miss %', hatch='...', color='#FFEBCC', edgecolor='black', alpha=0.4)
    b3 = ax1.bar(x + width, r_l3_misses, width, label='Ryzen: L3 Miss %', hatch='xxx', color='#D5F5E3', edgecolor='black', alpha=0.4)

    for rects in [b1, b2, b3]:
        for rect in rects:
            if (h := rect.get_height()) > 0:
                ax1.annotate(f'{h:.1f}%', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                            textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')

    l1 = ax2.plot(x, r_times, marker='o', markersize=9, color='#d62728', linewidth=2.5, label='Ryzen: Time (s)')
    l2 = ax2.plot(x, x_times, marker='s', markersize=9, color='#1f77b4', linewidth=2.5, label='Xeon: Time (s)')
    l3 = ax3.plot(x, r_amat, marker='D', markersize=8, linestyle=':', color='#8b0000', linewidth=2, label='Ryzen: AMAT (cycles)')
    l4 = ax3.plot(x, x_amat, marker='X', markersize=8, linestyle='--', color='#00008b', linewidth=2, label='Xeon: AMAT (cycles)')

    ax1.set_xlabel('Number of Threads', fontweight='bold')
    ax1.set_ylabel('Cache Miss Rate (%)', fontweight='bold')
    ax2.set_ylabel('Execution Time (seconds)', fontweight='bold', color='#d62728')
    ax3.set_ylabel('AMAT (cycles per access)', fontweight='bold', color='#00008b')

    plt.title(f'Architecture Comparison - Class {target_class}\nRyzen (Modern) vs Xeon (Legacy)', fontsize=14, fontweight='bold', pad=30)
    ax1.set_xticks(x); ax1.set_xticklabels([f'{t}T' for t in threads])
    ax1.grid(axis='y', linestyle='--', alpha=0.3)

    handles = [b1, b2, b3] + l1 + l2 + l3 + l4
    ax1.legend(handles, [h.get_label() for h in handles], loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=True, shadow=True)

    out_file = os.path.join(plot_dir, f'{target_app}_architectural_comparison_Class_{target_class}.png')
    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[*] Comparison Chart Generated: {out_file}")

def plot_speedup_comparison(df_ryzen, df_xeon, target_app, plot_dir, target_class='A'):
    """
    Compares the scaling efficiency (Speedup) between Ryzen and Xeon architectures.
    Shows how close each CPU gets to the theoretical ideal linear scaling.
    """
    threads = [1, 2, 4, 8]
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot Ideal Scaling line (1:1 ratio)
    ax.plot(threads, threads, linestyle='--', color='gray', label='Ideal (Linear) Scaling', alpha=0.5)

    # Process both architectures
    for df, label, color, marker in [(df_ryzen, 'Ryzen', '#d62728', 'o'), (df_xeon, 'Xeon', '#1f77b4', 's')]:
        if label == 'Xeon':
            # Xeon uses 'Benchmark' column with app.class format
            subset = df[df['Benchmark'] == f'{target_app}.{target_class}'].sort_values('Threads')
            t1_data = subset[subset['Threads'] == 1]
            if not t1_data.empty:
                t1 = t1_data['Time_s'].iloc[0]
                # Calculate Speedup: T(1 thread) / T(n threads)
                speedup = [t1 / t for t in subset[subset['Threads'].isin(threads)]['Time_s']]
                ax.plot(threads, speedup, marker=marker, markersize=8, color=color, linewidth=2, label=f'{label} Speedup')
        else:
            # Ryzen uses 'class' and 'threads' columns
            subset = df[df['class'] == target_class].sort_values('threads')
            t1_data = subset[subset['threads'] == 1]
            if not t1_data.empty:
                t1 = t1_data['time'].iloc[0]
                speedup = [t1 / t for t in subset[subset['threads'].isin(threads)]['time']]
                ax.plot(threads, speedup, marker=marker, markersize=8, color=color, linewidth=2, label=f'{label} Speedup')

    ax.set_xlabel('Number of Threads', fontweight='bold')
    ax.set_ylabel('Speedup Factor (x)', fontweight='bold')
    ax.set_title(f'Scaling Efficiency Comparison - Class {target_class}\nRyzen vs Xeon', fontsize=12, fontweight='bold')
    ax.set_xticks(threads)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend()

    out_file = os.path.join(plot_dir, f'{target_app}_speedup_comparison_{target_class}.png')
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[*] Speedup Comparison Generated: {out_file}")

def plot_throughput_comparison(df_ryzen, df_xeon, target_app, plot_dir, target_class='A'):
    """
    Compares the absolute Workload Throughput (Mop/s) between architectures.
    Highlights the generational gap in execution performance.
    """
    threads = [1, 2, 4, 8]
    fig, ax = plt.subplots(figsize=(10, 6))

    r_mops, x_mops = [], []

    for t in threads:
        # Extract Ryzen Mop/s (assuming 'mops' column exists in your Ryzen CSV)
        r_row = df_ryzen[(df_ryzen['class'] == target_class) & (df_ryzen['threads'] == t)]
        # Extract Xeon Mop/s
        x_row = df_xeon[(df_xeon['Benchmark'] == f'{target_app}.{target_class}') & (df_xeon['Threads'] == t)]

        r_mops.append(r_row['mops'].iloc[0] if not r_row.empty and 'mops' in r_row else 0)
        x_mops.append(x_row['Mops_Total'].iloc[0] if not x_row.empty else 0)

    width = 0.35
    x_pos = np.arange(len(threads))

    ax.bar(x_pos - width/2, r_mops, width, label='Ryzen (Zen 3)', color='#d62728', alpha=0.7, edgecolor='black')
    ax.bar(x_pos + width/2, x_mops, width, label='Xeon (Westmere)', color='#1f77b4', alpha=0.7, edgecolor='black')

    ax.set_ylabel('Total Throughput (Mop/s)', fontweight='bold')
    ax.set_xlabel('Number of Threads', fontweight='bold')
    ax.set_title(f'Absolute Performance Comparison - Class {target_class}\nWorkload: {target_app.upper()}', fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'{t}T' for t in threads])
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # Add value labels on top of bars
    for i, m in enumerate(r_mops):
        if m > 0: ax.text(i - width/2, m, f'{m:.0f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    for i, m in enumerate(x_mops):
        if m > 0: ax.text(i + width/2, m, f'{m:.0f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    out_file = os.path.join(plot_dir, f'{target_app}_throughput_comparison_{target_class}.png')
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[*] Throughput Comparison Generated: {out_file}")

def plot_efficiency_comparison(df_ryzen, df_xeon, target_app, plot_dir, target_class='A'):
    threads = [1, 2, 4, 8]
    fig, ax = plt.subplots(figsize=(10, 6))

    for df, label, color in [
        (df_ryzen, 'Ryzen', 'red'),
        (df_xeon, 'Xeon', 'blue')
    ]:
        if label == 'Xeon':
            subset = df[df['Benchmark'] == f'{target_app}.{target_class}']
            t1 = subset[subset['Threads'] == 1]['Time_s'].values[0]
            times = subset[subset['Threads'].isin(threads)]['Time_s']
        else:
            subset = df[df['class'] == target_class]
            t1 = subset[subset['threads'] == 1]['time'].values[0]
            times = subset[subset['threads'].isin(threads)]['time']

        speedup = t1 / times
        efficiency = speedup / np.array(threads)

        ax.plot(threads, efficiency, marker='o', label=label, linewidth=2)

    ax.axhline(1.0, linestyle='--', color='gray')
    ax.set_title('Parallel Efficiency Comparison')
    ax.set_xlabel('Threads')
    ax.set_ylabel('Efficiency')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend()

    out_file = os.path.join(plot_dir, f'{target_app}_efficiency_comparison.png')
    plt.savefig(out_file, dpi=300)
    plt.close()


def plot_perf_per_core(df_ryzen, df_xeon, target_app, plot_dir, target_class='A'):
    threads = [1, 2, 4, 8]
    fig, ax = plt.subplots(figsize=(10, 6))

    for df, label in [(df_ryzen, 'Ryzen'), (df_xeon, 'Xeon')]:
        perf_per_core = []

        for t in threads:
            if label == 'Xeon':
                row = df[(df['Benchmark'] == f'{target_app}.{target_class}') & (df['Threads'] == t)]
                mops = row['Mops_Total'].iloc[0] if not row.empty else 0
            else:
                row = df[(df['class'] == target_class) & (df['threads'] == t)]
                mops = row['mops'].iloc[0] if not row.empty else 0

            perf_per_core.append(mops / t if t > 0 else 0)

        ax.plot(threads, perf_per_core, marker='o', label=label)

    ax.set_title('Performance per Core')
    ax.set_xlabel('Threads')
    ax.set_ylabel('Mop/s per Core')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend()

    out_file = os.path.join(plot_dir, f'{target_app}_perf_per_core.png')
    plt.savefig(out_file, dpi=300)
    plt.close()

def plot_amat_vs_performance(df_ryzen, df_xeon, target_app, plot_dir, target_class='A'):
    fig, ax = plt.subplots(figsize=(10, 6))

    HIT, MISS = 4, 200

    for df, label in [(df_ryzen, 'Ryzen'), (df_xeon, 'Xeon')]:
        amat_vals, perf_vals = [], []

        if label == 'Xeon':
            subset = df[df['Benchmark'] == f'{target_app}.{target_class}']
            for _, row in subset.iterrows():
                amat = HIT + (row['load-misses_rate']/100 * MISS)
                amat_vals.append(amat)
                perf_vals.append(row['Mops_Total'])
        else:
            subset = df[df['class'] == target_class]
            for _, row in subset.iterrows():
                amat = HIT + (row['percent_l1_Misses']/100 * MISS)
                amat_vals.append(amat)
                perf_vals.append(row['mops'])

        ax.scatter(amat_vals, perf_vals, label=label, s=80)

    ax.set_xlabel('AMAT (cycles)')
    ax.set_ylabel('Throughput (Mop/s)')
    ax.set_title('Memory Latency vs Performance')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend()

    out_file = os.path.join(plot_dir, f'{target_app}_amat_vs_perf.png')
    plt.savefig(out_file, dpi=300)
    plt.close()