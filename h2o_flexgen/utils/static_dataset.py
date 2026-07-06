import json
from transformers import AutoTokenizer
import sys
import statistics

input_paths = [
    '../flexgen/fewshots_datasets/input/copa.jsonl',
    '../flexgen/fewshots_datasets/input/openbookqa.jsonl',
    '../flexgen/fewshots_datasets/input/piqa.jsonl',
    '../flexgen/fewshots_datasets/input/rte.jsonl',
    '../flexgen/fewshots_datasets/input/winogrande.jsonl',
    '../flexgen/fewshots_datasets/input/squad_val.jsonl',
    '../flexgen/fewshots_datasets/input/sys_prompt.jsonl',
]

def list_statistics(numbers):
    if not numbers:
        print("The list is empty")
        return
    
    max_value = max(numbers)
    min_value = min(numbers)
    mean_value = statistics.mean(numbers)
    median_value = statistics.median(numbers)
    try:
        mode_value = statistics.mode(numbers)
    except statistics.StatisticsError:
        mode_value = "No unique mode"  # 如果没有众数或有多个众数

    print(f"  Max: {max_value}")
    print(f"  Min: {min_value}")
    print(f"  Mean: {mean_value}")
    print(f"  Median: {median_value}")
    print(f"  Mode: {mode_value}")



tokenizer = AutoTokenizer.from_pretrained(f'cache/huggingface/hub/facebook/opt-30b', padding_side="left", use_fast=True)

for input_path in input_paths:
    print(f'\n-> dataset: {input_path}')
    requests = []
    prefix_dict = {}
    prefix_len_lst = []
    with open(input_path, 'r') as f:
        for line in f:
            if line.strip() != '':
                requests.append(json.loads(line))
    print(f'total request number: {len(requests)}')
    for request in requests:
        prompt = request['prompt']
        input_ids = tokenizer(prompt, add_special_tokens=False, return_tensors='pt').input_ids
        suffix_ids = tokenizer(request['suffix'], add_special_tokens=False, return_tensors='pt').input_ids
        prefix_len = input_ids.shape[1] - suffix_ids.shape[1]
        
        cur_prefix = str(input_ids[:, :prefix_len])
        if cur_prefix not in prefix_dict:
            prefix_dict[cur_prefix] = 0
        else:
            prefix_dict[cur_prefix] += 1
        # print(input_ids, input_ids.shape)
        # print(suffix_ids, suffix_ids.shape)
        # print(input_ids[:, :prefix_len], input_ids[:, :prefix_len].shape)
        # print(f'input_ids.len = {input_ids.shape[1]}, suffix_ids.len = {suffix_ids.shape[1]}, prefix_len = {prefix_len}')
        
        prefix_len_lst.append(prefix_len)

    # find min, max, avg
    print(f'unique prefix number: {len(prefix_dict)}')
    
    print('Token number per request statistics:')
    list_statistics(prefix_len_lst)
    
    print('Reuse times per prefix statistics:')
    list_statistics(prefix_dict.values())
    
    