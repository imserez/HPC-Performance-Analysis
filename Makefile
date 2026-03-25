# ==========================================
# HPC Performance Analysis - Dynamic Makefile
# ==========================================

# 1. Global Variables & Paths
PYTHON = python3
SCRIPT = scripts/analyze_performance.py
BASE_RESULTS_DIR = data/xeon_results
CSV_OUT_DIR = data/xeon_csv
PLOTS_DIR = plots

# 2. Automatic Benchmark Detection
ALL_DIRS := $(notdir $(wildcard $(BASE_RESULTS_DIR)/*))
APPS := $(filter-out utils, $(ALL_DIRS))

# 3. Stamp files (Physical files to track completion)
# Transforms the list of apps into a list of hidden .done files
STAMPS := $(patsubst %, $(CSV_OUT_DIR)/%/.done, $(APPS))

# 4. Phony Targets
.PHONY: all clean fclean info re plots $(APPS) compare

# ==========================================
# Main Rules
# ==========================================

# 'make all' depends on all physical stamp files
all: $(STAMPS)

# User-friendly aliases (e.g., 'make cg' points to its stamp file)
$(APPS): %: $(CSV_OUT_DIR)/%/.done

# The physical rule: Only runs if the script or the raw data directory is newer than .done
$(CSV_OUT_DIR)/%/.done: $(SCRIPT) $(BASE_RESULTS_DIR)/%
	@echo "========================================"
	@echo "=> Starting pipeline for: $*"
	@echo "========================================"
	$(PYTHON) $(SCRIPT) --app $*
	@mkdir -p $(dir $@)
	@touch $@
	@echo "=> Analysis for $* completed successfully. ✅\n"

# Rebuild everything from scratch (make re)
re: fclean all



# ==========================================
# Optional Modules
# ==========================================

# 'make compare APP=cg' runs the optional architecture comparison
compare:
	@if [ -z "$(APP)" ]; then \
		echo "Error: You must specify an app (e.g., make compare APP=cg)"; \
	else \
		$(PYTHON) scripts/compare_architectures.py --app $(APP); \
	fi


# ==========================================
# Utilities & Cleaning
# ==========================================

# ==========================================
# New Specific Rules
# ==========================================

# 'make plots APP=cg' regenerates plots without re-parsing logs
plots:
	@if [ -z "$(APP)" ]; then \
		echo "Error: You must specify an app (e.g., make plots APP=cg)"; \
		exit 1; \
	fi
	@$(PYTHON) $(SCRIPT) --app $(APP) --plots-only && echo "=> Plots updated for $(APP). 🎨" || (echo "=> Failed to update plots. Run make first" && exit 1)

info:
	@echo "Base results directory : $(BASE_RESULTS_DIR)"
	@echo "Excluded directories   : utils"
	@echo "Detected benchmarks    : $(APPS)"

clean:
	@echo "=> Cleaning generated Plots, and stamp files and cache..."
	rm -f $(CSV_OUT_DIR)/*/.done
	rm -f $(PLOTS_DIR)/*/*/*.png
	@echo "=> Cleaning Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "=> Cleanup complete. 🧹"

clean-%:
	@echo "=> Cleaning generated files for $* (preserving CSV)..."
	rm -f $(CSV_OUT_DIR)/$*/.done
	rm -f $(PLOTS_DIR)/*/$*/*.png
	@echo "=> Cleanup for $* complete. 🧹"
# fclean ahora llama a 'clean' primero para asegurar que se borre también la caché
fclean: clean
	@echo "=> Deep cleaning output directories... Removing all CSV data..."
	rm -rf $(CSV_OUT_DIR)/*
	rm -rf $(PLOTS_DIR)/*
	@echo "=> Total reset complete. 🗑️"

