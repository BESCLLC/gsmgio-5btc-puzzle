"""Run the full candidate space against BOTH page blobs.

Until the page source arrived only the small SalPhaseIon blob was available, so
the Cosmic Duality blob (1328 bytes, 83 AES blocks) had never been swept here.
"""
import hashlib, itertools, sys
import candidates as C
import sweep as S
from pagehash import BLOBS

totals = {}

for bname, blob in BLOBS.items():
    print(f"\n######## blob: {bname} "
          f"({len(blob.ct)} bytes ciphertext, salt {blob.salt.hex()}) ########")
    hits = []

    def go(stream, label):
        hits.extend(S.run(stream, label, blob=blob))

    def seven_orderings():
        for msl in C.MATRIXSUM_VALUES:
            pool = [msl if t == "matrixsumlist" else t for t in C.SEVEN]
            for perm in itertools.permutations(pool):
                yield "".join(perm)

    def with_priors():
        for p in C.KNOWN_PRIOR:
            yield p
            for t in C.TOKENS + C.MATRIXSUM_VALUES:
                yield p + t
                yield t + p

    def xor_chains():
        for msl in C.MATRIXSUM_VALUES:
            pool = [msl if t == "matrixsumlist" else t for t in C.SEVEN]
            for k in range(2, len(pool) + 1):
                for combo in itertools.combinations(pool, k):
                    acc = bytes(32)
                    for t in combo:
                        acc = bytes(a ^ b for a, b in
                                    zip(acc, hashlib.sha256(t.encode()).digest()))
                    yield acc.hex()

    go(seven_orderings(), "7-token orderings x matrixsumlist readings")
    go(C.permutations_upto(C.TOKENS, 3), "token pool, ordered 1-3")
    go(C.permutations_upto(C.TOKENS, 4), "token pool, ordered 4")
    go(with_priors(), "prior-phase passwords +/- tokens")
    go(xor_chains(), "xor-chain of token sha256 digests (as password)")
    totals[bname] = len(hits)

print("\n" + "=" * 72)
for bname, n in totals.items():
    print(f"{bname}: {n} plausible plaintexts")
print("=" * 72)
