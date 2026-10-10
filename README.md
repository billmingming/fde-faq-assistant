# 企业 FAQ 问答助手

这是我用来练习 Python、SQLite 和大模型接口的一个小项目。企业制度、课程说明和帮助文档通常分散在多个文件里，查找起来比较麻烦，所以我把资料整理进本地知识库，再做一个可以提问的命令行工具。

程序不会直接把问题交给大模型。它会先在本地资料中找相关内容，再把找到的片段交给 DeepSeek，并要求回答只依据这些资料。如果没有找到内容，就直接提示，不调用大模型猜测。

## 目前实现的内容

- 读取 `data` 目录下的 TXT 和 Markdown 文件
- 按标题拆分资料，并对长文本进行切片
- 把文档和片段保存到 SQLite
- 对中文问题做简单检索，并显示来源和匹配分数
- 通过 DeepSeek API 生成带来源编号的回答
- 处理没有结果、缺少 API Key 和 HTTP 请求异常
- 提供 `chat.py` 连续问答界面
- 保留 `main.py` 的命令行功能

## 项目目录

```text
企业 FAQ 问答助手/
  app/
    storage.py        SQLite 存储和查询
    retrieval.py      中文关键词和文本切片
    llm.py            DeepSeek 请求与提示词
    workflow.py       检索和回答的连接流程
  data/
    handbook.txt      示例资料
  tests/
    test_storage.py
    test_retrieval.py
    test_llm.py
    test_workflow.py
  main.py             命令行入口
  chat.py             连续问答入口
  evaluate.py         检索效果评估
  evaluation_questions.json
```

## 运行前

建议使用 Python 3.11 或更高版本。在 PyCharm 中把项目解释器设置成项目目录下的 `.venv`。

API Key 不写进代码，放在环境变量里：

```text
DEEPSEEK_API_KEY=你的APIKey
```

## 直接进入问答界面

用 PyCharm 运行时，新建一个 Python 运行配置：

```text
脚本：chat.py
工作目录：项目根目录
环境变量：DEEPSEEK_API_KEY=你的APIKey
```

也可以在项目根目录执行：

```powershell
python chat.py
```

启动时会重新读取 `data` 目录并建立索引，然后可以连续输入问题：

```text
年假有多少天
```

程序会先显示相关资料，再显示 DeepSeek 的回答。输入 `q`、`quit`、`exit` 或 `退出` 可以结束。直接按 `Ctrl+C` 也会正常退出，不再显示完整的异常信息。

## 命令行用法

原来的几个命令仍然保留：

```powershell
python main.py index
python main.py search "年假"
python main.py ask "年假有多少天"
python main.py stats
```

`index` 用来重建本地索引；`search` 只查看检索结果，不请求大模型；`ask` 会检索后再请求 DeepSeek；`stats` 用来查看当前有多少文档和片段。

## 测试

运行单元测试：

```powershell
python -m unittest discover -s tests -t . -v
```

目前有 10 项测试，覆盖 SQLite 存储、中文检索、文本切片、DeepSeek 异常处理和问答流程。

检查检索效果：

```powershell
python main.py index
python evaluate.py
```

评估使用 10 个问题，看正确资料是否出现在前三个检索结果中。当前示例资料下全部能够命中。这个结果只说明当前资料集和问题集的检索情况，不代表回答准确率。

## 目前还没有做的

- 还没有接入向量检索，当前使用的是中文关键词匹配
- 目前只读取 TXT 和 Markdown
- 目前是命令行工具，没有图形界面
- 还没有用户权限、客户系统接口和生产环境部署
