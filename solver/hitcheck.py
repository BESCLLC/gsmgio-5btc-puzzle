"""What counts as a hit, and what does not.

Three sweeps in this investigation have now been sunk by validators that either
reject the right answer or accept noise. The rules that survive contact:

WORTHLESS as a signal
  - a 2-byte prefix test ("does it start 5J/5K/5H"). False-positive rate
    3/65536 = 1 in 21,845. At sweep scale, hits are guaranteed. Demonstrated by
    manufacturing them from random passwords.
  - printability / word counts / base58 ratio, when the payload is key material.
    The verified Cosmic plaintext scores printable 0.40, words 0, base58 0.24 --
    every readability filter REJECTS the correct answer.

SOUND
  - valid PKCS#7 padding: cheap, kills 255/256, necessary but not sufficient.
  - a known plaintext hash: decisive when one exists.
  - a full WIF/hex key decode that survives base58check, not a prefix.
  - HASH160 of the derived pubkey against the target: the only thing that ends it.
"""
import hashlib
import validate

PRIZE_H160 = "a9553269572a317e39f0f518cb87c1a0ee1dbae4"
KNOWN = {
    "1449a2178eea7c0e3fabac8c1ad2afa294be4fc1800c594a025a056e88c626bf": "SalPhaseIon 79B",
    "4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081": "Cosmic 1327B",
}


def verdict(pt, padding_was_valid):
    """-> (is_real_hit, reason)"""
    if not padding_was_valid:
        return False, "padding invalid -- wrong key, regardless of how it starts"
    h = hashlib.sha256(pt).hexdigest()
    if h in KNOWN:
        return True, f"matches known plaintext: {KNOWN[h]}"
    keys = validate.keys_in(pt)
    if not keys:
        return False, "valid padding but no decodable key inside"
    for k in keys:
        for a in validate.addresses(k):
            if a in validate.PRIZE:
                return True, f"PRIZE: {a}"
    return False, f"{len(keys)} decodable key(s), none reaching the prize"
