import re

CJK_RUN_RE = re.compile(r"[\u4e00-\u9fff]+")
ENGLISH_TOKEN_RE = re.compile(r"[a-z0-9_]{2,}")


def make_terms(text: str):
    lowered = text.lower()
    terms = set(ENGLISH_TOKEN_RE.findall(lowered))

    for run in CJK_RUN_RE.findall(lowered):
        if len(run) == 1:
            terms.add(run)
        else:
            terms.update(
                run[index:index + 2]
                for index in range(len(run) - 1)
            )

    return sorted(terms)


def split_text(text: str, max_chars: int = 400, overlap: int = 50):
    if max_chars <= 0:
        raise ValueError("max_chars 必须大于 0")
    if overlap < 0:
        raise ValueError("overlap 不能小于 0")
    if overlap >= max_chars:
        raise ValueError("overlap 必须小于 max_chars")

    normalized = "\n".join(
        line.strip()
        for line in text.splitlines()
        if line.strip()
    )

    if not normalized:
        return []

    paragraphs = normalized.split("\n")
    chunks = []
    current = ""

    for paragraph in paragraphs:
        candidate = (
            paragraph
            if not current
            else current + "\n" + paragraph
        )

        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        if len(paragraph) > max_chars:
            chunks.extend(
                split_long_text(paragraph, max_chars, overlap)
            )
        else:
            current = paragraph

    if current:
        chunks.append(current)

    return chunks


def split_long_text(text: str, max_chars: int, overlap: int):
    chunks = []
    start = 0
    step = max_chars - overlap

    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start += step

    return chunks