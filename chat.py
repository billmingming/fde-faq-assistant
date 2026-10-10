from app.storage import Database
from app.workflow import answer_question
from main import index_files


def main():
    database = Database("data/faq.sqlite")

    try:
        document_count, chunk_count = index_files(
            database,
            "data",
            max_chars=400,
            overlap=50,
        )

        print(
            f"资料索引完成：文档 {document_count} 个，"
            f"片段 {chunk_count} 个。"
        )
        print("输入问题开始问答，输入 q 退出。\n")

        while True:
            question = input("请输入问题：").strip()

            if question.lower() in {"q", "quit", "exit", "退出"}:
                print("已退出问答。")
                break

            if not question:
                print("问题不能为空。\n")
                continue

            result = answer_question(database, question)

            print("\nAI 回答：")
            print(result["answer"])

            if result["sources"]:
                print("\n来源：")
                for index, source in enumerate(
                    result["sources"],
                    start=1,
                ):
                    print(
                        f"[{index}] {source['source']} - "
                        f"{source['title']}"
                    )

            print()

    finally:
        database.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已退出问答。")