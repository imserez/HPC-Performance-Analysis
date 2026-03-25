import argparse
import os
import sys
from style_config import apply_global_styles, get_project_paths
from etl import extract_and_transform
from visualizations import plot_triple_axis, plot_2x2_grid, plot_amat, plot_memory_saturation, plot_speedup, plot_ipc_efficiency, plot_parallel_efficiency, plot_throughput_vs_time, plot_cpu_vs_memory_bound


import pandas as pd

def main():
    # --- 1. CLI ARGUMENTS ---
    parser = argparse.ArgumentParser(description='NPB Performance Analyzer')
    parser.add_argument('--app', type=str, required=True, help='Target benchmark app')
    # NUEVO FLAG:
    parser.add_argument('--plots-only', action='store_true', help='Skip ETL and only regenerate plots')
    args = parser.parse_args()
    TARGET_APP = args.app.lower()

    # --- 2. WORKLOAD PARAMETERS & PATHS ---
    PATHS = get_project_paths(TARGET_APP)
    BASE_DIR, CSV_OUT_DIR, PLOT_DIR = PATHS['base'], PATHS['csv'], PATHS['plots_xeon']
    csv_path = os.path.join(CSV_OUT_DIR, f"{TARGET_APP}_parsed_results_full.csv")

    # --- 3. ORCHESTRATION ---
    STYLE = apply_global_styles(TARGET_APP)

    if not args.plots_only and os.path.exists(csv_path):
        print(f"[!] CSV already exists at {csv_path}. Skipping ETL to save time.")
        print(f"[*] Loading existing data...")
        df_results = pd.read_csv(csv_path)
    elif args.plots_only:
        if os.path.exists(csv_path):
            print(f"[+] Loading existing CSV: {csv_path}")
            df_results = pd.read_csv(csv_path)
        else:
            print(f"[-] Error: CSV not found. Run full pipeline first.")
            sys.exit(1)
    else:
        # Solo entra aquí si NO existe el CSV y NO es plots-only
        print(f"[*] Running full ETL for {TARGET_APP.upper()}...")
        df_results = extract_and_transform(TARGET_APP, BASE_DIR, CSV_OUT_DIR)

    if not df_results.empty:
        # --- THE FIX: Ensure the plot directory exists before calling any visualization ---
        if not os.path.exists(PLOT_DIR):
            os.makedirs(PLOT_DIR, exist_ok=True)
            print(f"[*] Created plot directory: {PLOT_DIR}")

        print(f"[*] Generating all visualizations in {PLOT_DIR}...")
        plot_triple_axis(df_results, TARGET_APP, STYLE, PLOT_DIR, interactive=False)
        plot_2x2_grid(df_results, TARGET_APP, STYLE, PLOT_DIR, interactive=False)
        plot_amat(df_results, TARGET_APP, STYLE, PLOT_DIR, interactive=False)
        plot_speedup(df_results, TARGET_APP, STYLE, PLOT_DIR, interactive=False)
        plot_memory_saturation(df_results, TARGET_APP, STYLE, PLOT_DIR, interactive=False)
        plot_ipc_efficiency(df_results, TARGET_APP, STYLE, PLOT_DIR, interactive=False)
        plot_parallel_efficiency(df_results, TARGET_APP, STYLE, PLOT_DIR, interactive=False)
        plot_throughput_vs_time(df_results, TARGET_APP, STYLE, PLOT_DIR, interactive=False)
        plot_cpu_vs_memory_bound(df_results, TARGET_APP, STYLE, PLOT_DIR, interactive=False)


    print("=> Pipeline finished. ✅")

if __name__ == "__main__":
    main()