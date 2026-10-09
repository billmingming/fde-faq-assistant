import argparse
import re
from pathlib import Path

from app.retrieval import split_text
from app.storage import Database
from app.workflow import answer_question, search_question


def parse_sections(file_path: Path):
    text = file_path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", text.strip())

    for block in blocks:
        lines = [
            line.strip()
            for line in block.splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        if lines[0].startswith("[") and lines[0].endswith("]"):
            title = lines[0].strip("[]")
            content = "\n".join(lines[1:])
        else:
            title = file_path.stem
            content = "\n".join(lines)

        if content.strip():
            yield title, content.strip()


def index_files(database, data_dir: str, max_chars: int, overlap: int):
    data_path = Path(data_dir)

    if not data_path.exists():
        raise FileNotFoundError(f"资料目录不存在：{data_path}")

    database.clear()
    document_count = 0
    chunk_count = 0

    files = [
        path
        for path in data_path.rglob("*")
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}
    ]

    for file_path in files:
        source = str(file_path.relative_to(data_path))

        for title, content in parse_sections(file_path):
            chunks = split_text(
                content,
                max_chars=max_chars,
                overlap=overlap,
            )

            if not chunks:
                continue

            database.add_document(source, title, chunks)
            document_count += 1
            chunk_count += len(chunks)

    return document_count, chunk_count


def create_parser():
    parser = argparse.ArgumentParser(
        description="企业 FAQ 问答助手"
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    index_parser = subparsers.add_parser(
        "index",
        help="读取资料并重建 SQLite 索引",
    )
    index_parser.add_argument(
        "--data",
        default="data",
        help="资料目录，默认是 data",
    )
    index_parser.add_argument(
        "--db",
        default="data/faq.sqlite",
        help="SQLite 文件路径",
    )
    index_parser.add_argument(
        "--max-chars",
        type=int,
        default=400,
        help="每个文本片段的最大长度",
    )
    index_parser.add_argument(
        "--overlap",
        type=int,
        default=50,
        help="相邻片段的重叠长度",
    )

    search_parser = subparsers.add_parser(
        "search",
        help="只检索资料，不调用大模型",
    )
    search_parser.add_argument("question")
    search_parser.add_argument("--db", default="data/faq.sqlite")
    search_parser.add_argument("--top-k", type=int, default=3)

    ask_parser = subparsers.add_parser(
        "ask",
        help="检索资料并调用 DeepSeek",
    )
    ask_parser.add_argument("question")
    ask_parser.add_argument("--db", default="data/faq.sqlite")
    ask_parser.add_argument("--top-k", type=int, default=3)

    stats_parser = subparsers.add_parser(
        "stats",
        help="查看索引统计信息",
    )
    stats_parser.add_argument("--db", default="data/faq.sqlite")

    return parser


def run_index(args):
    database = Database(args.db)

    try:
        document_count, chunk_count = index_files(
            database,
            args.data,
            args.max_chars,
            args.overlap,
        )
        print(f"索引完成：文档 {document_count} 个，片段 {chunk_count} 个。")
    finally:
        database.close()


def run_search(args):
    database = Database(args.db)

    try:
        results = search_question(
            database,
            args.question,
            limit=args.top_k,
        )

        if not results:
            print("资料中没有找到相关内容。")
            return

        for index, result in enumerate(results, start=1):
            print(f"\n[{index}] {result['title']}")
            print(f"来源：{result['source']}")
            print(f"匹配分：{result['score']}")
            print(result["content"])
    finally:
        database.close()


def run_ask(args):
    database = Database(args.db)

    try:
        result = answer_question(database, args.question)

        print("\nAI 回答：")
        print(result["answer"])

        if result["sources"]:
            print("\n来源：")
            for index, source in enumerate(result["sources"], start=1):
                print(
                    f"[{index}] {source['source']} - "
                    f"{source['title']}"
                )
    finally:
        database.close()


def run_stats(args):
    database = Database(args.db)

    try:
        stats = database.stats()
        print(f"文档数：{stats['documents']}")
        print(f"片段数：{stats['chunks']}")
    finally:
        database.close()


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "index":
        run_index(args)
    elif args.command == "search":
        run_search(args)
    elif args.command == "ask":
        run_ask(args)
    elif args.command == "stats":
        run_stats(args)


if __name__ == "__main__":
    main()