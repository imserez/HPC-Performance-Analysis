#!/bin/bash

#$ -S /bin/bash
#$ -cwd
#$ -o pin_output_dcache_b.log
#$ -e error.log
#$ -pe openmp 4

export OMP_NUM_THREADS=4
export OMP_STACKSIZE=16M

BASE_PATH="/share/apps/aca/benchmarks/NPB3.2/NPB3.2-OMP/bin"
PIN_BIN="/share/apps/aca/pin-2.12-58423-gcc.4.4.7-linux/pin"
DCACHE_TOOL="/share/apps/aca/pin-2.12-58423-gcc.4.4.7-linux/source/tools/Memory/obj-intel64/dcache.so"

threads_num=(1 2 4 8)
benchmarks=(cg.S cg.W cg.A) # ch.B

verbose=1

for b in "${benchmarks[@]}"; do
	for t in "${threads_num[@]}"; do
		export OMP_NUM_THREADS=$t
		if [ $verbose -eq 1 ];
		then
			echo "Executing $b with $t threads"
		fi

		OUT_FILE="results_dcache/dcache_${b}_t${t}.out"
		$PIN_BIN -t $DCACHE_TOOL -o $OUT_FILE -- "$BASE_PATH/$b"
	done
done
