# aegis-dataset-prep

Dataset preparation, fine-tuning, upload, and evaluation workspace for the AEGIS
vision-language experiment notebook.

## Currently implemented

- `Qwen3-VL-2B-Finetuning-Eval.ipynb`: end-to-end notebook for loading a gated
  dataset, preparing train/test splits, running LoRA fine-tuning, uploading model
  artifacts, and evaluating predictions.
- `src/aegis_dataset_prep/`: reusable helpers for environment configuration,
  Hugging Face cache setup, dataset split/count utilities, chat conversion,
  pickle IO, plotting, and output parsing/metrics.
- `tests/`: lightweight unit tests for the reusable helpers and a notebook
  cleanliness check that rejects committed cell outputs or execution counts.
- `.github/workflows/ci.yml`: GitHub Actions workflow that runs the lightweight
  tests without installing the GPU/ML training stack.

## Planned

- Move more training and upload orchestration behind explicit script entrypoints
  once the runtime environment is stable enough to validate those paths outside a
  notebook.

## Design intent

- Keep heavy model training, authentication, uploads, and checkpoint syncs as
  explicit notebook actions.
- Keep pure parsing, conversion, config, and counting logic in importable modules
  so they can be reviewed and tested without GPU access or private credentials.

## Non-goals

- This repository does not publish model weights, datasets, credentials, run
  links, account IDs, or local runtime outputs.
- The CI workflow does not attempt to install `unsloth`, CUDA-specific `torch`,
  or run fine-tuning/evaluation.

## Redacted

- Dataset IDs, model destinations, Hugging Face tokens, W&B credentials, account
  identifiers, and executed authentication output must stay outside git history.

## Safe setup

1. Create an isolated Python environment outside this repository.
2. Install the runtime-specific GPU stack first, then run `pip install -r requirements.txt`.
3. Copy `.env.example` into your private runtime configuration and fill values
   locally only.
4. Review the first notebook cell before running any training, sync, or upload
   cells. Required settings include experiment name, base model, dataset, output
   model destination, LoRA rank, and batch size.

## Local checks

Run the lightweight checks without the training stack:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Local Outputs

Generated checkpoints, run logs, converted datasets, local caches, and notebook checkpoints are ignored by `.gitignore`. Keep large artifacts and private credentials out of git history.
