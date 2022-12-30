"""
task_loaders.py | Author : Gabe Grand
Utilities for autogenerating configs for experiments based on templates.

"""

import json
import os
from enum import Enum

import data.drawings.make_tasks as drawing_tasks
from src.models.laps_grammar import LAPSGrammar
from src.models.model_loaders import (
    GRAMMAR,
    INITIALIZE_GROUND_TRUTH,
    LIBRARY_LEARNER,
    PROGRAM_REWRITER,
    SAMPLE_GENERATOR,
)
from src.task_loaders import ALL, GroundTruthOrderedTaskBatcher

DEFAULT_EXPERIMENT_DIR = "experiments_iterative"
DEFAULT_TEMPLATE_DIR = os.path.join(DEFAULT_EXPERIMENT_DIR, "templates")


DEFAULT_STITCH_PARAMS = {
    "max_arity": 2,
    "iterations": 1,
    "candidates_per_iteration": 1,
}

DEFAULT_CODEX_PARAMS = {
    "debug": False,
    "use_cached": False,
    "n_samples": 50,
    "n_samples_per_query": 5,
    "temperature": 0.40,
    "max_tokens_completion_beta": 2.0,
    "function_name_classes": ["human_readable", "default_no_inline", "numeric"],
    "final_task_origin": "default",
    "body_task_types": ["programs"],
    "final_task_types": ["programs"],
    "prepend_dsl_description": False,
}


class ExperimentType(str, Enum):
    ORACLE = "oracle"
    ORACLE_TRAIN_TEST = "oracle_train_test"
    STITCH = "stitch"
    STITCH_CODEX = "stitch_codex"
    STITCH_CODEX_LANGUAGE = "stitch_codex_language"
    STITCH_CODEX_LANGUAGE_ORIGIN_RANDOM_TEST = (
        "stitch_codex_language_origin_random_test"
    )
    STITCH_CODEX_DSL_DESCRIPTION = "stitch_codex_dsl_description"


def get_domain_metadata(domain: str):
    METADATA = {
        "logo": {
            "tasks_loader": "compositional_graphics_200",
            "task_language_loader": "compositional_graphics_200_synthetic",
            "ocaml_special_handler": "LOGO",
            "dsl_description_prefix": "",
            "global_batch_sizes": [5, 10, 15, 25, 50, 100, 200],
        },
        "clevr": {
            "tasks_loader": "clevr",
            "task_language_loader": "clevr_synthetic",
            "ocaml_special_handler": "clevr",
            "dsl_description_prefix": "",
            "global_batch_sizes": [5, 10, 15, 25, 50, 100, 191],
        },
        "re2": {
            "tasks_loader": "re2",
            "task_language_loader": "re2_synthetic",
            "ocaml_special_handler": "re2",
            "dsl_description_prefix": "Lambda calculus DSL for regular expressions.\n\nCharacter primitives must be composed using one of the functions; e.g., (regex_or 'a' (regex_or 'b' 'c'))",
            "global_batch_sizes": [5, 10, 15, 25, 50, 100, 200, 300, 400, 491],
        },
    }

    # Metadata for each drawing task domain
    METADATA["drawings"] = {
        "tasks_loader": "drawings",
        "task_language_loader": f"drawings_human",
        "ocaml_special_handler": "drawings",
        "global_batch_sizes": [
            5,
            10,
            15,
            25,
            50,
            100,
            200,
            300,
            400,
            500,
            600,
            700,
            800,
        ],
    }
    for drawing_domain in drawing_tasks.TASK_DOMAINS:
        drawing_domain_name = "drawings_" + drawing_domain
        drawing_domain_metadata = {
            "tasks_loader": drawing_domain_name,
            "task_language_loader": f"drawings_human_{drawing_domain}",
            "ocaml_special_handler": "drawings",
            "dsl_description_prefix": "",
            "global_batch_sizes": [5, 10, 15, 25, 50, 100, 150, 200],
        }
        METADATA[drawing_domain_name] = drawing_domain_metadata

    return METADATA[domain]


def build_config(
    experiment_name: str,
    experiment_type: str,
    domain: str,
    output_directory: str = DEFAULT_EXPERIMENT_DIR,
    random_seed: int = 0,
    iterations: int = 1,
    task_batcher: str = GroundTruthOrderedTaskBatcher.name,
    global_batch_size: int = ALL,
    enumeration_timeout: int = None,
    stitch_params: dict = DEFAULT_STITCH_PARAMS,
    codex_params: dict = DEFAULT_CODEX_PARAMS,
    compute_likelihoods: bool = True,
    compute_description_lengths: bool = True,
    increment_task_batcher: bool = False,
    init_frontiers_from_checkpoint: bool = False,
):
    config = {}
    config.update(
        build_config_body(
            experiment_type=experiment_type,
            domain=domain,
            iterations=iterations,
            task_batcher=task_batcher,
            global_batch_size=global_batch_size,
            enumeration_timeout=enumeration_timeout,
            stitch_params=stitch_params,
            codex_params=codex_params,
            compute_likelihoods=compute_likelihoods,
            compute_description_lengths=compute_description_lengths,
            increment_task_batcher=increment_task_batcher,
        )
    )
    config.update(
        build_config_metadata(
            experiment_name=experiment_name,
            domain=domain,
            experiment_type=experiment_type,
            global_batch_size=global_batch_size,
            output_directory=output_directory,
            init_frontiers_from_checkpoint=init_frontiers_from_checkpoint,
            random_seed=random_seed,
        )
    )
    return config


def build_config_metadata(
    experiment_name: str,
    domain: str,
    experiment_type: str,
    global_batch_size: int = ALL,
    output_directory: str = DEFAULT_EXPERIMENT_DIR,
    init_frontiers_from_checkpoint: bool = False,
    random_seed: int = 0,
):
    domain_meta = get_domain_metadata(domain)

    export_directory = os.path.join(
        output_directory,
        "outputs",
        experiment_name,
        "domains",
        domain,
        experiment_type,
        f"seed_{random_seed}",
    )
    log_directory = os.path.join(
        output_directory,
        "logs",
        experiment_name,
        "domains",
        domain,
        experiment_type,
        f"seed_{random_seed}",
    )

    return {
        "metadata": {
            "experiment_name": experiment_name,
            "experiment_id": f"{experiment_type}_{global_batch_size}",
            "human_readable": "Autogenerated iterative experiment.",
            "export_directory": export_directory,
            "log_directory": log_directory,
            "tasks_loader": domain_meta["tasks_loader"],
            "task_language_loader": domain_meta["task_language_loader"],
            "dsl_description_prefix": domain_meta["dsl_description_prefix"],
            "export_with_timestamp": False,
            "resume_checkpoint_directory": None,
            "init_frontiers_from_checkpoint": init_frontiers_from_checkpoint,
            "ocaml_special_handler": domain_meta["ocaml_special_handler"],
            "global_batch_size": global_batch_size,
            "random_seed": random_seed,
        }
    }


def build_config_body(
    experiment_type: str,
    domain: str,
    iterations: int = 1,
    task_batcher: str = GroundTruthOrderedTaskBatcher.name,
    global_batch_size: int = ALL,
    enumeration_timeout: int = None,
    stitch_params: dict = DEFAULT_STITCH_PARAMS,
    codex_params: dict = DEFAULT_CODEX_PARAMS,
    compute_likelihoods: bool = True,
    compute_description_lengths: bool = True,
    increment_task_batcher: bool = False,
):
    template_path = os.path.join(
        DEFAULT_TEMPLATE_DIR, f"template_{experiment_type}.json"
    )
    with open(template_path, "r") as f:
        config = json.load(f)

    domain_meta = get_domain_metadata(domain)

    model_initializers = config["model_initializers"]
    model_initializers[0]["model_loader"] = domain_meta["ocaml_special_handler"]
    config["model_initializers"] = model_initializers

    config["experiment_iterator"]["max_iterations"] = iterations
    config["experiment_iterator"]["task_batcher"]["model_type"] = task_batcher
    config["experiment_iterator"]["task_batcher"]["params"][
        "global_batch_size"
    ] = global_batch_size

    config["experiment_iterator"]["task_batcher"]["params"][
        "increment_at_global_iteration"
    ] = increment_task_batcher

    # params updates use the following precedence order (highest to lowest):
    # 1. params from CLI (e.g., stitch_params)
    # 2. params from template (e.g., block["params"])
    # 3. params from config_builder globals (e.g., DEFAULT_STITCH_PARAMS)

    loop_blocks = []
    for block in config["experiment_iterator"]["loop_blocks"]:
        if (
            block.get("model_type") == LAPSGrammar.GRAMMAR
            and block.get("model_fn") == LAPSGrammar.infer_programs_for_tasks.__name__
            and enumeration_timeout is not None
        ):
            block["params"].update(
                {
                    "enumeration_timeout": enumeration_timeout,
                }
            )
        if block.get("model_type") == SAMPLE_GENERATOR:
            _codex_params = DEFAULT_CODEX_PARAMS
            _codex_params.update(block["params"])
            _codex_params.update(codex_params)
            block["params"] = _codex_params
        if block.get("model_type") == LIBRARY_LEARNER:
            _stitch_params = DEFAULT_STITCH_PARAMS
            _stitch_params.update(block["params"])
            _stitch_params.update(stitch_params)
            block["params"] = _stitch_params
        if (
            block.get("model_type")
            in [
                LAPSGrammar.GRAMMAR,
                SAMPLE_GENERATOR,
                PROGRAM_REWRITER,
            ]
            or block.get("state_fn") == INITIALIZE_GROUND_TRUTH
        ):
            block["params"].update(
                {
                    "compute_likelihoods": compute_likelihoods,
                }
            )
        loop_blocks.append(block)
    config["experiment_iterator"]["loop_blocks"] = loop_blocks

    return config
