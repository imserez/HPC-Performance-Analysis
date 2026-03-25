import os
import re
import pandas as pd

def extract_and_transform(target_app, base_dir, csv_out_dir):
    """
    Parses PIN tool logs and NPB standard output to generate a consolidated CSV.
    """
    master_data = {}

    # Define the output CSV path
    csv_path = os.path.join(csv_out_dir, f"{target_app}_parsed_results_full.csv")

    # --- A) Parse NPB Log ---
    log_path = os.path.join(base_dir, "normal_results", f"NPB-{target_app.upper()}.log")
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            content = f.read()
        pattern_log = r"Class\s*=\s*([SWA-Z]).*?Time in seconds\s*=\s*([\d\.]+).*?Total threads\s*=\s*(\d+).*?Mop/s total\s*=\s*([\d\.]+).*?Mop/s/thread\s*=\s*([\d\.]+)"
        for match in re.finditer(pattern_log, content, re.DOTALL):
            cls = f"{target_app}.{match.group(1)}"
            threads = int(match.group(3))
            master_data[(cls, threads)] = {
                'Benchmark': cls, 'Threads': threads, 'Time_s': float(match.group(2)),
                'Mops_Total': float(match.group(4)), 'Mops_Thread': float(match.group(5))
            }

    # --- B) Parse DCACHE Results ---
    dcache_dir = os.path.join(base_dir, "dcache_results")
    if os.path.exists(dcache_dir):
        for filename in os.listdir(dcache_dir):
            if filename.endswith(".out"):
                match_name = re.search(rf"{target_app}\.([SWA-Z])_t(\d+)", filename)
                if match_name:
                    cls, threads = f"{target_app}.{match_name.group(1)}", int(match_name.group(2))
                    if (cls, threads) not in master_data:
                        master_data[(cls, threads)] = {'Benchmark': cls, 'Threads': threads}

                    with open(os.path.join(dcache_dir, filename), 'r') as f:
                        content = f.read()
                        def extract(metric, text):
                            m = re.search(rf"{metric}:\s+(\d+)\s+([\d\.]+)%", text)
                            return (int(m.group(1)), float(m.group(2))) if m else (None, None)

                        metrics = ["Load-Hits", "Load-Misses", "Load-Accesses", "Store-Hits", "Store-Misses", "Store-Accesses", "Total-Hits", "Total-Misses", "Total-Accesses"]
                        for m in metrics:
                            val, rate = extract(m, content)
                            master_data[(cls, threads)][m.lower()] = val
                            master_data[(cls, threads)][f"{m.lower()}_rate"] = rate

    # --- C) Parse INSCOUNT Results ---
    inscount_dir = os.path.join(base_dir, "inscount_results")
    if os.path.exists(inscount_dir):
        for filename in os.listdir(inscount_dir):
            if filename.endswith(".out"):
                match_name = re.search(rf"{target_app}\.([SWA-Z])_t(\d+)", filename)
                if match_name:
                    cls, threads = f"{target_app}.{match_name.group(1)}", int(match_name.group(2))
                    if (cls, threads) not in master_data:
                        master_data[(cls, threads)] = {'Benchmark': cls, 'Threads': threads}

                    with open(os.path.join(inscount_dir, filename), 'r') as f:
                        counts = re.findall(r"Count\[\d+\]=\s+(\d+)", f.read())
                        if counts:
                            master_data[(cls, threads)]['Total_Instructions'] = sum(int(c) for c in counts)

    # 1. Create the DataFrame (THIS MUST HAPPEN BEFORE SAVING)
    df_results = pd.DataFrame(list(master_data.values()))

    if df_results.empty:
        print(f"Warning: No valid data extracted for {target_app.upper()}")
        return df_results

    # 2. Filter and sort columns
    expected_columns = [
        'Benchmark', 'Threads', 'Load-hits', 'load-hits_rate', 'load-misses', 'load-misses_rate',
        'load-accesses', 'load-accesses_rate', 'Store-hits', 'store-hits_rate', 'store-misses',
        'store-misses_rate', 'store-accesses', 'store-accesses_rate', 'total-hits', 'total-hits_rate',
        'total-misses', 'total-misses_rate', 'total-accesses', 'total-accesses_rate',
        'Time_s', 'Mops_Total', 'Mops_Thread', 'Total_Instructions'
    ]
    existing_columns = [col for col in expected_columns if col in df_results.columns]
    df_results = df_results[existing_columns].sort_values(by=['Benchmark', 'Threads']).reset_index(drop=True)

    # --- 3. DATA SINK: ENSURE DIRECTORY EXISTS AND SAVE ---
    if not os.path.exists(csv_out_dir):
        os.makedirs(csv_out_dir, exist_ok=True)
        print(f"[*] Created missing output directory: {csv_out_dir}")

    df_results.to_csv(csv_path, index=False)
    print(f"[*] CSV Generated: {csv_path}")

    return df_results

def parse_ryzen_logs(ryzen_base_dir, ryzen_csv_dir):
    """
    Parses Ryzen perf logs and generates a clean CSV validation dataset.
    """
    master_data = []
    if not os.path.exists(ryzen_base_dir):
        return pd.DataFrame()

    for filename in os.listdir(ryzen_base_dir):
        if filename.endswith(".log"):
            filepath = os.path.join(ryzen_base_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()

            blocks = re.split(r'TEST CON \d+ HILOS', content)
            for block in blocks:
                m_class = re.search(r'Class\s*=\s*([SWA-Z])', block)
                m_threads = re.search(r'Total threads\s*=\s*(\d+)', block)
                m_time = re.search(r'Time in seconds\s*=\s*([\d\.]+)', block)
                m_mops = re.search(r'Mop/s total\s*=\s*([\d\.]+)', block)
                m_l1 = re.search(r'L1-dcache-load-misses\s*#\s*([\d\.]+)%', block)
                m_l3 = re.search(r'cache-misses\s*#\s*([\d\.]+)%', block)

                if m_class and m_threads and m_time:
                    master_data.append({
                        'class': m_class.group(1),
                        'threads': int(m_threads.group(1)),
                        'time': float(m_time.group(1)),
                        'mops': float(m_mops.group(1)) if m_mops else 0.0,
                        'percent_l1_Misses': float(m_l1.group(1)) if m_l1 else 0.0,
                        'percent_L3_Miss-Rate': float(m_l3.group(1)) if m_l3 else 0.0
                    })

    if not master_data:
        return pd.DataFrame()

    os.makedirs(ryzen_csv_dir, exist_ok=True)
    df = pd.DataFrame(master_data).sort_values(by=['class', 'threads']).reset_index(drop=True)
    csv_path = os.path.join(ryzen_csv_dir, "ryzen_data.csv")
    df.to_csv(csv_path, index=False)

    return df