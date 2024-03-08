#!/bin/bash
#PBS -N athena                  # Job name
#PBS -l nodes=4:ppn=32          # Number of nodes and processors per node
#PBS -l walltime=12:00:00	# Walltime (hh:mm:ss)
#PBS -o output.log              # Output file
#PBS -e error.log               # Error file
#PBS -q default                 # Queue name

# Change to your working directory
cd $PBS_O_WORKDIR

source /share/apps/composerxe-2011.2.137/bin/compilervars.sh intel64
PATH=/usr/mpi/intel/openmpi-1.10.3/bin:$PATH
LD_LIBRARY_PATH=/usr/mpi/intel/openmpi-1.10.3/lib:/share/apps/composerxe-2011.2.137/composerxe-2011.2.137/compiler/lib/intel64:/share/apps/comp$

DIR=$HOME/Athena-Cversion/bin

mpirun -np 128 $DIR/athena -i /home/dbambague/Athena-Cversion/tst/2D-sr-mhd/athinput.2Dks

