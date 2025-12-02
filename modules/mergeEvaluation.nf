#!/usr/bin/env nextflow
/*
 * Process to aggregate each week evaluation results of one Algorithm
*/

process mergeEvaluationProcess{
	container= "${params.docker_image}"
	input:
	path evaluation_result

	output:
	path "evaluation.json", emit evaluationResults
	"""
	mergeEvaluation.py --output evaluation.json --results ${evaluation_result}
	"""
}

