# 企业 FAQ 问答助手

## 项目背景

企业制度、课程说明和帮助文档通常分散在多个文本文件中，人工查找效率较低。本项目实现本地资料读取、文本切片、SQLite 存储和关键词检索，并调用 DeepSeek API 生成基于资料的回答。

## 主要功能

- 读取 `data` 目录下的 TXT 和 Markdown 资料
- 按标题拆分知识条目
- 对长文本进行切片并保存到 SQLite
- 支持中文二元词关键词检索
- 返回匹配片段、来源和匹配分
- 调用 DeepSeek API 生成带来源编号的回答
- 没有检索结果时明确提示，不调用大模型猜测
- 提供一个本地检索效果评估脚本

## 技术栈

- Python
- SQLite
- argparse
- pathlib、re
- urllib
- DeepSeek Chat API
- unittest

## 项目结构

```text
企业FAQ问答助手/
  app/
    storage.py
    retrieval.py
    llm.py
    workflow.py
  data/
    handbook.txt
    faq.sqlite
  tests/
    test_storage.py
    test_retrieval.py
    test_llm.py
    test_workflow.py
  main.py
  evaluate.py
  evaluation_questions.json
  README.md
  测试记录.md