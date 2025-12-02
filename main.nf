/* 
 * enables modules 
 */
// Include the process to request Data
include { requestData } from "./modules/Data_Request"

// Include the RF related Processes: Train, Test , Evaluate
include { RF_train } from "./modules/RFProcess"
include { model_test } from "./modules/testProcess"
include { predictionEvaluation as RF_eval} from "./modules/predictionEvaluation"
//include {mergeEvaluation as RF_merge_eval} from "./modules/mergeEvaluation"

// Include the process to merge all results in one file
include { mergeResProcess } from "./modules/aggregateResults"

// Load user algorithms
if (params.userModel && params.userTest) {
    include { userModel } from "${params.userModel}"
    include { userTest } from "${params.userTest}"
    include { predictionEvaluation as userEval} from "./modules/predictionEvaluation"
}

workflow {
    /*
    *   Define Channels
    */
    data_train = Channel.fromPath(params.train_data)
    data_test = Channel.fromPath(params.test_data)
    data_real_labels = Channel.fromPath(params.test_data)

    // Create tuple with data like:
    //    [2, data/path/train_2]
    //    [3, data/path/train_3]
    //    [1, data/path/train_1]
    // Note: Files should at least contain the pattern "_w[0-9]*.csv"
    data_test = data_test
        .map { [file(it).getName().split("_w")[-1].replaceAll(".csv", ""), it] }
    data_real_labels = data_real_labels
        .map { [file(it).getName().split("_w")[-1].replaceAll(".csv", ""), it] }

    /*
    *    Computations
    */

    requestData()
    data_train = requestData
        .out
        .map { [file(it).getName().split("_w")[-1].replaceAll(".csv", ""), it] }
    RF_train(data_train)

    // Generate associative : index <-> path data for tests <-> path model
    //    [4, data/path/test_4, data/path/model_4]
    //    [2, data/path/test_2, data/path/model_2]
    //    [3, data/path/test_3, data/path/model_3]
    //    [1, data/path/test_1, data/path/model_1]
    models_with_index =  RF_train
        .out
        .combine(data_test, by:0)
        .map { [it[0], it[2], it[1]] }

    model_test(models_with_index)

    // Generate associative : index <-> path data true labels <-> path prediction data
    //    [4, data/path/true_labels_4, data/path/prediction_4]
    //    [2, data/path/true_labels_2, data/path/prediction_2]
    //    [3, data/path/true_labels_3, data/path/prediction_3]
    //    [1, data/path/true_labels_1, data/path/prediction_1]
    evaluated_with_index = model_test
        .out
        .combine(data_real_labels, by:0)
        .map { [it[0], it[2], it[1]] }
    RF_eval("baseline", evaluated_with_index)
    evaluation_files = RF_eval
        .out
        .map { [it[1]] }
        .collect()

    if (params.userModel && params.userTest) {
        userModel(data_train)

        user_models_with_index = userModel
            .out
            .combine(data_test, by:0)
            .map { [it[0], it[2], it[1]] }

        userTest(user_models_with_index)

        user_evaluated_with_index = userTest
            .out
            .combine(data_real_labels, by:0)
            .map { [it[0], it[2], it[1]] }

        userEval("user", user_evaluated_with_index)

        user_evaluation_files = userEval
            .out
            .map { [it[1]] }
            .collect()
    }

    /*
    * Aggregate Results in one File
    */
    if (params.userModel && params.userTest) {
        evaluation_files = user_evaluation_files.combine(evaluation_files)
    }

    resultChannel = mergeResProcess(evaluation_files)
    resultChannel.view { filename -> "Concatenate results stored in ${filename}" }
}
