import json
import os
from urllib import error, request


def build_messages(question: str, hits: list[dict]):
    context_parts = []

    for index, hit in enumerate(hits, start=1):
        context_parts.append(
            f"[{index}] 来源：{hit['source']}\n"
            f"标题：{hit['title']}\n"
            f"内容：{hit['content']}"
        )

    context = "\n\n".join(context_parts)

    return [
        {
            "role": "system",
            "content": (
                "你是企业知识库问答助手。"
                "只能根据提供的资料回答，"
                "资料中没有答案时明确说“资料中没有找到依据”。"
                "回答后使用 [1]、[2] 标注来源。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"资料如下：\n{context}\n\n"
                f"用户问题：{question}\n\n"
                "请根据资料回答，并保留来源编号。"
            ),
        },
    ]


def ask_deepseek(question: str, hits: list[dict]):
    if not hits:
        return "资料中没有找到相关内容。"

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        return "未配置 DEEPSEEK_API_KEY。"

    payload = {
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        "messages": build_messages(question, hits),
        "temperature": 0.2,
        "stream": False,
    }

    http_request = request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]

    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return f"DeepSeek API 错误 {exc.code}：{detail[:300]}"

    except error.URLError as exc:
        return f"网络连接失败：{exc.reason}"