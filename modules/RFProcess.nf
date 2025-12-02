#!/usr/bin/env nextflow
/*
 * Process to train RF model on data collected from the LRS
*/
process RF_train{
    container= "${params.docker_image}"
    input:
    tuple val(index), path(data_to_train)
    output:
    tuple val(index), path("model_${index}")

    """
    train_RF.py --p $params.RF_n_estimators $params.RF_criterion $params.RF_random_state --a ${data_to_train} --m "model_${index}"
    """
}
