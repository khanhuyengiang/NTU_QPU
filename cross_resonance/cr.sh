#!/bin/bash

#SBATCH --partition=ntu-qpu
#SBATCH --output=slurm.out

export QIBO_BACKEND="qibolab"
export QIBOLAB_PLATFORM="icarusq_iqm5q"
export QIBOLAB_PLATFORMS="/mnt/scratch/qibolab_platforms_nqch"

module load qibolab/0.1.5
srun python3 cr_test.py
