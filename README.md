# HyperInfer

HyperInfer is a prefix KV cache loading system for LLM inference. The current
implementation is built on the FlexGen/H2O codebase and focuses on selective KV
loading plus layer-aware asynchronous prefetching.

## Repository Layout

- `h2o_flexgen/flexgen/`: FlexGen-based implementation and performance scripts.
- `h2o_flexgen/flexgen/flex_opt_fast_pcache.py`: main HyperInfer entry.
- `h2o_flexgen/flexgen/my_pcache_fast.py`: prefix cache implementation.
- `h2o_flexgen/flexgen/scripts/lm_performance_fast_pcache.sh`: performance
  comparison script.

## Environment

The tested internal environment is `/home/zrd/miniconda3/envs/impress` with
Python 3.12.13. For a fresh setup, create a Python environment and install:

```bash
pip install -r requirements.txt
```

`requirements-impress-freeze.txt` records the exact pip package snapshot from
the internal `impress` environment. It is mainly for provenance and debugging;
`requirements.txt` is the recommended installation entry.

Model weights and generated prefix KV caches are not included in this
repository.

## Running Performance Comparisons

The fast-path comparison script mirrors the original `lm_performance.sh`
comparison set, but routes all commands through `flex_opt_fast_pcache.py`.

```bash
cd h2o_flexgen/flexgen
bash scripts/lm_performance_fast_pcache.sh
```

Useful overrides:

```bash
CUDA_VISIBLE_DEVICES=1 bash scripts/lm_performance_fast_pcache.sh
PYTHON_BIN=/path/to/python bash scripts/lm_performance_fast_pcache.sh
GPU_SIZE=10240 CPU_SIZE=32768 bash scripts/lm_performance_fast_pcache.sh
```

Before running, create or link the runtime cache directory expected by the
FlexGen scripts:

```bash
cd h2o_flexgen/flexgen
mkdir -p cache/kvs cache/prefix/opt-6.7b cache/prefix/opt-13b cache/prefix/opt-30b
```

## Running Accuracy Evaluations

The accuracy scripts use the local `lm_eval/base.py` and `lm_eval/evaluator.py`
patches. Run the symlink step once in the same Python environment used for the
experiments:

```bash
cd h2o_flexgen/flexgen
python ./lm_eval/symlink.py
```

Then run the figure scripts:

```bash
./scripts/figure_11.sh
./scripts/figure_15.sh
./scripts/figure22_acc.sh
```

If `python` is not on `PATH`, pass the interpreter explicitly:

```bash
PYTHON_BIN=/path/to/python ./scripts/figure_15.sh
```
