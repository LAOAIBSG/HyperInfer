import os
import re
import sys

def parse_log_by_accum(log_file_path):
    results = []

    with open(log_file_path, 'r') as file:
        lines = file.readlines()

        cur_request_result = [] # each layer's results for each request
        cur_layer_result = {}
        last_layer_id = -1
        for line in lines:
            
            # 使用正则表达式匹配目标信息
            match_accum = re.search(r'target accum_percent for current attn layer\[(\d+)\] = ([\d.]+)%', line)
            match_select = re.search(r'select (\d+) / (\d+) = ([\d.]+)% of all tokens, with sim = ([\d.]+). Whether selected\? (.*)', line)

            if match_accum:
                layer = int(match_accum.group(1))
                accum_percent = int(match_accum.group(2))
                
                cur_layer_result['layer'] = layer
                cur_layer_result['accum_percent'] = accum_percent
                
                if layer < last_layer_id:
                    # 新的一个 request
                    results.append(cur_request_result)
                    cur_request_result = []
                
                last_layer_id = layer
            
            if match_select:
                num_selected = int(match_select.group(1))
                total_tokens = int(match_select.group(2))
                sele_percent = float(match_select.group(3))
                sim = float(match_select.group(4))
                is_selected = match_select.group(5) == 'True'
                
                if layer == last_layer_id:
                    cur_layer_result['num_selected'] = num_selected
                    cur_layer_result['total_tokens'] = total_tokens
                    cur_layer_result['sele_percent'] = sele_percent
                    cur_layer_result['sim'] = sim
                    cur_layer_result['is_selected'] = is_selected
                    
                    cur_request_result.append(cur_layer_result)
                    cur_layer_result = {}

    return results

def parse_log_by_percent(log_file_path):
    results = []

    with open(log_file_path, 'r') as file:
        lines = file.readlines()

        cur_request_result = [] # each layer's results for each request
        cur_layer_result = {}
        last_layer_id = -1
        for line in lines:
            
            # 使用正则表达式匹配目标信息
            match_select = re.search(r'select (\d+) / (\d+) = ([\d.]+)% of all tokens, with sim = ([\d.]+). Whether selected\? (.*)', line)

            if line.strip() == '== after init cache___ ==':
                layer = 0
                if len(cur_request_result) > 0:
                    # 新的一个 request
                    results.append(cur_request_result)
                    cur_request_result = []
                
                    cur_layer_result['layer'] = layer
                
            
            if match_select:
                num_selected = int(match_select.group(1))
                total_tokens = int(match_select.group(2))
                sele_percent = float(match_select.group(3))
                sim = float(match_select.group(4))
                is_selected = match_select.group(5) == 'True'
                
                cur_layer_result['num_selected'] = num_selected
                cur_layer_result['total_tokens'] = total_tokens
                cur_layer_result['sele_percent'] = sele_percent
                cur_layer_result['sim'] = sim
                cur_layer_result['is_selected'] = is_selected
                    
                cur_request_result.append(cur_layer_result)
                cur_layer_result = {}
                    
                layer += 1

    return results

def process_directory(directory_path):
    log_files = [f for f in os.listdir(directory_path) if f.endswith('trace.log')]
    all_results = {}

    for log_file in log_files:
        log_file_path = os.path.join(directory_path, log_file)
        if 'by_accum' in log_file_path:
            results = parse_log_by_accum(log_file_path)
        elif 'by_percent' in log_file_path:
            results = parse_log_by_percent(log_file_path)
        all_results[log_file] = results

    return all_results





def get_avg_sele_load_percent(results):
    sele_load_percent = []
    for each_request in results:
        for each_layer in each_request:
            if each_layer['is_selected']:
                sele_load_percent.append(each_layer['sele_percent'])
            else:
                sele_load_percent.append(100)
    print(f'avg selected load percent: {sum(sele_load_percent) / len(sele_load_percent)}')

def get_avg_sele_percent_for_accum(results):
    sele_percent_for_accum = []
    for each_request in results:
        for each_layer in each_request:
            sele_percent_for_accum.append(each_layer['sele_percent'])
    print(f'avg selected percent for target accum: {sum(sele_percent_for_accum) / len(sele_percent_for_accum)}')





def main():

    if len(sys.argv) < 2:
        print("Usage: python ../utils/extract_info.py [log_file | directory]")
        sys.exit(1)

    input_path = sys.argv[1]
    input_path = input_path.strip("'")

    if os.path.isfile(input_path):
        if input_path.endswith('.log'):
            if 'by_accum' in input_path:
                results = parse_log_by_accum(input_path)
            elif 'by_percent' in input_path:
                results = parse_log_by_percent(input_path)
            print(f"Results for {input_path}:")
            get_avg_sele_load_percent(results)
            get_avg_sele_percent_for_accum(results)
            
        else:
            print("Please provide a .log file.")
    elif os.path.isdir(input_path):
        all_results = process_directory(input_path)
        for log_file, results in all_results.items():
            print(f"\nResults for {log_file}:")
            get_avg_sele_load_percent(results)
            get_avg_sele_percent_for_accum(results)
    else:
        print("The provided path is neither a file nor a directory.")


if __name__ == "__main__":
    main()