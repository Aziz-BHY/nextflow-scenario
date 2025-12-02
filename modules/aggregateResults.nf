#!/usr/bin/env nextflow
/*
 * Process to aggregate results for one Algorithm
*/

process mergeResProcess {
    container= "${params.docker_image}"
    input:
    path(evaluation_files)
    output:
    path "output.json" , emit: alg_FinalResults
"""
merge_results.py --inputs ${evaluation_files} --output output.json
"""
}
