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

## Round 6: Chain-4 verified — and the prize key is not stored in anything we hold

The b45a record closes the chain's shape. Four 79-byte records now span three
independently obtained ciphertexts:

    SalPhaseIon (salt 3ab58534)  ->  K_C1 K_C2 E_C
    b45a        (salt b45a5e3d)  ->  K_S1 K_S2 E_S      opened by K_C1 as a WIF
    Cosmic      (salt 2d3f6fe0)  ->  K_B1 K_B2 E_B | K_H1 K_H2 E_H | 1169 tail

### Chain-4 exists

The mask *argument* remains worthless — random noise yields a `Salted__` header
and 1152 aligned bytes 100% of the time. But the mask *object* is real, and the
decryption proves it where the header never could: applying the reported key/IV
to `masked[16:]` gives 1151 bytes with **valid padding** and
`sha256 = e4269ed5fbb202a81e5e1aa6b5190fdd1ea126b2c8547ea7cdbdf45387ea135b`,
the published anchor. Saved as `chain4.dec`. `1151 = 31 + 35x32`, and the
XOR-triangle apex reproduces exactly as `683c4eec…73a9`.

Both things were true at once: the argument carried no information, and the
object it argued for exists.

### The derivation story still does not reproduce — for the second time

`E_C || E_S || E_B[:2]` reproduces byte-exactly as the 32-byte password, and the
masked salt `5bbd88ac32481bca` reproduces too. But `EVP_BytesToKey` over that
password does **not** yield the working key `54fc3947…`. 54 variants tried —
raw/hex/HEX password, six salts, three digests. This is the same pattern as the
Cosmic key `6ac438fa…`: the key is correct, and the published account of where
it comes from does not produce it.

### The strongest new constraint

The prize address is a vanity address, so its key must be *stored*, not derived.
So slide a 32-byte window across every plaintext we hold — SalPhaseIon (79B),
Cosmic (1327B), Chain-4 (1151B) — and test each offset as a private key:

**2,464 windows, no prize.** None of the 35 Chain-4 blocks either, nor the
31-byte header padded either way, nor the apex.

The prize key is therefore not stored verbatim anywhere in the recovered
material. Either a further encrypted layer remains, or the key is assembled from
non-contiguous bytes — which is exactly what a selector would do.

### Loose end

The mask covers 1168 of the tail's 1169 bytes. The final byte of `cosmic.dec` is
used by nothing in any construction proposed so far.

## Round 7: the chain verified end to end — and the gap located

### The b45a blob was in this repo all along

It is the trailing base64 inside the **Phase 3.2 plaintext**, printed in the
README since 2020: `U2FsdGVkX1+0Wl49gnWTyiim…`, salt `b45a5e3d827593ca`, 96 bytes.
No archive hunt was needed.

That makes the whole chain independently reproducible from primary artifacts:

    SalPhaseIon blob (from page source)
      + password "matrixsumlist enter lastwordsbeforearchichoice thispassword matrixsumlist"
      + MD5 KDF
      -> 79B = K_C1 || K_C2 || E_C
    WIF(K_C1, uncompressed) = 5K2byJMssxFKuTgnk9YQjpBz5FhkwwF2LaZoAyTus8HjGEpz8AT
      -> opens the b45a blob, MD5 KDF
      -> 79B = K_S1 || K_S2 || E_S
    Cosmic blob + key 6ac438fa… / IV c6ff2e39…
      -> 1327B = K_B1 K_B2 E_B | K_H1 K_H2 E_H | 1169B tail
    tail masked + key 54fc3947… / IV 30efcf17…
      -> 1151B = 31B header + 35 x 32B

Every step verified locally against ciphertext transcribed from the page source.

### The gap

The chain rule is *the first key of each record, as a WIF, opens the next blob*.
It holds for `K_C1 -> b45a`. It does **not** hold for `K_S1 -> Cosmic`: neither
`K_S1` nor `K_S2`, compressed or uncompressed, under either KDF, produces the
working Cosmic key `6ac438fa…`.

So the chain is not `Sal -> b45a -> Cosmic`. It is:

    Sal -> b45a -> [ MISSING BLOB ] -> Cosmic

and that missing blob is what `WIF(K_S1)` opens. This also explains why the
Cosmic and Chain-4 key derivations have never reproduced: their published
provenance skips a link that nobody has published.

**What to hunt for:** a `Salted__` blob, probably 96 bytes like the other two,
that decrypts under `WIF(K_S1)` with the MD5 KDF to a 79-byte record.

### Correction

Last round I called the Chain-4 31-byte header "structured" on the basis of its
entropy (4.95) against the blocks' (7.83). That comparison is invalid: Shannon
entropy is bounded by log2(n), and log2(31) = 4.95 — the header's figure is
simply the maximum a 31-byte sample can show, meaning only that all 31 bytes are
distinct (P ≈ 0.15 for random bytes). Both regions are consistent with random.
Further, 28 of the 31 values exceed 34, so they cannot be block indices into a
35-block field. The header is not evidently a selector table. Withdrawn.

## Round 8: the Telegram dump has seven new salts — and they are all truncated

A Telegram export search for `U2FsdGVk` surfaced blobs with **seven salts that
appear nowhere in the puzzle chain**:

    aa46dd00cc230e6c   ab583398aaa4500d   e2991cdcd2c957f9   34a5901a53543d6a
    073f31b317bd0cf2   4a4a51c1562d7db7   4c664c282939f61a   4f37245e63fdb78a

Every one presented as exactly 32 bytes of ciphertext — which is the tell. Check
it against blobs whose true size is known:

| blob | real ciphertext | as captured |
| --- | --- | --- |
| Phase 2 | 656 B | 32 B |
| Cosmic | 1328 B | 32 B |
| Phase 3.2 | 2432 B | 32 B |

All three collapse to 32 bytes, because OpenSSL wraps base64 at 64 characters
and a line-oriented grep returns only the first line. The new salts are real
blobs; what was captured is their opening line.

This also means none of them *could* have opened, whatever key was tried: a
79-byte record needs 80 bytes of ciphertext = 5 blocks = 128 base64 characters
across two lines. Testing all eight recovered keys × WIF/hex/raw × both KDFs
against the truncated captures gave 2 padding-valid results out of 832, against
3.25 expected by chance — pure noise, as expected.

`tg_extract.py` re-extracts with continuation lines joined, tolerating `<br>`,
`<div>`, `<p>` and entity separators, and keeps the longest capture per salt.
Self-tested: it recovers Phase 2 at 656 B, Cosmic at 1328 B, Phase 3.2 at
2432 B and b45a at 80 B, and survives HTML markup interleaved between lines.

**Target:** a blob whose ciphertext is 80 bytes (5 blocks), opening under
`WIF(K_S1)` with the MD5 KDF.

## Round 9: the mechanism changes after SalPhaseIon — token hunting cannot reach Cosmic

A decoded creator hint was reported as an ordered sequence: `yellowblueprimes`,
`matrixsumlist`, `lastwordsbeforearchichoice`, `yinyang`.

### yellowblueprimes has real numeric content

The README's own additional hint reads *"Yellow has a number and so does Blue."*
Counting the 14×14 matrix:

    blue/black squares (1s) = 101   prime
    yellow/white squares(0s)=  95   not prime (5 × 19)

101 is both prime and the matrix total — so `matrixsumlist` and the blue count
are the same number, and the next prime after 101 is 103, the modulus of the
103×103 claim. That is a genuine thread, not a naive reading.

### But the tokens cannot be Cosmic's password, and this is provable

Two keys still have no reproducing derivation: Cosmic's `6ac438fa…` and
Chain-4's `54fc3947…`. If the new tokens were the missing ingredient, they would
close that gap. Searched:

- all ordered subsets up to length 5 of a 19-token pool — 11,956,472 derivations
- all **products** up to length 5 of a 16-token pool (repeats allowed, since the
  verified SalPhaseIon password repeats `matrixsumlist`) — 13,421,760 derivations
- each base string raw and SHA-256'd, under both KDFs, against both salts

**Zero matches.** And the search is sound, because a positive control was
included: the verified SalPhaseIon key. The sweep found it —
`matrixsumlist + enter + lastwordsbeforearchichoice + thispassword +
matrixsumlist`, MD5, raw — proving the method finds a real password of exactly
this shape when one exists.

### Why no token string will ever open Cosmic

The chain changes mechanism after SalPhaseIon:

    SalPhaseIon  <- opened by a TOKEN CONCATENATION
    b45a         <- opened by WIF(K_C1), a key from the previous plaintext
    Cosmic       <- key 6ac438fa…, provenance unknown
    Chain-4      <- key 54fc3947…, provenance unknown

Once the chain switches to *the first key of each record, as a WIF, opens the
next blob*, the passwords stop being English at all — they are base58 key
encodings. So searching keyword phrases against Cosmic is a category error, and
the 12M + 13.4M derivations above confirm it empirically.

One more constraint from the verified password: `yellowblueprimes` cannot precede
`matrixsumlist` in the SalPhaseIon password, because that password is confirmed
and begins with `matrixsumlist`. Whatever `yellowblueprimes` keys, it is not that
step.

## Round 10: carrier efficiency kills the mapping — and says what partA/partC hold

The proposed reading is that the creator's hint list names what each carrier
decodes to: `dbbi…`(partA) → `yellowblueprimes`, `abba` → `matrixsumlist`,
z-seg → `lastwordsbeforearchichoice`, `faed…`(partC) → `yinyang`.

Two of those are verified, so the shape of the idea is right. But measure the
**encoding efficiency** of the verified carriers:

| carrier | symbols | base | capacity | decodes to | used | efficiency |
| --- | --- | --- | --- | --- | --- | --- |
| abba run | 104 | 2 | 104.0 bits | `matrixsumlist` | 104 bits | **100.0%** |
| abba run | 40 | 2 | 40.0 bits | `enter` | 40 bits | **100.0%** |
| z-seg | 63 | 10 | 209.3 bits | `lastwordsbeforearchichoice` | 208 bits | **99.4%** |
| z-seg | 29 | 10 | 96.3 bits | `thispassword` | 96 bits | **99.7%** |

Every verified carrier is packed essentially full. Now the proposal:

| carrier | symbols | capacity | proposed | efficiency |
| --- | --- | --- | --- | --- |
| partA | 91 | 288.5 bits | `yellowblueprimes` (128 bits) | 44.4% |
| partC | 570 | 1806.9 bits | `yinyang` (56 bits) | **3.1%** |

A creator who packs four carriers to 99–100% does not then spend 570 symbols on
a seven-letter word. The mapping cannot be right.

**But the same arithmetic says what they do hold.** At the established
efficiency:

    partA  ->  ~36 bytes of payload
    partC  -> ~226 bytes of payload

Neither is an English word. partA at ~36 bytes is 32 + 4 — the shape of a key
plus a short trailer, the same shape as the 103×103 output's HALF/BETTER/TRAIL.
partC at ~226 bytes is large enough to be a record pair or an encrypted object
in its own right.

That reframes both runs: they are not instructions, they are **data**, and every
attempt so far to read them as words was looking for the wrong size of thing.

### Validator, fourth time

The sweep's test was `wc>=3 or pr>0.93 or (padok and pr>0.6)`. Against the
verified SalPhaseIon plaintext: printable 0.39, words 0 — it returns **False**.
The correct password, had it been in the candidate list, would have printed
nothing. Re-run here with a padding + known-plaintext-hash validator, the
positive control fires immediately and correctly identifies the real password.

## Round 11: "key eyes" reproduced from primary data — and null-tested

The creator hint *"prime numbers are required to proceed"* + *"some characters
need to be zeroed out"* is not metaphor. partA and partC use `a-i` only; the
z-segments that decoded use `a-i` **and `o` = 0**. The missing zeros are the
literal missing ingredient, and primes are said to choose them.

This also dissolves the round-6 objection: a 570-digit number can never decode
to a leading letter, but zeroing leading digits shortens the effective number,
so that constraint does not apply once zeros enter.

### Prime-zeroing: negative

`zeroing.py` applies ten rules — zero or drop, at prime positions (0- and
1-indexed), at composite positions, at prime digit values, at composite values —
then decodes with the block's own convention. Best result 19% lowercase against
~10% for random bytes. Nothing. (Worth noting: `val-composite zero` on partC
yields **236 bytes**, matching the ~226–236 predicted by the round-10 efficiency
argument, so the sizing model holds.)

### The community's "key eyes", reproduced independently

Laying partC out as **30 × 19**, taking row sums, keeping the primes, and
mapping a1z26 mod 26:

    sums   = [92, 86, 102, 107, 80, 87, 101, 105, ...]
    primes = [107, 101, 89, 109, 103, 109, 97]
    ->  c w k e y e s        "key eyes"

Reproduced here from the page-source symbols, not taken from a write-up.

**Null test** (20,000 shuffles of partC's own multiset, same layout):

| | rate |
| --- | --- |
| output contains `key` or `eye` | 3.03% |
| output contains `keyes` | **0.010%** |
| mean output length | 6.8 (real: 7) |

The exact substring is ~1 in 10,000 — but across 12 layouts × 2 alphabet
mappings the effective rate is nearer 1 in 400. Suggestive, and consistent with
the creator's *"it's in front of your eyes"*. It is a **meta-hint, not a
cryptographic result**: it confirms partC is the right object and the prime
row-sum reading is on the right track, and it yields no key material.

## Round 12: prime-structure zeroing exhausted

Following the only creator-consistent signal (the 30×19 prime row-sums that give
`keyes`), zeroing was driven by that structure rather than by position primality:
keep/drop prime-sum rows, keep/drop prime-sum columns, concatenated or with the
others zeroed, on both runs.

**All negative.** The useful calibration: for uniform random bytes
P(printable) = 95/256 = **37.1%** and P(lowercase) = 26/256 = **10.2%**. Every
result landed at 33–43% printable and 0–18% lowercase — the null distribution.
Quoting a printability figure near 0.37 as a partial result is quoting noise.

Also closed: the `i=0, a=1..h=8` family. `digitmap.py`'s exhaustive sweep already
covered it — its `012345678` digit set assigns 0 to each letter in turn across
all 9! permutations, so every "treat one letter as zero" variant of the
un-zeroed reading is done.

### Standing state of partA / partC

| fact | status |
| --- | --- |
| capacity | partA ~36 B, partC ~226 B of payload |
| they are data, not words | established (carrier efficiency, round 10) |
| whole-string decode, all 9! mappings | exhausted, negative |
| uniform chunking 2–60, all mappings | exhausted, negative |
| prime position/value zeroing | exhausted, negative |
| prime row/column structure zeroing | exhausted, negative |
| unkeyed 9×9 Polybius, VIC/checkerboard | negative |
| running-key from partA over partC | negative (natural mapping) |
| 30×19 prime row-sums | yields `keyes`, p ≈ 1/400 after search correction |

The only positive signal partC has ever produced is a seven-character meta-hint.
Everything that would constitute a decode has been ruled out across its natural
search space.

## Round 13: three Telegram claims settled

**Jerry's 91 = 91.** The phase-3.2.2 plaintext stripped —
`INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE`
— is exactly 91 characters, and partA is exactly 91 symbols. Tempting, and
decisively wrong.

A 26→9 substitution is many-to-one, so different letters may share a symbol. But
the same *plaintext* letter must always give the same *cipher* symbol. It does
not: 17 of 21 letters map to multiple symbols, and `E` maps to **seven of the
nine**. partA is not a substitution of that phrase.

Nor is it positional. `A ≡ PT mod 9` agrees on 10/91 — chance is 11%. The
Vigenère difference stream `(PT − A) mod 26` shows **25 distinct values of 26**
and repeats at no period below 25. The length match is a coincidence of message
length.

**Pomyk's "many b's in prime positions."** Resampled null, 20,000 draws:

| | b's | at prime positions | expected | p |
| --- | --- | --- | --- | --- |
| partA 1-indexed | 25 | 7 | 6.6 | 0.515 |
| partA 0-indexed | 25 | 8 | 6.6 | 0.311 |
| partC either | 49 | 11 | 8.9 | 0.27 |

No clustering. The intuition that produced "primes are involved" came from the
creator's own hint, not from this distribution.

**The base-10 values circulating are wrong.** Under `a=1..i=9`:

    partA = 4229262833257298125259825775752522758852886212648256...  (91 digits, composite)
    partC = 6154775546324128877314365447647279711547791615378773...  (570 digits, composite)

Neither matches `4009060833…` nor the `2387909401…` that was primality-tested in
the thread. That discussion was reasoning about a different integer.

### The one surviving idea

nieods' *"dbbib is used to decode faed"* — partA keying partC — remains open, and
is the item outstanding from the round-6 retraction. `run_running2.py` sweeps it
properly: all 9! alphabet orderings × 22 keys from the 7×13 grid × 3 combining
ops × partC forwards and reversed, scoring the **entire** decode rather than a
structurally impossible leading-byte criterion.

## Round 14: the 91/91 match is coincidence; "key I's" tested

**Statistical independence.** Mutual information between partA's symbols and the
VIC plaintext's letters: observed 1.1384 bits, shuffled mean 1.1119, 95th
percentile 1.2346, **p = 0.344**. (MI is inflated at this sample size — 91 pairs
over 9×21 cells — so the shuffled baseline is the thing to compare against.)

Stated precisely, since the scope matters:

- **every letter-only function is dead** — substitution, bucketing, any scheme
  where the same letter always yields the same symbol (17 of 21 letters map to
  multiple symbols; `E` maps to seven of nine)
- **every periodic position function is dead** — the `(PT − A) mod 26` stream has
  25 distinct values of 26 and repeats at no period below 25
- what survives is only an *aperiodic* position-dependent encoding driven by a
  third source, which is unfalsifiable until someone names the source

So the 91 = T₁₃ = |VIC| coincidence is a coincidence unless that source appears.

**"key I's" tested.** Deleting the i's, mapping `i → 0`, and taking the
characters before/after each i, on both runs: everything at the 10.2% lowercase
/ 37.1% printable random baseline. One incidental confirmation — partA with its
i's deleted decodes to exactly **36 bytes**, matching the round-10 capacity
prediction.

## Round 15: the 91 → 121 prime-reinsertion construction

The best-formed hypothesis anyone has produced, and it reproduces exactly.

`N − π(N) = 91` has the **unique** solution `N = 121`, since π(121) = 30 and
121 is the 91st non-prime. Reinserting 30 zeros at prime positions gives an
11×11 grid; read as base 9 with `i = 0, a..h = 1..8` it yields exactly 48 bytes —
the size of an AES-256 key plus IV:

    53fb4ae40acf9d781932e8e2f8ac785b 0f5f2cc329e5b4822570ce79dc031f71
    b098c4986abcc0c6da62060a42ef68e1

Rebuilt independently here, byte-identical. What distinguishes this from every
other construction in this file is that **all its ingredients predate the
output**: 91 is partA's real length, "REINSERTING THE PRIME BASICS" is explicit
Architect text, the zero-character hint is the creator's, and 121 = 11² is a
consequence rather than a chosen target.

### What it is not

- It derives **neither** unexplained key. Hamming distance from `bs[0:32]` to the
  Chain-4 key is 124/256 bits (48.4%) and to the Cosmic key 144/256 (56.2%) —
  both at the 50% random line. No XOR, SHA-256 or EVP relation found either.
- `121 = 11²` is ~1 in 22 given the square density near 121 — notable, not
  miraculous, and since 91 was the creator's choice a designed 91 produces it by
  construction.
- The **80 i's** (5 + 75) against 80-byte ciphertexts is +0.81σ from the uniform
  base-9 expectation of 73.4. A coincidence of counts.

### A as an operator on the VIC answer

Tested directly, since mutual information only covers A *encoding* VIC, not A
*acting on* it. Shift ciphers (`VIC±A`, `A−VIC`) across four digit maps: best
score 0.087 against 0.28 for English. Selector readings (keep VIC letters where
A holds symbol X): the `A=='e'` selection scores 0.340, which **fails its null** —
random 18-letter subsequences of VIC score ≥ 0.340 **27.5% of the time**, because
selecting from an English sentence preserves English letter frequencies. It
segments as `nrc i h pie y lan hat ole`.

Note on the scorer: the 0.28 threshold was calibrated on 26–79 character
plaintexts and does **not** transfer to short fragments. Any selector result must
be scored against subsequences of the same source and length.

### Why this construction cannot currently be falsified

All four blobs in the chain are open. A correct 48-byte KEY‖IV would have
**nothing left to unlock**. Testing it against Cosmic — as was done — tests an
already-open door and can only fail. So this is *untested*, not disproved, and
it becomes testable the moment the missing blob between b45a and Cosmic appears.
The 121 hypothesis and the missing-link gap are complementary: if that blob
turns up, these 48 bytes are the first thing to try on it.

## Round 16: the entropy proof fails its control; "another door" is confirmed

### The entropy argument does not go through

Claim: A/C sit at near-random base-9 entropy, therefore no rearrangement can
yield text, therefore the key must be external.

The z-segments are the control — **known** to decode to English by this exact
scheme:

| run | n | alphabet | IC | H | % of max |
| --- | --- | --- | --- | --- | --- |
| z-seg → `lastwordsbeforearchichoice` | 63 | 10 | 0.0988 | 3.222 | **97.0%** |
| z-seg → `thispassword` | 29 | 9 | 0.1182 | 2.947 | 93.0% |
| partA | 91 | 9 | 0.1509 | 2.882 | 90.9% |
| partC | 570 | 9 | 0.1181 | 3.120 | 98.4% |

A segment that decodes to plain English sits at **97% of maximum entropy —
higher than partA**. Base conversion destroys the plaintext's frequency
structure, so order-0 symbol entropy cannot detect an English payload at all.

What survives: a **bijective** decode preserves total entropy, and 91 × 2.882 =
262 bits in 36 bytes is 7.3 bits/byte, which cannot be 36 English characters
(~54 bits). Bijective decodes to English are genuinely ruled out. But
**selection, zeroing and aggregation are lossy and escape the argument entirely**
— and those are precisely the operations the creator's hint names.

### The 21 Telegram blobs contain no new authentic object

| | |
| --- | --- |
| authentic | 4 — Sal 80B, b45a 80B, Cosmic, Phase 2 / 3.2 |
| corrupted copies | 2 — salt `bab585348552415f` |
| solver artifact | 1 — salt `696d736563757265` = ASCII `imsecure` |
| truncated first lines | 14 at 32B — still need re-extraction |

The `bab585348552415f` pair is a **mistyped paste of SalPhaseIon**: `+6` typed for
`86` and `/X` for `X`, which shifts every character after position 21. Its salt
differs from `3ab585348552415d` in only the first and last byte.

### Provenance of the hints

`in front of your eyes` is **not attributable to the creator** in this dump.
Every occurrence is `[Deleted Account]` quoting it. In Jrk's own messages the
phrase appears once, in a 2016 anecdote about the DAO — unrelated. The `key I's`
reading therefore rests on an unsourced quote.

Jrk's verified statements, in his own words:

1. *"We've seen prime numbers being mentioned; well, that is definitely an aspect
   which is required to proceed. Furthermore, along the way, some characters need
   to be 'zeroed out'."*
2. *"The previous 'there is another door hint' is still a thing. We're not sure if
   anyone has found another door so far, and we can't check that."*
3. *"Roses are White but often Red. Yellow has a number and so does Blue… the
   rabbits nest may contain a whole lot more."*
4. *"**Blueprint** is sort of the leading list at this point."*

**(2) is independent creator confirmation of the missing link.** It was derived
here from key-derivation failures alone — the 7-token XOR not producing
`6ac438fa…`, `WIF(K_S1)` not opening Cosmic — and the creator says outright that
an unfound door exists.

**(4) is worth a second look.** The community's `yellowblueprimes` may be a
mis-parse: Jrk says *Blueprint* is the leading list, and *"Yellow has a number and
so does Blue."* `yellow blue prime s` versus `yellow blueprint s` is one
space away.

## Round 17: BNCC-8B trit fractionation

The 2020 National Cipher Challenge Part 8B takes five Baudot characters as a
5×5 bit matrix, rotates it 90°, and reads the rows back. Since 9 = 3², the radix
analogue here is exact: one symbol is two trits, two symbols make a 2×2 trit
matrix, and the dihedral symmetries of that matrix are the transform family.
`trit.py` implements all eight, under both trit-significance conventions.

**Correction to the premise.** The construction was proposed as pairing `A[i]`
with `C[i]` for 91 aligned pairs and no leftover. partA is 91 symbols and
**partC is 570** — verified byte-identical to the page source in round 8. There
is no position-by-position alignment. Pairs are therefore taken within each run,
with `A×C[:91]`, `A×C[-91:]` and `A×C[::6][:91]` included as cross variants.

**Result:** 80 derived streams, each tried raw / SHA-256 / double-SHA-256 as a
password against the four authentic blobs under both KDFs. 1,440 decryptions,
**6 with valid padding against 5.6 expected by chance**, none containing a
decodable key. (Sanity: the identity operation reproduces partA exactly.)

### Why it had to come out this way

The dihedral transform is a **bijection on symbol pairs**, so it preserves total
entropy — measured deltas are +0.000 to +0.136 bits/symbol, i.e. nothing. The
round-16 bound therefore still binds after any rotation:

    partA:  91 × 2.882 =  262 bits into  36 bytes = 7.3 bits/byte
    partC: 570 × 3.120 = 1778 bits into 226 bytes = 7.9 bits/byte

English is ~1.5 bits/char. **No bijective transform of A or C — rotation,
transposition, permutation, base change — can decode to text, before or after
fractionation.** This is a general result, not a per-attempt failure, and it
retires the entire family in one step.

What it leaves standing: fractionation as a *stage* before a **lossy** operation.
Selection, zeroing and aggregation are the only things that can lower entropy,
and "some characters need to be zeroed out" is Jrk's authenticated wording.
The productive order is therefore transform → **then** zero, not transform alone.

## Round 18: fractionation × zeroing

The combined search — 80 dihedral-fractionated streams × 9 zeroing rules
(prime/composite position, prime/composite value, i→0, drop-i, none), decoded
with the block's convention and tried as passwords against the four authentic
blobs under both KDFs.

**5,184 decryptions, 22 padding-valid against ~20 expected by chance, zero real
hits.** Best lowercase decode 18.9% against a 10.2% random baseline.

That exhausts the productive order identified in round 17 (transform → then
zero) across every rule the creator's authenticated hint supports.

## Round 19: A/C as key material

`keyhunt.py` — the entropy bound rules out A/C bijectively decoding to *English*,
but says nothing against them decoding to a **key**: 32 bytes of AES key is
supposed to be ~8 bits/byte. Testing these runs for readable output was testing
for the wrong thing.

Direct key injection needs no IV guess for rejection: in CBC the final block
decrypts as `D(C_n) XOR C_{n-1}`, which never touches the IV, so the PKCS#7
oracle costs one AES block operation. Every digit assignment × every 32-byte
window of the decoded payload, against the three authentic blobs:
**15,225,840 key trials, 59,637 padding-valid against 59,476 expected by
chance.** Nothing.

That test was structurally weak, though, and the reason matters: **all four
blobs are open.** Their keys are known and none is an A/C decode, so no
A/C-derived key can ever validate against them. Every transform tested against
those blobs is hammering a door already ajar.

`prizehunt.py` — **written, not yet run.** The one test needing no locked door:
does A or C decode directly to the *prize private key*? Every digit assignment ×
every 32-byte window × both point serialisations, checked against the prize
HASH160 `a9553269572a317e39f0f518cb87c1a0ee1dbae4`, including the ELITE ±1
ternary-shift variants. With `coincurve` at ~26,000 keys/s, partA is ~3 minutes
and partC ~90. It is the literal reading of the creator's claim that everything
needed is on the page and that what you want is the private key — and it either
finds the key or closes "the key is stored in A/C" permanently.

### A note on 180° antisymmetry

`sum(p − q)` over a grid and its 180° rotation is **identically zero** for any
grid whatsoever — the rotation is an involution, so each pair contributes
`(x−y)` and `(y−x)`, which cancel. Likewise "1-cells whose partner is 0" is just
mismatches ÷ 2 by construction. Neither figure can distinguish the puzzle from
noise. The one informative number, the mismatch count on the 14×14 matrix, is
98 of 196 against **98.0 expected** for a random binary grid with 101 ones —
+0.01σ. Six random grids reproduce the whole pattern, including a random 7×13
that also gives exactly 80 mismatches, matching partA.
