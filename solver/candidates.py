"""Candidate password space for the SalPhaseIon end-game blob.

Everything the puzzle text hands us at this stage, in the forms the puzzle has
used before. The house style established by phases 2, 3 and 3.2 is:

    password = sha256(<tokens concatenated, lowercase, no separators>).hexdigest()

and the SalPhaseIon page repeats that instruction twice in its own encoding:
"shabef" -> sha256, "our first hint is your last command" (the very first hint
of the whole puzzle was HASHTHETEXT), and "sha256 ans too" (hash the answer as
well -> a second round).
"""
import itertools

# The 14x14 bit matrix from https://gsmg.io/puzzle
MATRIX = [
    [0,0,1,1,0,1,0,0,1,0,1,1,0,0],
    [1,1,1,1,0,0,1,1,1,0,1,0,1,1],
    [1,1,0,1,1,1,0,1,0,0,1,0,0,1],
    [0,1,1,0,1,0,0,0,0,1,1,1,0,1],
    [0,1,1,0,0,0,1,1,0,0,0,1,1,0],
    [1,0,0,1,1,0,0,0,1,0,0,0,1,1],
    [1,0,0,1,1,1,0,0,0,1,0,0,0,0],
    [1,1,1,0,0,0,0,0,0,0,1,0,0,0],
    [0,0,0,1,1,1,0,1,1,1,1,1,0,1],
    [1,1,1,1,1,1,0,0,1,1,0,0,0,1],
    [1,1,0,1,0,0,0,0,0,1,1,0,1,1],
    [1,1,1,1,0,0,1,0,1,0,1,1,0,0],
    [0,1,0,1,1,1,0,1,0,0,0,1,1,0],
    [0,1,1,0,1,1,0,1,1,0,1,0,1,1],
]
ROWSUMS = [sum(r) for r in MATRIX]                    # [6,10,8,7,6,6,5,4,9,9,7,8,7,9]
COLSUMS = [sum(c) for c in zip(*MATRIX)]              # [8,10,8,10,8,7,3,6,7,5,9,6,6,8]
DIAG    = [sum(MATRIX[i][i] for i in range(14)),
           sum(MATRIX[i][13 - i] for i in range(14))]

def _joins(nums):
    return [
        "".join(map(str, nums)),
        ",".join(map(str, nums)),
        " ".join(map(str, nums)),
        "-".join(map(str, nums)),
        str(sum(nums)),
    ]

# "matrixsumlist" read literally: the list of sums of the matrix.
MATRIXSUM_VALUES = sorted({
    v
    for nums in (ROWSUMS, COLSUMS, ROWSUMS + COLSUMS, COLSUMS + ROWSUMS, DIAG)
    for v in _joins(nums)
} | {"matrixsumlist"})

# Tokens the SalPhaseIon layer literally spells out, plus the answer-words the
# earlier layers left lying around.
TOKENS = [
    "matrixsumlist",
    "enter",
    "lastwordsbeforearchichoice",
    "thispassword",
    "sha256",
    "shabef",
    "ourfirsthintisyourlastcommand",
    "anstoo",
    "theone",
    "thematrixhasyou",
    "causality",
    "hashthetext",
    "ciaobella",
    "ciaobellao",
    "thefutureisours",
    "jacquefresco",
]

# The canonical seven, in the order the page presents them.
SEVEN = [
    "matrixsumlist",
    "enter",
    "lastwordsbeforearchichoice",
    "thispassword",
    "sha256",
    "ourfirsthintisyourlastcommand",
    "theone",
]

# Passwords/answers that actually worked earlier in the chain, kept as prefixes
# because the puzzle re-used "causality" as part 1 of the phase-3 password.
KNOWN_PRIOR = [
    "causality",
    "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
    "causalitySafenetLunaHSM11110",
]


def permutations_upto(pool, n):
    """All ordered concatenations of 1..n distinct tokens from pool."""
    for k in range(1, n + 1):
        for combo in itertools.permutations(pool, k):
            yield "".join(combo)
