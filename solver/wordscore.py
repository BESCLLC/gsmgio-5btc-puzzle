"""The right scorer for this puzzle.

Every plaintext this puzzle has ever produced is unspaced lowercase English:
"lastwordsbeforearchichoice", "thispassword", "theflowerblossomsthrough...".
So the test for a candidate decode is not letter frequency -- which a wall of
ETAOIN passes trivially -- but whether it *segments into words*.

Max-coverage segmentation by dynamic programming, weighted by word length so
that a few accidental short words cannot fake a hit.
"""
from functools import lru_cache
from wordfreq import top_n_list, zipf_frequency

WORDS = {w for w in top_n_list('en', 60000)
         if len(w) >= 3 and w.isalpha() and zipf_frequency(w, 'en') >= 2.5}
WORDS |= {"is", "it", "in", "of", "to", "at", "on", "or", "an", "as", "be",
          "by", "do", "go", "he", "if", "me", "my", "no", "so", "up", "us",
          "we", "am", "the", "key", "one", "you", "sha", "aes", "btc"}
MAXLEN = 18


@lru_cache(maxsize=None)
def _best(s):
    """-> (weighted covered chars, segmentation)"""
    if not s:
        return 0.0, ()
    best = _best(s[1:])
    best = (best[0], ('_' + s[0],) + best[1])
    for L in range(2, min(MAXLEN, len(s)) + 1):
        w = s[:L]
        if w in WORDS:
            sub = _best(s[L:])
            # length^1.5 so long words dominate; short words barely register
            val = sub[0] + L ** 1.5
            if val > best[0]:
                best = (val, (w,) + sub[1])
    return best


def score(text, sample=400):
    """0..1-ish: weighted word coverage. English prose lands ~0.8+, random
    letters ~0.15-0.25."""
    s = ''.join(c for c in text.lower() if c.isalpha())[:sample]
    if len(s) < 12:
        return 0.0
    _best.cache_clear()
    val, _ = _best(s)
    return val / (len(s) ** 1.5 / len(s) * len(s))


def segment(text, sample=400):
    s = ''.join(c for c in text.lower() if c.isalpha())[:sample]
    _best.cache_clear()
    return ' '.join(w for w in _best(s)[1])


if __name__ == "__main__":
    import random
    tests = {
        "known plaintext": "lastwordsbeforearchichoice",
        "known plaintext 2": "theflowerblossomsthroughwhatseemstobeaconcretesurface",
        "real English": "yourlifeisthesumofaremainderofanunbalancedequationinherent",
        "etaoin wall": "NEIOSSIIONATOETRRSSAEOANIOOSNOSTSFEEIOSSHNEIASRSSAOEYIRERTERFAIMSTNSINSEME",
        "random": ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(72)),
    }
    for k, v in tests.items():
        print(f"{score(v):.3f}  {k}")
        print(f"       {segment(v)[:100]}")
