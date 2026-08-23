# `solver/` — tooling for the SalPhaseIon end-game

Reproducible tooling for the part of the GSMG.IO 5 BTC puzzle that is still
open: the two AES blobs on the SalPhaseIon / Cosmic Duality page. Nothing in
here is a claim that the puzzle is solved — it is a verified harness, the
candidate space that the puzzle's own text implies, and the honest result of
running one against the other.

Run everything from inside this directory (`cd solver`). Only dependency:

    pip install pycryptodome

## Files

| file | what it does |
| --- | --- |
| `gsmg.py` | EVP_BytesToKey (MD5 and SHA-256 flavours), the salted-blob container, and a cheap padding oracle |
| `selftest.py` | encrypts with the real `openssl` binary and decrypts with `gsmg.py` — run this first, it must pass |
| `extract.py` | pulls the SalPhaseIon symbol stream out of `../README.md` and splits it on the `z` separators |
| `numeric.py` | the letters→digits→hex→ASCII decode the block already uses; validated against the two solved segments |
| `matrix.py` | row/column sums of the 14×14 bit matrix — the literal reading of `matrixsumlist` |
| `candidates.py` | the token pool the SalPhaseIon layer spells out, plus every reading of `matrixsumlist` |
| `sweep.py` | two-stage filter: PKCS#7 padding, then plaintext plausibility |
| `run_salphaseion.py` | the actual sweep over the candidate space |
| `analyze.py` | structural statistics on the still-undecoded 570-symbol segment |
| `source/` | the verbatim page source: the SalPhaseIon symbol stream and the full Cosmic Duality blob |
| `pagehash.py` | rebuilds both blobs from the page and tests the "hash this page's text" reading |
| `run_sweeps.py` | the candidate sweep, against **both** blobs |
| `digitmap.py` | exhausts all 9! digit assignments for the block's own decode convention |
| `checkerboard.py` | straddling checkerboard / VIC, the cipher the puzzle already used in 3.2.2 |
| `polybius.py` | 9x9 coordinate-pair hypothesis for partC |
| `hashtheruns.py` | hashes the undecoded runs under all 9! digit mappings, against both blobs |
| `wordscore.py`, `english.py` | word-segmentation scorer, calibrated against known puzzle plaintexts |

## Why the oracle is cheap

The blob is a 96-byte OpenSSL container: `Salted__` + 8-byte salt + 80 bytes of
ciphertext (5 AES blocks), so the plaintext is 65–80 bytes. A 64-character hex
private key pads to exactly 80 — which is presumably the point.

To reject a wrong password you only need the last two ciphertext blocks: decrypt
the last one in ECB, XOR with its predecessor, check PKCS#7. That is one AES
block operation, and it kills 255/256 of all candidates. Survivors get fully
decrypted and are kept only if the whole plaintext is printable ASCII, which
random bytes essentially never are. Measured: ~85,000 candidates/second/core,
and the padding survivor count lands within a few percent of `n/256` every run —
i.e. the oracle behaves exactly as the maths says it should, which is the
evidence that a zero-hit result is a real zero and not a broken pipeline.

## What has been tried here, and the result

`python3 run_salphaseion.py` — 1,412,800 decryptions, **zero** plausible
plaintexts:

| sweep | decryptions |
| --- | --- |
| all 5,040 orderings of the seven spelled-out tokens × 24 readings of `matrixsumlist` | 967,680 |
| ordered combinations of 1–4 tokens from the wider pool | 407,296 |
| prior-phase passwords, alone and glued to each token | 2,592 |
| XOR-chains of the token SHA-256 digests, used as the password | 23,040 |
| the same XOR-chains injected directly as key + four IV guesses | 12,192 |

Each base string is tried raw, as `sha256(x)`, as `sha256(sha256(x))` and as
`sha256(bytes(sha256(x)))`, against both the MD5 KDF (OpenSSL 1.0, which is what
2019 would have produced) and the SHA-256 KDF (OpenSSL 1.1+).

This is consistent with, and tiny next to, the community's published negative
result of 335M+ candidates. The password is not a straightforward assembly of
the tokens the page hands you.

## The part nobody has decoded

`python3 extract.py` splits the 895-symbol block into:

- **partA** — 91 symbols over `a–i`
- the `abba` run — 104 bits → `matrixsumlist`
- **partC** — 570 symbols over `a–i`
- `z`-separated: 63 symbols → `lastwordsbeforearchichoice`, 29 symbols → `thispassword`
- plain text: `shabef our first hint is your last command` (`shabef` = `sha`+2+5+6 = sha256)

`numeric.py` reproduces both `z`-segment solves exactly, so the decode convention
is confirmed — and it does **not** work on partA or partC.

`analyze.py` on partC: IC = 0.1181 against 0.1111 for a flat 9-symbol alphabet,
75–78 of the 81 possible symbol pairs occur, longest repeated n-gram is 5
(`aedgg`, ×3). That is the signature of a fractionated or keyed cipher, not a
simple substitution — a 9×9 Polybius pairing with a repeated alphabet would look
exactly like this, which is consistent with the keyed-square reading that has
been proposed elsewhere, and equally consistent with several other constructions.
There is a mild bias toward `g`/`h`/`i` (row-plane digit 2 at 42% vs 33%) that
nothing yet explains.

## Where the wall is

The two blobs need a password. The page tells you *what to hash* in terms nobody
has pinned down (`lastwordsbeforearchichoice` in particular is a label, not an
answer — the answer is presumably a Matrix quote, and the space of "last words
before the Architect's choice" is large and unconstrained). Until partA/partC
give up a constraint, this is unguided search, and unguided search over a SHA-256
password space does not terminate.


## Round 2: with the real page source

The page source was retrieved by hand (`gsmg.io` is blocked from this
environment) and archived under `source/`. Three things came out of it:

**The README transcription is byte-perfect.** All 895 symbols match the page
exactly, and the README stream is an exact prefix of the real 1075-symbol
stream. Transcription error was never the problem.

**There is no grid.** The block lives in a `<textarea>`; the rows in the
screenshot are soft-wrap, not layout. Column-major and spiral reading orders are
therefore not a thing to chase.

**The Cosmic Duality blob is now here in full** — 1792 base64 chars, 1344 bytes,
`Salted__` + salt `2d3f6fe06dc950e6` + 1328 bytes = 83 AES blocks, so its
plaintext is 1313-1328 bytes. That is a paragraph of text, not a bare key.
`run_sweeps.py` now runs the whole candidate space against both blobs:
2,825,600 decryptions total, zero plausible plaintexts.

### Eliminated

- **The block's own decode convention, exhaustively.** `digitmap.py` tries all
  9! digit assignments under both digit sets (725,760 per run) for the
  letters→digits→decimal→base 16→ASCII decode that produced
  `lastwordsbeforearchichoice` and `thispassword`. Nothing above 75% lowercase
  for either partA or partC. This convention is *dead* for those two runs — not
  spot-checked, exhausted.
- **"Our first hint is your last command" read as HASHTHETEXT applied to this
  page.** `pagehash.py`: 12 readings of "the text" x 5 normalisations x 4
  password forms x 2 KDFs x 2 blobs. Zero.
- **Hashing the undecoded runs themselves**, under every possible digit mapping
  (`hashtheruns.py`). If "hash the text" means the runs rather than the page, and
  the mapping is non-alphabetical, the string to hash is the mapped decimal form.
  All 9! mappings x both digit sets x 4 pieces (partA, partC, and both
  concatenations) x single/double SHA-256 x 2 KDFs x 2 blobs = **23,224,320
  decryptions**. Zero.
- **Unkeyed 9x9 Polybius** for partC (`polybius.py`).
- **Straddling checkerboard / VIC** with the phase-3.2.2 alphabet, a plain
  alphabet and an ETAOIN alphabet, every row pair, three digit mappings — 810
  clean decodes per run, nothing above the noise threshold.

### A scoring trap worth knowing about

The first checkerboard pass reported six "hits" scoring in the thousands. They
were artifacts: an ETAOIN-ordered alphabet maps frequent digits to frequent
letters, so the output is a wall of E/T/A/O/I/N/S/R that sails through
chi-square while containing no words. `wordscore.py` replaces that with maximum
word-coverage segmentation, calibrated on this puzzle's own plaintexts:

| text | score |
| --- | --- |
| `lastwordsbeforearchichoice` | 0.43 |
| `theflowerblossomsthrough...` | 0.34 |
| the ETAOIN wall that fooled the old scorer | 0.16 |
| random letters | 0.08 |

Threshold 0.28. Re-scored, every checkerboard and Polybius result falls to
0.0-0.2. Any future search should use this scorer, not letter frequency.
