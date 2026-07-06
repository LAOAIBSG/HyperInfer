# HyperInfer

HyperInfer is a prefix KV cache loading system for LLM inference. This release
keeps the original FlexGen/H2O-based research prototype, with scripts for the
accuracy experiments and the fast pcache performance comparison.

The repository does not include model weights or generated prefix KV caches.
Readers should prepare model weights on their own machine.

## Main Files

- `h2o_flexgen/flexgen/flex_opt.py`: accuracy experiment entry.
- `h2o_flexgen/flexgen/flex_opt_fast_pcache.py`: performance experiment entry
  with read-only asynchronous prefetch.
- `h2o_flexgen/flexgen/my_pcache_fast.py`: fast prefix cache implementation.
- `h2o_flexgen/flexgen/scripts/figure_11.sh`: accuracy script for Fig. 11.
- `h2o_flexgen/flexgen/scripts/figure_15.sh`: accuracy script for Fig. 15.
- `h2o_flexgen/flexgen/scripts/figure22_acc.sh`: accuracy part of Fig. 22.
- `h2o_flexgen/flexgen/scripts/lm_performance_fast_pcache.sh`: performance
  comparison script.

## Install

Create a Python environment and install the dependencies:

```bash
git clone https://github.com/ISCS-ZJU/HyperInfer.git
cd HyperInfer

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

If the PyTorch wheel selected by pip does not match your CUDA setup, install a
compatible PyTorch build first, then install the remaining packages.

`requirements-impress-freeze.txt` records the internal environment used during
development. It is provided for reference; `requirements.txt` is the recommended
installation entry.

## Prepare Runtime Paths

Set the paths used by both accuracy and performance scripts:

```bash
cd h2o_flexgen/flexgen

# Directory that stores FlexGen-converted OPT weights.
# Expected examples:
#   $WEIGHT_PATH/opt-6.7b-np
#   $WEIGHT_PATH/opt-13b-np
#   $WEIGHT_PATH/opt-30b-np
export WEIGHT_PATH=/path/to/flexgen_opt_weights

# HuggingFace cache directory for tokenizers and optional model downloads.
export HF_HOME=/path/to/huggingface_cache

# HyperInfer uses this variable when loading tokenizers or downloading weights.
# It can point to the same directory as HF_HOME.
export HYPERINFER_HF_CACHE=$HF_HOME

mkdir -p "$HF_HOME"
bash scripts/setup_runtime_dirs.sh
bash scripts/check_repro_setup.sh
```

`WEIGHT_PATH` should contain FlexGen-format OPT weights. Prepare them with the
steps below before running the experiments.

## Prepare FlexGen Weights

FlexGen does not load HuggingFace OPT checkpoints directly during inference. It
expects one directory per model under `WEIGHT_PATH`, with each tensor saved as a
NumPy file:

```text
$WEIGHT_PATH/opt-6.7b-np/
$WEIGHT_PATH/opt-13b-np/
$WEIGHT_PATH/opt-30b-np/
```

Convert HuggingFace OPT weights with `opt_config.py`:

```bash
cd h2o_flexgen/flexgen

export WEIGHT_PATH=/path/to/flexgen_opt_weights
export HF_HOME=/path/to/huggingface_cache
export HYPERINFER_HF_CACHE=$HF_HOME

python opt_config.py --model facebook/opt-6.7b --path "$WEIGHT_PATH"
python opt_config.py --model facebook/opt-13b --path "$WEIGHT_PATH"
python opt_config.py --model facebook/opt-30b --path "$WEIGHT_PATH"
```

The converter downloads HuggingFace PyTorch `.bin` shards into
`HYPERINFER_HF_CACHE`/`HF_HOME`, loads each shard with PyTorch, and writes every
parameter as a separate NumPy file under `$WEIGHT_PATH/<model-name>-np/`. During
conversion it also:

- removes the leading `model.` prefix from parameter names;
- renames `decoder.final_layer_norm` to `decoder.layer_norm`;
- copies `decoder.embed_tokens.weight` to `lm_head.weight` for the shared output
  embedding.

If the HuggingFace checkpoint is already downloaded, point
`HYPERINFER_HF_MODEL_DIR` to that model snapshot for one conversion:

```bash
export HYPERINFER_HF_MODEL_DIR=/path/to/local/facebook/opt-6.7b/snapshot
python opt_config.py --model facebook/opt-6.7b --path "$WEIGHT_PATH"
unset HYPERINFER_HF_MODEL_DIR
```

The current converter reads PyTorch `.bin` checkpoints. If a local snapshot only
contains `.safetensors` files, use a `.bin` checkpoint snapshot or convert it to
PyTorch format first.

## Run Accuracy Experiments

Patch the installed `lm_eval` package to use the local evaluator files:

```bash
cd h2o_flexgen/flexgen
python ./lm_eval/symlink.py
```

Then run the accuracy scripts:

```bash
./scripts/figure_11.sh
./scripts/figure_15.sh
./scripts/figure22_acc.sh
```

If your Python executable is not named `python`, pass it explicitly:

```bash
PYTHON_BIN=/path/to/python ./scripts/figure_15.sh
```

Accuracy outputs are written under `h2o_flexgen/flexgen/fewshots_datasets/output`
and summarized by the CSV files under `h2o_flexgen/flexgen/scripts/`.

## Run Performance Comparisons

The performance script follows the original `lm_performance.sh` comparison set
but routes commands through `flex_opt_fast_pcache.py`.

```bash
cd h2o_flexgen/flexgen
./scripts/lm_performance_fast_pcache.sh
```

Useful overrides:

```bash
# Use GPU 0 for this run only.
CUDA_VISIBLE_DEVICES=0 ./scripts/lm_performance_fast_pcache.sh

# Use a specific Python interpreter for this run only.
PYTHON_BIN=/path/to/python ./scripts/lm_performance_fast_pcache.sh

# Use a different FlexGen weight directory for this run only.
WEIGHT_PATH=/path/to/flexgen_opt_weights ./scripts/lm_performance_fast_pcache.sh

# Override the GPU/CPU KV cache capacity parameters used by the script.
GPU_SIZE=10240 CPU_SIZE=32768 ./scripts/lm_performance_fast_pcache.sh
```

The `VAR=value command` form only applies the variable to that single command.
Use `export VAR=value` if you want the setting to persist for later commands in
the same shell.

The script first generates the important-token mapping list and dumps prefix KV
data, then runs the AS/H2O/IMPRESS/HyperInfer comparison commands.

## Notes
