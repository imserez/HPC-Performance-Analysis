# HPC Performance Analysis Framework

This project provides a complete pipeline for analyzing the performance of HPC workloads, with a focus on the NAS Parallel Benchmarks (NPB). It automates data extraction, transformation, visualization, and optional architectural comparisons across different CPU platforms.

The workflow is designed to be reproducible, extensible, and easy to use through a Makefile-driven interface.

---

## Project Structure

.
├── data/
│ ├── xeon_results/ # Raw benchmark outputs (Intel Xeon)
│ ├── xeon_csv/ # Processed CSV data (generated)
│ ├── ryzen_results/ # Optional local results (AMD Ryzen)
│ └── ryzen_csv/ # Processed Ryzen data
├── plots/ # Generated visualizations
├── scripts/
│ ├── analyze_performance.py
│ ├── compare_architectures.py
│ ├── etl.py
│ ├── visualizations.py
│ └── style_config.py
├── docs/ # Detailed analysis reports
├── notebooks/ # Exploratory analysis (optional)
├── Makefile
└── README.md

---

## Overview

The framework processes raw benchmark outputs and produces:

- Structured CSV datasets
- Performance visualizations (throughput, execution time, scaling, etc.)
- Memory behavior analysis (cache misses, AMAT, saturation)
- Parallel efficiency and speedup metrics
- Optional cross-architecture comparisons (e.g., Xeon vs Ryzen)

---

## Requirements

- Python 3.x
- Required Python libraries:
  - matplotlib
  - numpy
  - pandas

Install dependencies if needed:

    pip install matplotlib numpy pandas

---

## Usage

All operations are managed through the Makefile.

### Run full analysis

    make

This will:

1. Detect all available benchmarks automatically
2. Parse raw logs from data/xeon_results/
3. Generate CSV files in data/xeon_csv/
4. Produce plots in plots/

---

### Run a specific benchmark

    make cg

This executes the pipeline only for the selected application.

---

### Regenerate plots only

    make plots APP=cg

This skips parsing and regenerates visualizations using existing CSV data.

---

### Architecture comparison (optional)

    make compare APP=cg

This runs a comparison between different architectures using:

- Xeon data (provided in the project)
- Ryzen data (optional, user-generated)

---

### Rebuild everything from scratch

    make re

Equivalent to:

    make fclean && make

---

### Cleaning

Remove generated plots and cache:

    make clean

Remove everything (plots + CSV data):

    make fclean

Clean a specific benchmark:

    make clean-cg

---

## Scripts Description

### analyze_performance.py

Main entry point of the pipeline. It orchestrates:

- Data extraction from raw logs
- Transformation into structured CSV format
- Generation of all visualizations

---

### etl.py

Handles parsing and transformation logic:

- Reads raw benchmark outputs
- Extracts metrics such as execution time, instructions, cache misses
- Produces structured datasets

---

### visualizations.py

Contains all plotting functions, including:

- Throughput vs time analysis
- Speedup and parallel efficiency
- Memory behavior (AMAT, cache misses)
- IPC and saturation analysis

---

### compare_architectures.py

Generates comparative plots between architectures, such as:

- Performance scaling
- Cache behavior differences
- Throughput comparison
- Efficiency and AMAT correlations

---

### style_config.py

Centralized configuration for:

- Colors
- Markers
- Benchmark definitions
- Thread configurations

---

## Ryzen Data (Optional)

The ryzen\_\* directories contain locally collected data used for validation and comparison purposes.

These datasets are not required to run the main pipeline.

They are included to:

- Cross-check results obtained on the Xeon platform
- Provide a reference for architectural comparison
- Demonstrate how the framework can be extended to other systems

Users are encouraged to:

- Run their own benchmarks on different hardware
- Replace or extend these datasets with their own measurements

---

## Reports and Documentation

A detailed performance analysis can be found in:

    docs/

This includes:

- Interpretation of results
- Scalability analysis
- Memory bottleneck discussion
- Architectural insights

---

## Notes

- The pipeline automatically adapts to the available thread configurations in the dataset.
- Missing metrics (e.g., cache data) are handled gracefully.
- The design prioritizes reproducibility and modularity.

---

## Summary

This project provides a structured and automated way to:

- Analyze HPC benchmark performance
- Understand scaling behavior
- Identify memory bottlenecks
- Compare architectures

It is intended both as a practical analysis tool and as a foundation for further experimentation.
