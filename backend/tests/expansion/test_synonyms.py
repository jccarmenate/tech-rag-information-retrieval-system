from app.expansion.synonyms import expand_with_synonyms, get_synonyms


def test_get_synonyms_returns_related_words_for_common_term():
    synonyms = get_synonyms("fast", max_synonyms=3)
    assert isinstance(synonyms, tuple)
    assert len(synonyms) <= 3


def test_get_synonyms_never_includes_the_term_itself():
    synonyms = get_synonyms("computer", max_synonyms=5)
    assert "computer" not in synonyms


def test_expand_with_synonyms_keeps_original_terms_first():
    expanded = expand_with_synonyms(["python", "library"], max_synonyms_per_term=1)
    assert expanded[0] == "python"
    assert expanded[1] == "library"
    assert len(expanded) >= 2


def test_expand_with_synonyms_handles_unknown_words_gracefully():
    expanded = expand_with_synonyms(["zzzznotarealword"], max_synonyms_per_term=2)
    assert expanded == ["zzzznotarealword"]
