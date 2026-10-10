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
- 提供命令行功能和连续问答界面
- 提供本地检索效果评估脚本

## 技术栈

- Python
- SQLite
- argparse
- pathlib、re
- urllib
- DeepSeek Chat API
- unittest
- Git

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
  tests/
    test_storage.py
    test_retrieval.py
    test_llm.py
    test_workflow.py
  main.py
  chat.py
  evaluate.py
  evaluation_questions.json
  README.md
```

## 环境准备

需要 Python 3.11 或更高版本。在 PyCharm 中使用项目下的 `.venv` 作为解释器。

DeepSeek API Key 不写入代码，通过环境变量提供：

```text
DEEPSEEK_API_KEY=你的APIKey
```

## 启动问答界面

`chat.py` 是独立启动入口，不改变 `main.py` 原有的命令行功能。启动后会先重新读取 `data` 目录并建立索引，然后进入连续问答模式。

在 PyCharm 中创建 Python 运行配置：

```text
名称：企业问答界面
脚本路径：D:\zhuomian\简历修改m\企业 FAQ 问答助手\chat.py
工作目录：D:\zhuomian\简历修改m\企业 FAQ 问答助手
Python 解释器：项目下的 .venv
环境变量：DEEPSEEK_API_KEY=你的APIKey
```

也可以在项目根目录直接运行：

```powershell
python chat.py
```

启动后输入问题，例如：

```text
年假有多少天
```

程序会输出回答和资料来源。输入 `q`、`quit`、`exit` 或 `退出` 可以正常结束。直接按 `Ctrl+C` 时，程序会捕获 `KeyboardInterrupt` 并显示“已退出问答”，不会输出完整异常堆栈。

## 命令行功能

原来的命令行功能保持不变：

```powershell
python main.py index
python main.py search "年假"
python main.py ask "年假有多少天"
python main.py stats
```

各命令含义：

- `index`：读取资料并重建 SQLite 索引
- `search`：只检索资料，不调用大模型
- `ask`：检索资料并调用 DeepSeek
- `stats`：查看文档和片段数量

## 测试与评估

运行单元测试：

```powershell
python -m unittest discover -s tests -t . -v
```

运行检索效果评估：

```powershell
python main.py index
python evaluate.py
```

## 已知限制

- 当前使用中文关键词检索，不是向量检索或完整 RAG 平台
- 当前只支持 TXT 和 Markdown 资料
- 当前是命令行问答界面，没有图形界面
- 当前未加入用户权限、客户系统接口和生产部署
- 检索评估只代表当前测试资料和问题集，不代表生产环境准确率
