#!/usr/bin/env nextflow
/*
 * Process to test models on datasets 
*/

process model_test{
    container= "cned-scenario:latest"
    input:
    tuple val(index), path(data_test), path(model)
    output:
    tuple val(index), path("evaluation_${index}")
    """
    test_RF.py --m ${model} --t ${data_test} --f "evaluation_${index}"
    """
}
