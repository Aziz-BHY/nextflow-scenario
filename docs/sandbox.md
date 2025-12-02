# Use the scenario with the sandbox

[[_TOC_]]

For information on the lola-sandbox, see [Readme - Sandbox](https://gitlab.inria.fr/lola/lola-sandbox) for more information and installation instruction.

## Create switchable-algorithms

Without proper switchable-algorithms (yet!), the current algorithm for generating model and test model will be used.

The `algo_recipe.json` for each switchable algorithm must exists to use them. See the [Create algorithm for Lola](https://loladoc-dev.loria.fr/algorithm-scenario/algorithm-creation/).

`algorithms/train_weeks/algo_recipe.json`:

``` json
{
    "name": "Train data",
    "description": "train qlsdjqsldjqsld",
    "command": "train_RF.py --p {{ RF_n_estimators }} {{ RF_criterion }} {{ RF_random_state }} --a {{ INPUT_DATA_TRAIN }} --m {{ OUTPUT_MODEL }}",
    "harbor_url": "cned-scenario:latest",
    "parameters": [
        {
            "name": "input data file",
            "description": "Path of the data used to train the model",
            "variable_name": "INPUT_DATA_TRAIN",
            "type": "input_file_1",
            "editable": false
        },
        {
            "name": "output model file",
            "description": "Path of the output model",
            "variable_name": "OUTPUT_MODEL",
            "type": "output_file_1",
            "editable": false
        },
        {
            "name": "n estimators",
            "description": "n estimators ??",
            "variable_name": "RF_n_estimators",
            "type": "int",
            "editable": true,
            "default": 10
        },
        {
            "name": "criterion",
            "description": "criterion",
            "variable_name": "RF_criterion",
            "type": "string",
            "editable": true,
            "default": "entropy"
        },
        {
            "name": "random state",
            "description": "random state",
            "variable_name": "RF_random_state",
            "type": "int",
            "editable": true,
            "default": 0
        }
    ]
}
```

`algorithms/test_weeks/algo_recipe.json`

``` json
{
    "name": "test data",
    "description": "test qlsdjqsldjqsld",
    "command": "test_RF.py --m {{ INPUT_MODEL }} --t {{ INPUT_TEST_DATA }} --f {{ OUTPUT_DATA }}_${index}",
    "harbor_url": "cned-scenario:latest",
    "parameters": [
        {
            "name": "input data file",
            "description": "Path of the data to test on the model",
            "variable_name": "INPUT_TEST_DATA",
            "type": "input_file_1",
            "editable": false
        },
        {
            "name": "input model file",
            "description": "Path of the model",
            "variable_name": "INPUT_MODEL",
            "type": "input_file_2",
            "editable": false
        },
        {
            "name": "output evaluation file",
            "description": "Path of the output file containing evaluation",
            "variable_name": "OUTPUT_DATA",
            "type": "output_file_1",
            "editable": false
        }
    ]
}
```

## Generate the sandbox configuration

`cned-parameters.json`

``` json
{
   "scenario_path":"scenario/cned-scenario",
   "scenario_parameters":{},
   "algorithms":[
      {
         "algorithm_path":"algorithms/train_weeks",
         "nf_variable":"userModel",
         "parameters": {
            "RF_n_estimators": 10,
            "RF_criterion": "entropy",
            "RF_random_state": 0
         }
      },
      {
         "algorithm_path":"algorithms/test_weeks",
         "nf_variable":"userTest",
         "parameters":{}
      }
   ]
}
```

## Run the sandbox

``` bash
mkdir -p workdir/
lola-sandbox run --lrs-host http://0.0.0.0:80 -w workdir -C cned-parameters.json
```

