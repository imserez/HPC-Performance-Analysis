 /bin/bash
#$ -cwd
#$ -o cpu_info.txt
#$ -e error_cpu_info.log

echo "=== CPU summary (lscpu) ==="
lscpu

echo -e "\n=== Exact CPU model (cpuinfo) ==="
cat /proc/cpuinfo | grep "model name" | uniq

echo -e "\n=== Cache line size ==="
getconf LEVEL1_DCACHE_LINESIZE
