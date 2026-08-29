"""Systematic sweep of the SalPhaseIon end-game blob.

The blob is 96 bytes: OpenSSL magic + salt + 80 bytes = 5 AES blocks, i.e. a
plaintext of 65..80 bytes. A 64-character hex private key pads to exactly 80,
which is what we are hoping to find.
"""
import hashlib, itertools, sys
import candidates as C
from sweep import run
from gsmg import Blob, SALPHASEION_B64

BLOB = Blob(SALPHASEION_B64)
all_hits = []


def sweep(stream, label):
    all_hits.extend(run(stream, label))


# --- 1. the seven tokens the page spells out, every ordering, every reading of
#        "matrixsumlist" ------------------------------------------------------
def seven_orderings():
    for msl in C.MATRIXSUM_VALUES:
        pool = [msl if t == "matrixsumlist" else t for t in C.SEVEN]
        for perm in itertools.permutations(pool):
            yield "".join(perm)


sweep(seven_orderings(), "7-token orderings x matrixsumlist readings")

# --- 2. shorter ordered combinations from the wider token pool ---------------
sweep(C.permutations_upto(C.TOKENS, 3), "token pool, ordered 1-3")
sweep(C.permutations_upto(C.TOKENS, 4), "token pool, ordered 4")

# --- 3. prior-phase passwords, alone and glued to each token ------------------
def with_priors():
    for p in C.KNOWN_PRIOR:
        yield p
        for t in C.TOKENS + C.MATRIXSUM_VALUES:
            yield p + t
            yield t + p


sweep(with_priors(), "prior-phase passwords +/- tokens")

# --- 4. XOR chains of the token hashes ---------------------------------------
#     (the "xor the sha256 of each token" construction that gets proposed a lot)
def xor_chains():
    for msl in C.MATRIXSUM_VALUES:
        pool = [msl if t == "matrixsumlist" else t for t in C.SEVEN]
        for k in range(2, len(pool) + 1):
            for combo in itertools.combinations(pool, k):
                acc = bytes(32)
                for t in combo:
                    h = hashlib.sha256(t.encode()).digest()
                    acc = bytes(a ^ b for a, b in zip(acc, h))
                yield acc.hex()


sweep(xor_chains(), "xor-chain of token sha256 digests (as password)")

# --- 5. the same XOR chains injected directly as the AES key -----------------
def key_injection():
    n = hits = 0
    for msl in C.MATRIXSUM_VALUES:
        pool = [msl if t == "matrixsumlist" else t for t in C.SEVEN]
        for k in range(1, len(pool) + 1):
            for combo in itertools.combinations(pool, k):
                acc = bytes(32)
                for t in combo:
                    acc = bytes(a ^ b for a, b in
                                zip(acc, hashlib.sha256(t.encode()).digest()))
                for iv in (bytes(16), BLOB.salt * 2, acc[:16], acc[16:]):
                    n += 1
                    pt = BLOB.check_key(acc, iv)
                    if pt and all(0x20 <= b < 0x7f or b in (9, 10, 13) for b in pt):
                        hits += 1
                        print(f"  !!! KEY HIT combo={combo} iv={iv.hex()} -> {pt!r}")
    print(f"[direct key injection] {n:,} decryptions | {hits} plausible plaintexts")


key_injection()

print()
print("=" * 72)
print(f"TOTAL plausible plaintexts across all sweeps: {len(all_hits)}")
print("=" * 72)
