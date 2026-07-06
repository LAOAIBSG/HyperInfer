# HyperInfer

HyperInfer is a prefix KV cache loading system for LLM inference. The current
implementation is built on the FlexGen/H2O codebase and focuses on selective KV
loading plus layer-aware asynchronous prefetching.

This repository is the public-release workspace. The original experimental
repository is kept separately so this copy can be cleaned and documented without
disturbing past experiment history.

## Repository Layout

- `h2o_flexgen/flexgen/`: FlexGen-based implementation and performance scripts.
- `h2o_flexgen/flexgen/flex_opt_fast_pcache.py`: main HyperInfer fast-path entry.
- `h2o_flexgen/flexgen/my_pcache_fast.py`: prefix cache implementation with
  read-only asynchronous prefetch.
- `h2o_flexgen/flexgen/scripts/lm_performance_fast_pcache.sh`: performance
  comparison script for the fast pcache path.
- `h2o_hf/`: H2O/HuggingFace-side evaluation code kept from the original
  baseline repository.
- `datasets/` and `seeds/`: small benchmark metadata and inputs used by scripts.

## Environment

The code uses the same environment as the original FlexGen/H2O setup. On our
internal machine, the tested environment is:

```bash
/home/zrd/miniconda3/envs/impress/bin/python
```

For a new machine, install dependencies from:

```bash
pip install -r requirements.txt
```

Model weights and generated prefix KV caches are not included in this repository.

## Running Performance Comparisons

The fast-path comparison script mirrors the original `lm_performance.sh` command
set, but routes all commands through `flex_opt_fast_pcache.py`.

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

## Notes For Public Release

- Generated logs, prefix caches, model weights, and large runtime artifacts are
  intentionally excluded.
- Add a repository-level license before making this repository public.
- The code still follows the structure of the research prototype; cleanup should
  prioritize reproducible scripts and clear cache-path documentation.
