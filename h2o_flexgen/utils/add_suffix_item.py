import os
import json
import argparse

def process_jsonl_file(file_path):
    # 创建一个临时文件，用于存储更新后的内容
    temp_file_path = file_path + ".tmp"
    if file_path.endswith('2wikimqa_my.jsonl') or file_path.endswith('sys_prompt_1.jsonl') or file_path.endswith('sys_prompt.jsonl'):
        with open(file_path, 'r', encoding='utf-8') as infile, open(temp_file_path, 'w', encoding='utf-8') as outfile:
            is_modified = False
            for line in infile:
                if line.strip()!='':
                    data = json.loads(line)

                if 'suffix' not in data:
                    prompt = data.get('context', '') + data.get('input', '')
                    suffix = data.get('input', '')
                    data['prompt'] = prompt
                    data['suffix'] = data.pop('input')
                    data.pop('context')
                    
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
    elif file_path.endswith('squad_val.jsonl') or file_path.endswith('squad_train.jsonl') :
        with open(file_path, 'r', encoding='utf-8') as infile, open(temp_file_path, 'w', encoding='utf-8') as outfile:
            is_modified = False
            for line in infile:
                if line.strip()!='':
                    data = json.loads(line)

                if 'suffix' not in data:
                    prompt = data.get('context', '') + data.get('question', '')
                    suffix = data.get('question', '')
                    data['prompt'] = prompt
                    data['suffix'] = data.pop('question')
                    data.pop('context')
                    
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
    else:    
        with open(file_path, 'r', encoding='utf-8') as infile, open(temp_file_path, 'w', encoding='utf-8') as outfile:
            is_modified = False
            for line in infile:
                data = json.loads(line)
                
                if 'suffix' not in data:
                    prompt = data.get('prompt', '')
                    # 查找最后一次出现 '\n\nQuestion:' 的位置
                    question_index = prompt.rfind('\n\n')
                    if question_index != -1:
                        # 提取 '\n\nQuestion:' 之后的内容
                        suffix = prompt[question_index:]
                        # 添加新的键值对
                        data['suffix'] = suffix
                        is_modified = True

                # 将更新后的字典写回到临时文件中
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')

    # 用临时文件替换原文件
    os.replace(temp_file_path, file_path)
    if is_modified:
        print(f'-> 处理 {file_path} 完成')

def process_all_jsonl_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.jsonl'):
            file_path = os.path.join(directory, filename)
            process_jsonl_file(file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSONL files in a directory.")
    parser.add_argument('--directory', '-d', type=str, required=True, help="Path to the directory containing JSONL files.")
    
    args = parser.parse_args()
    directory = args.directory
    
    if os.path.isdir(directory):
        process_all_jsonl_files(directory)
    else:
        print(f"The specified path '{directory}' is not a valid directory.")
