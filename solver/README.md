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


## Round 3: calibrated against the creator's own blobs

The Phase 2 and Phase 3 ciphertexts (archived in `source/`) have *known*
passwords, which makes them the calibration data this harness never had.

**The puzzle uses the SHA-256 KDF, not MD5.** Phase 2 decrypts to its documented
plaintext under `sha256("causality")` with the SHA-256 KDF and fails padding
under MD5; Phase 3 does the same under its seven-part password. `calibrate.py`
asserts both. Every sweep before this had to hedge across both KDFs; future ones
get double the throughput. Past negative results stand -- both were tested, so
SHA-256 was always covered.

**The seven-part concatenation reproduces its documented digest exactly**, which
confirms the creator's assembly convention: parts joined with no separator, case
preserved, punctuation and spaces kept where the source has them.

### The first byte is not free

Under this block's decode convention (digits -> decimal integer -> base 16 ->
ASCII), the first byte of the output is fixed by the *digit count*, because
`hex()` pads to an even length and the leading bits follow from log2(N):

| digits | reachable first bytes | can start with a letter? |
| --- | --- | --- |
| 570 (partC) | 5-45 | **no** |
| 91 (partA) | 8-78 | **no** |
| 63 (`lastwordsbeforearchichoice`) | 1-255 | yes |
| 29 (`thispassword`) | 1-255 | yes |

Both solved segments are short. partA and partC, read as single numbers, cannot
begin with a letter under *any* digit mapping. The whole-string reading was
never viable -- they have to be chunked, like the z-separated segments were,
except partA and partC carry no `z` to chunk them on.

`chunkhunt.py` therefore sweeps chunked decodes: every digit mapping x both digit
sets x chunk sizes 2-60, filtered on the leading chunk, for 42,819,840
(mapping, size) pairs per run. Zero decoded to lowercase throughout, for either
run. Uniform chunking is out; whatever splits them is irregular.

### Correction

An earlier background sweep (partA keying partC across all 9! alphabet
orderings) reported zero, and that zero was meaningless: its fast filter
required the first two decoded bytes to be lowercase letters, which the table
above shows is impossible at 570 digits. The `fastdecode.py` arithmetic is
sound and validated -- it was anchored on a criterion that cannot hold. Any
re-run must filter on printable ASCII across several bytes, not leading
lowercase.

## Round 4: the Chain-4 XOR mask is a tautology

A widely repeated argument holds that the mask `b657264f2f6e6921` "drops directly
out of the ciphertext under the already-established OpenSSL grammar": take the
first eight unexplained bytes `e5364a3b4a0a367e`, XOR with `Salted__`
(`53616c7465645f5f`), obtain the mask, apply it, and a literal `Salted__` header
appears followed by a salt and 1152 bytes of "perfectly block-aligned"
ciphertext.

That argument is circular. The mask is *defined* as `first8 XOR "Salted__"`, so
`first8 XOR mask == "Salted__"` holds by algebra for any eight bytes in
existence. And 1168 - 16 = 1152 = 72x16 regardless of input, so the block
alignment is arithmetic, not evidence.

`maskdemo` in the commit log runs the identical procedure on random noise: every
trial yields a `Salted__` header, a plausible-looking salt, and exactly 1152
bytes at `1152 % 16 == 0`. Noise passes this test 100% of the time.

This does not prove the Chain-4 object is not real. It proves the argument
offered for it carries no information. The only thing that would settle it is a
password that decrypts a blob we hold.

### The 35x32 coordinate fit, quantified

The completed control table `# -4 2 32 12 4 27 0 2 -16 15 #` read as five
(block, byte) pairs against a 35x32 field does fit: block slot accepts -35..34,
byte slot accepts 0..31, and all five pairs are legal. Under a null that
shuffles the same ten values into five random pairs, **8.4%** of arrangements
fit. That is roughly one in twelve -- suggestive, not exceptional, and the
pairing was chosen after the target dimensions were known.

### A fair refinement of the vanity-address argument

Selection is not derivation. A vanity key cannot be *computed* from the
artifacts, but it can be *stored* in a payload and *selected* out of it. So a
coordinate/selector reading stays compatible with the vanity constraint, while
XOR-reduction-to-an-apex does not -- and indeed the reported apex
`683c4eec...73a9` fails against the prize HASH160, exactly as the vanity
argument predicts it must.

## Round 5: the 79-byte record repeats — and it beats 103×103

With the Cosmic plaintext verified and held locally (`cosmic.dec`), the two
competing readings of it can finally be compared on evidence.

### The record format recurs across two independent blobs

    SalPhaseIon plaintext:  32 + 32 + 15 = 79     K_C1, K_C2, E_C
    Cosmic plaintext:       32 + 32 + 15 = 79     K_B1, K_B2, E_B
                            32 + 32 + 15 = 79     K_H1, K_H2, E_H
                            1169 remaining

A record layout appearing three times across two separately obtained ciphertexts
is structural corroboration of exactly the kind the 103×103 construction lacks.

### The two readings disagree, and one of them has to go

| | "half" | "better half" |
| --- | --- | --- |
| 103×103 → base38 | `0423d911…` | `48cc46e6…` |
| 79-byte records | `db9ccfe9…` (K_H1) | `44d19415…` (K_B1) |

Different values. Both cannot be the intended pair. The record layout is
corroborated across two blobs; 103×103 has no corroboration and fails its null
test — its "span 38" is the *median* span for random data (round 4). Weight
belongs on the records. 103×103 reproduces faithfully from the real plaintext,
but reproducing an arithmetic pipeline is not evidence the pipeline was intended.

### Negative results this round

- **No derivation of the working Cosmic key** `6ac438fa…` from `K_C1`, `K_C2`,
  `K_S1`, `K_S2`, `E_C` or `E_S`: XOR of every subset, SHA-256 of every ordered
  concatenation, and `EVP_BytesToKey` over concatenations in raw/hex/HEX under
  both digests. The key decrypts the blob; its published provenance still does
  not reproduce it.
- **None of the ten recovered scalars reaches the prize HASH160** — `K_C1/2`,
  `K_B1/2`, `K_H1/2`, `K_S1/2` and the two 103×103 values, compressed and
  uncompressed — nor do pairwise XOR, modular sum, difference, or SHA-256 of the
  half/better-half keys.
- The 1169-byte tail is 7.84 bits/byte over 250 distinct values: encrypted, not
  encoded.

### A validator note, twice learned

A content filter keyed on printability, word counts or base58 ratio **rejects
the correct Cosmic plaintext** (printable 0.40, words 0, base58 0.24). Any sweep
using one cannot succeed even when the password is in its candidate set. These
payloads are binary key material. Validate on a plaintext hash or a structural
invariant, never on readability.
