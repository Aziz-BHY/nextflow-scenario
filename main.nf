#!/usr/bin/env nextflow

process TEST_SLURM {
    executor 'slurm'
    cpus 1
    time '5m'
    memory '1 GB'

    output:
    file "hello.txt"

    script:
    """
    echo "Hello from Slurm on host: hostname" > hello.txt
    """
}

workflow {
    TEST_SLURM()
}
