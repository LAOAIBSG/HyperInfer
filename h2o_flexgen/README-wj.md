
## Usage

### 注意：下面默认命令都在 H2O/h2o_flexgen/flexgen 中执行 （代码中的路径使用相对路径）

### 输出两个时间日志的差异和加速比（在 time_logs/下执行），取前k个最好的
python3 cal_parallel_benefits_sorted.py file1.txt file2.txt -k $样本数量

### 不使用h2o剪枝的推理
python flex_opt.py --gpu-batch-size 1 --overlap false --model facebook/opt-6.7b --prompt-len 256  // 如果提供的 prompt 长度超过 prompt-len，则会按照提供的 prompt 长度运行，不会截断

### 使用h2o剪枝的推理
python flex_opt.py --gpu-batch-size 1 --overlap false --model facebook/opt-6.7b --prompt-len 256 --hh-ratio 0.1 --hh-all

### 显示同层不同head、同head不同层的重要KV分布相似度
python flex_opt.py --gpu-batch-size 1 --overlap false --hh-ratio 0.1 --hh-all --model facebook/opt-6.7b --ret-topk-indices --prompt-len 256

### 前缀prefill后存入磁盘的 h2o_flexgen/flexgen/cache/prefix 目录下（输入去掉最后100个token剩下的作为前缀）[建议把 prefix 软连接到数据盘]
python flex_opt.py --gpu-batch-size 1 --overlap false --model facebook/opt-6.7b --prompt-len 256 --prefix-dump

### 判断 prefixkv 是否存在，存在则全部读取，拼接KV后进行推理
python flex_opt.py --gpu-batch-size 1 --overlap false --model facebook/opt-6.7b --prompt-len 256 --prefix-aware-inf --full-load

### 判断 prefixkv 是否存在，存在则部分读取，拼接KV后进行推理（读取的百分比由 --sele-percent 指定，由于实际上没有减少I/O数据量，因此仅用于动机测试）
python flex_opt.py --gpu-batch-size 1 --overlap false --model facebook/opt-6.7b --prompt-len 256 --prefix-aware-inf --full-load --sele-inf --sele-percent 80 20 10

### WIP: 判断 prefixkv 是否存在，层数<10时，仅读取第一个head，然后根据该结果去选择性读取后续head，拼接KV后进行推理 (--hh-ratio 和 --hh-all 是用于指定 decoding 阶段的 token 保留比例，如果不指定则全保留)
python flex_opt.py --gpu-batch-size 1 --overlap false --model facebook/opt-6.7b --prompt-len 256 --prefix-aware-inf --sele-load --hh-ratio 0.1 --hh-all


### 判断 prefixkv 是否存在，每层先读取指定的三个head，然后求出相似度 s，如果大于阈值 t，则选择众数的 token position 选择性加载剩余的 head 中的KV；如果小于 t, 则剩余的 head 中的 KV 全部加载
python flex_opt.py --gpu-batch-size 1 --overlap false --model facebook/opt-6.7b --prompt-len 256 --prefix-aware-inf --sele-load --sele-head 0 1 2 --accum-percent 90 --sim-thred 0.5


## 测评

### 不使用剪枝
```bash
pip install -r ../../requirements.txt
export CUDA_VISIBLE_DEVICES=0

# 测评accuracy
# 运行脚本 备份lm_eval.evaluator lm_eval.base模块, 并软连接到./lm_eval/下相应文件
python ./lm_eval/symlink.py
# 生成推理结果（自动写入 fewshots_datasets/output/ 目录下）
python flex_opt.py --gpu-batch-size 1 --overlap false --model facebook/opt-6.7b --input-path ./fewshots_datasets/input/piqa.jsonl --model-type opt --logits --gen-len 1 --no-dir
# 如果想要输出在终端，加入 --no-redir
# python -u flex_opt.py --model facebook/opt-6.7b --model-type opt --gpu-batch-size 1 --overlap false --prompt-len 256 --logits --gen-len 1

# 测评 [运行中如果出现提示选择 y/N 时，选 y ] （输出自动写入 result/output 目录下）
python evaluate_task_result.py --result-file result/output/piqa-opt-6.7b-full.jsonl --task-name piqa --model-type opt --exp "ori"

# 测评 perplexity 数据集为/impllm/datasets/sys_prompt*.jsonl 、 /impllm/datasets/2wikimqa_my.jsonl
python flex_opt.py --gpu-batch-size 1 --overlap false --model facebook/opt-6.7b --input-path ../../datasets/sys_prompt_1.jsonl --model-type opt --logits --gen-len 1 --perplexity
```

## 使用脚本评测精度

```bash
# 根据要运行的函数，自定义命令中需要传入的参数
./scripts/lm_eval.sh ori_acc prefixkv_dump full_load_sele_inf full_load_full_inf sele_load_by_accum sele_load_by_percent run_motiv2

```1

###  给数据集添加 suffix item
python ../utils/add_suffix_item.py -d dir2dataset

### 读取 sele load 方法下加载的 KV 比例
python ../utils/extract_info.py dirname

```

## performance test

```bash
### all commands on impllm/h2o_flexgen/flexgen
### first prepare directory impllm/h2o_flexgen/flexgen/cache on ssd available
mkdir cache/kvs cache/prefix/opt-6.7b cache/prefix/opt-13b cache/prefix/opt-30b

### clear logs before test
### get prefix file
./scripts/dump.sh
### performance test, the output will be written to scripts/performance.csv
./scripts/lm_performance.sh
### sense test, the output will be written to scripts/sense_sim_thred.csv and scripts/sense_chunk_size.csv
./scripts/sense_sim_thred.sh
./scripts/sense_chunk_size.sh
