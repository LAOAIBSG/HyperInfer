# 数据集格式以及用法

有shared prefix的数据集有三个 ./sys_prompt_1.jsonl 和 ./sys_prompt.jsonl 是生成式任务（无标准答案）。 ./2wikimqa_my.jsonl 是问答式任务，有正确答案。  
PIQA 和 winorande是用来测精度的，和动机实验无关。

数据格式：
```json
{
    "input": "任务的输入/指令，通常较短，比如QA中的问题、Few-shot任务中的提问等",
    "context": "任务所需的长语境文本，比如文档、跨文件代码、Few-shot任务中的few-shot样本",
    "answers": "由所有标准答案组成的列表",
    "length": "前三项文本的总长度（中、英文分别用字、词数统计）",
    "dataset": "本条数据所属数据集名称",
    "language": "本条数据的语言",
    "all_classes": "分类任务中的所有类别，非分类任务则为null",
    "_id": "每条数据的随机id"
}
```
加载数据可以参考 `h2o_flexgen/flexgen/flex_opt.py` 中的 `get_inputs`函数。
