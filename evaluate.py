import argparse
import json
from pathlib import Path

from app.storage import Database
from app.workflow import search_question


def load_questions(path: str):
    data = json.loads(
        Path(path).read_text(encoding="utf-8")
    )

    if not isinstance(data, list):
        raise ValueError("评估文件必须是 JSON 数组")

    return data


def evaluate(database, questions: list[dict], top_k: int):
    matched = 0
    details = []

    for index, item in enumerate(questions, start=1):
        question = item["question"]
        expected_title = item["expected_title"]

        results = search_question(
            database,
            question,
            limit=top_k,
        )

        titles = [result["title"] for result in results]
        is_match = expected_title in titles

        if is_match:
            matched += 1

        details.append({
            "index": index,
            "question": question,
            "expected_title": expected_title,
            "actual_titles": titles,
            "is_match": is_match,
        })

    return matched, details


def main():
    parser = argparse.ArgumentParser(
        description="评估知识库检索命中率"
    )
    parser.add_argument(
        "--db",
        default="data/faq.sqlite",
        help="SQLite 数据库路径",
    )
    parser.add_argument(
        "--questions",
        default="evaluation_questions.json",
        help="评估问题文件",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="每次检索返回的结果数量",
    )
    args = parser.parse_args()

    questions = load_questions(args.questions)
    database = Database(args.db)

    try:
        matched, details = evaluate(
            database,
            questions,
            args.top_k,
        )
    finally:
        database.close()

    for item in details:
        status = "命中" if item["is_match"] else "未命中"
        actual = "、".join(item["actual_titles"]) or "无"

        print(
            f"{item['index']:02d}. {status} | "
            f"问题：{item['question']} | "
            f"期望：{item['expected_title']} | "
            f"实际：{actual}"
        )

    total = len(questions)
    rate = matched / total * 100 if total else 0

    print("\n评估结果：")
    print(f"问题总数：{total}")
    print(f"正确命中：{matched}")
    print(f"命中率：{rate:.1f}%")


if __name__ == "__main__":
    main()