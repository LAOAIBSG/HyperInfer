def append_jsonl_files(source_file, target_file):
    # 打开目标文件以追加模式打开（'a'）
    with open(target_file, 'a', encoding='utf-8') as target:
        # 打开源文件以读取模式打开（'r'）
        with open(source_file, 'r', encoding='utf-8') as source:
            # 逐行读取源文件，并将每一行追加到目标文件
            for line in source:
                target.write(line)

# 指定源文件和目标文件的路径
source_file_path = '/home/zrd/impllm/h2o_flexgen/flexgen/fewshots_datasets/input/winogrande.jsonl'
target_file_path = '/home/zrd/impllm/h2o_flexgen/flexgen/fewshots_datasets/input/input_expand/winogrande-expand.jsonl'

# 调用函数执行文件追加
append_jsonl_files(source_file_path, target_file_path)
