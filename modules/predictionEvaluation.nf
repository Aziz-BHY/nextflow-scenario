#!/usr/bin/env nextflow
/*
 * Process to evaluate the model ability to predict on unkown data 
*/

process predictionEvaluation {
    container= "${params.docker_image}"
    input:
    val(tag)
    tuple val(index), path(real_labels), path(predicted_data)
    output:
    // Add ${tag} in output name to avoir name collision between baseline
    // and user files
    tuple val(index), path("evaluation-${tag}_${index}.json")

    """
    evaluate.py --tag ${tag} \
                --r ${real_labels} \
                --p ${predicted_data} \
                --f "evaluation-${tag}_${index}.json" \
                --i $params.accuracy $params.f1_macro $params.f1_micro $params.precision_macro $params.precision_micro $params.recall_macro $params.recall_micro
    """
}
