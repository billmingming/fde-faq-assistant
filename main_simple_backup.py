import json
import os
import re
from pathlib import Path
from urllib import error, request


def load_sections(path: str):
    text = Path(path).read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", text.strip())
    sections = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 2:
            continue
        sections.append({
            "title": lines[0].strip("[]"),
            "content": "\n".join(lines[1:]),
        })

    return sections


def make_terms(text: str):
    text = text.lower()
    terms = set(re.findall(r"[a-z0-9_]{2,}", text))

    for run in re.findall(r"[\u4e00-\u9fff]+", text):
        if len(run) == 1:
            terms.add(run)
        else:
            terms.update(run[i:i + 2] for i in range(len(run) - 1))

    return terms


def search(question: str, sections: list[dict], top_k: int = 3):
    query_terms = make_terms(question)
    results = []

    for section in sections:
        text = section["title"] + "\n" + section["content"]
        score = sum(1 for term in query_terms if term in text.lower())
        if score > 0:
            results.append((score, section))

    results.sort(key=lambda item: item[0], reverse=True)
    return results[:top_k]


def ask_deepseek(question: str, results):
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        return "未配置 DEEPSEEK_API_KEY，暂时只显示检索结果。"

    context_parts = []

    for index, (score, section) in enumerate(results, start=1):
        context_parts.append(
            f"[{index}] {section['title']}\n{section['content']}"
        )

    context = "\n\n".join(context_parts)

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是企业文档问答助手。只能根据用户提供的资料回答；"
                    "资料中没有答案时，明确说“资料中没有找到依据”。"
                    "回答后保留来源编号，例如 [1]。"
                ),
            },
            {
                "role": "user",
                "content": f"资料：\n{context}\n\n问题：{question}",
            },
        ],
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
            response_data = json.loads(response.read().decode("utf-8"))
            return response_data["choices"][0]["message"]["content"]

    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return f"DeepSeek API 错误 {exc.code}：{detail[:300]}"

    except error.URLError as exc:
        return f"网络连接失败：{exc.reason}"


def main():
    sections = load_sections("data/handbook.txt")
    question = input("请输入问题：")
    results = search(question, sections)

    if not results:
        print("资料中没有找到相关内容。")
        return

    print("\n检索结果：")
    for index, (score, section) in enumerate(results, start=1):
        print(f"\n[{index}] {section['title']}，匹配分：{score}")
        print(section["content"])

    print("\nAI 回答：")
    print(ask_deepseek(question, results))


if __name__ == "__main__":
    main()