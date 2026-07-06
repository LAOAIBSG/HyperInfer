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

export WEIGHT_PATH=/path/to/flexgen_opt_weights
export OFFLOAD_DIR=/path/to/flexgen_offload_dir
export HF_HOME=/path/to/huggingface_cache
export HYPERINFER_HF_CACHE=$HF_HOME

bash scripts/setup_runtime_dirs.sh
bash scripts/check_repro_setup.sh
```

`WEIGHT_PATH` should contain FlexGen-format OPT weights, for example
`$WEIGHT_PATH/opt-6.7b-np`, `$WEIGHT_PATH/opt-13b-np`, and
`$WEIGHT_PATH/opt-30b-np`. If these converted weights are absent, the FlexGen
loader may try to download and convert HuggingFace `.bin` weights, which can take
a long time and requires enough disk space.

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
CUDA_VISIBLE_DEVICES=0 ./scripts/lm_performance_fast_pcache.sh
PYTHON_BIN=/path/to/python ./scripts/lm_performance_fast_pcache.sh
WEIGHT_PATH=/path/to/flexgen_opt_weights ./scripts/lm_performance_fast_pcache.sh
GPU_SIZE=10240 CPU_SIZE=32768 ./scripts/lm_performance_fast_pcache.sh
```

The script first generates the important-token mapping list and dumps prefix KV
data, then runs the AS/H2O/IMPRESS/HyperInfer comparison commands.

## Notes



