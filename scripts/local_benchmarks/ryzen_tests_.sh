#!/bin/bash

# 1. Setup
CLASS="B"
THREADS=(1 2 4 8 12 16)
OUTPUT_FILE="perf_ryzen_class_${CLASS}.log"
EXECUTABLE="./bin/cg.${CLASS}.x"

# 2. Verify executable
if [ ! -f "$EXECUTABLE" ]; then
    echo "Error: Not found $EXECUTABLE. compile it with: 'make cg CLASS=$CLASS'!"
    exit 1
fi

# 3. Prepare output file
echo "===========================================================" > $OUTPUT_FILE
echo " RESULTS RYZEN 7 5800HS - CG CLASS $CLASS " >> $OUTPUT_FILE
echo "===========================================================" >> $OUTPUT_FILE
echo "Date: $(date)" >> $OUTPUT_FILE

# 4. Execution loop
for t in "${THREADS[@]}"; do
    echo "Executing with $t threads..."

    echo -e "\n\n-----------------------------------------------------------" >> $OUTPUT_FILE
    echo " TEST WITH $t THREADS" >> $OUTPUT_FILE
    echo "-----------------------------------------------------------" >> $OUTPUT_FILE

    export OMP_NUM_THREADS=$t

    # Run perf
    perf stat -e L1-dcache-loads,L1-dcache-load-misses,cache-references,cache-misses $EXECUTABLE >> $OUTPUT_FILE 2>&1

done

echo "Tests finished! Results in: $OUTPUT_FILE"
