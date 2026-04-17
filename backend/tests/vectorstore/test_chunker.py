from app.vectorstore.chunker import chunk_text


def test_short_text_returns_single_chunk():
    assert chunk_text("just a few words", chunk_size=200) == ["just a few words"]


def test_empty_text_returns_no_chunks():
    assert chunk_text("", chunk_size=200) == []


def test_long_text_is_split_with_overlap():
    text = " ".join(f"word{i}" for i in range(500))
    chunks = chunk_text(text, chunk_size=200, overlap=40)

    assert len(chunks) > 1
    # the overlap means the tail of one chunk reappears at the head of the next
    first_tail = chunks[0].split()[-40:]
    second_head = chunks[1].split()[:40]
    assert first_tail == second_head


def test_all_words_are_covered():
    words = [f"w{i}" for i in range(450)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=200, overlap=40)
    covered = set(" ".join(chunks).split())
    assert covered == set(words)
