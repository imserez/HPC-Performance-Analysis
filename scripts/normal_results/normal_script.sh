#!/bin/bash

#$ -S /bin/bash
#$ -cwd
#$ -o pr2_1-out_$JOB_NAME_output.log$JOB_ID
#$ -e error.log
#$ -pe openmp 4

export OMP_NUM_THREADS=4
export OMP_STACKSIZE=16M

BASE_PATH="/share/apps/aca/benchmarks/NPB3.2/NPB3.2-OMP/bin"
threads_num=(1 2 4 8)
benchmarks=(cg.S cg.W cg.A cg.B)

verbose=1

for b in "${benchmarks[@]}"; do
	for t in "${threads_num[@]}"; do
		export OMP_NUM_THREADS=$t
		if [ $verbose -eq 1 ];
		then
			echo "Executing $b with $t threads"
		fi
		/usr/bin/time "$BASE_PATH/$b" 2>&1
	done
done
