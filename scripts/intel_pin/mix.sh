#!/bin/bash

#$ -S /bin/bash
#$ -cwd
# // #$ -o pr2_1-out_$JOB_NAME_output.log$JOB_ID
#$ -o pin_output_mix_s_w.log
#$ -e error.log
#$ -pe openmp 4

export OMP_NUM_THREADS=4
export OMP_STACKSIZE=16M

BASE_PATH="/share/apps/aca/benchmarks/NPB3.2/NPB3.2-OMP/bin"
PIN_BIN="/share/apps/aca/pin-2.12-58423-gcc.4.4.7-linux/pin"
MIX_TOOL="/share/apps/aca/pin-2.12-58423-gcc.4.4.7-linux/source/tools/Mix/obj-intel64/mix-mt.so"

threads_num=(1 2 4 8)
benchmarks=(cg.S cg.W cg.A) # cg.B

verbose=1

for b in "${benchmarks[@]}"; do
	for t in "${threads_num[@]}"; do
		export OMP_NUM_THREADS=$t
		if [ $verbose -eq 1 ];
		then
			echo "Executing $b with $t threads"
		fi

		OUT_FILE="results_mix/mix_${b}_t${t}.out"
		$PIN_BIN -t $MIX_TOOL -o $OUT_FILE -- "$BASE_PATH/$b"
	done
done
