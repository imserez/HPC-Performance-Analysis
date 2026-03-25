import os
import argparse
import pandas as pd
from style_config import get_project_paths
from etl import parse_ryzen_logs
from visualizations import plot_architecture_comparison, plot_speedup_comparison, plot_throughput_comparison, plot_amat_vs_performance, plot_perf_per_core, plot_efficiency_comparison

def clean_numeric(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '', regex=False).str.replace('%', '', regex=False)
    return df.apply(pd.to_numeric, errors='ignore')

def main():
    parser = argparse.ArgumentParser(description='Optional Architecture Comparison Module')
    parser.add_argument('--app', type=str, required=True, help='Target benchmark app (e.g., cg)')
    args = parser.parse_args()
    TARGET_APP = args.app.lower()

    PATHS = get_project_paths(TARGET_APP)
    xeon_csv_path = os.path.join(PATHS['csv'], f"{TARGET_APP}_parsed_results_full.csv")

    print("========================================")
    print("=> Running Validation Dataset ETL (Ryzen perf)...")

    df_ryzen_raw = parse_ryzen_logs(PATHS['ryzen_base'], PATHS['ryzen_csv'])
    if df_ryzen_raw.empty:
        print(f"[-] Missing or invalid Ryzen validation data in: {PATHS['ryzen_base']}")
        print("[-] Skipping comparison gracefully.")
        return


    if not os.path.exists(xeon_csv_path):
        print(f"[-] Missing Xeon data: {xeon_csv_path}")
        print("[-] Please run 'make all' first. Exiting module gracefully.")
        return

    print("[+] Datasets parsed successfully. Generating architectural comparison...")

    df_xeon = clean_numeric(pd.read_csv(xeon_csv_path))
    df_ryzen = clean_numeric(df_ryzen_raw)

    os.makedirs(PATHS['plots_comp'], exist_ok=True)

    plot_architecture_comparison(df_ryzen, df_xeon, TARGET_APP, PATHS['plots_comp'], target_class='A')
    plot_speedup_comparison(df_ryzen, df_xeon, TARGET_APP, PATHS['plots_comp'], target_class='A')
    plot_throughput_comparison(df_ryzen, df_xeon, TARGET_APP, PATHS['plots_comp'], target_class='A')
    plot_amat_vs_performance(df_ryzen, df_xeon, TARGET_APP, PATHS['plots_comp'], target_class='A')
    plot_perf_per_core(df_ryzen, df_xeon, TARGET_APP, PATHS['plots_comp'], target_class='A')
    plot_efficiency_comparison(df_ryzen, df_xeon, TARGET_APP, PATHS['plots_comp'], target_class='A')

    print("=> Architecture comparison completed. ✅")

if __name__ == "__main__":
    main()