def chunk_text(text, max_chars=800, overlap=100):
    text = text.replace("\r", "")
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, current = [], ""

    for p in paragraphs:
        if len(current) + len(p) <= max_chars:
            current += p + "\n"
        else:
            chunks.append(current.strip())
            current = current[-overlap:] + p + "\n"

    if current:
        chunks.append(current.strip())

    return chunks
