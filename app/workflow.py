from app.llm import ask_deepseek
from app.retrieval import make_terms


def search_question(database, question: str, limit: int = 3):
    terms = make_terms(question)
    return database.search(terms, limit=limit)


def answer_question(database, question: str):
    hits = search_question(database, question)

    if not hits:
        return {
            "answer": "资料中没有找到相关内容。",
            "sources": [],
        }

    answer = ask_deepseek(question, hits)

    return {
        "answer": answer,
        "sources": hits,
    }