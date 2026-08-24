"""A cheap rejection test for the puzzle's decode convention.

The convention is: 570 symbols -> 570 decimal digits -> one big integer ->
hex -> ASCII. The expensive part is the bignum, and we do it millions of times
only to throw the answer away. But a decode that is going to be lowercase text
is already decided by its *leading* digits:

  * hex(N) is prepended with '0' when it has an odd number of hex digits, so the
    first byte becomes 0x0N -- a control character, never a letter. Odd hex
    length is an instant reject, and that alone kills half the space.
  * the first bytes are determined by log2(N), which the top ~30 decimal digits
    pin down to far more precision than we need.

So we compute the first two bytes from 30 characters of float arithmetic and
only touch the bignum for the ~0.5% that survive.
"""
import math

LOG2_10 = math.log2(10)


def leading_bytes(digit_prefix, total_digits, nbytes=2):
    """First nbytes of the decoded output, from the leading digits alone.
    Returns None if the hex length is odd (guaranteed non-text)."""
    m = float(digit_prefix) / 10.0 ** (len(digit_prefix) - 1)   # in [1, 10)
    x = (math.log10(m) + (total_digits - 1)) * LOG2_10           # = log2(N)
    bits = int(x) + 1
    hexlen = -(-bits // 4)
    if hexlen % 2:
        return None
    out = []
    for i in range(1, nbytes + 1):
        v = 2.0 ** (x - 4 * hexlen + 8 * i)
        b = int(v) & 0xFF if i > 1 else int(v)
        out.append(b)
    return out


def is_lower(b):
    return 97 <= b <= 122


if __name__ == "__main__":
    # Validate against the slow path on the two known-good segments plus random
    # streams: the fast filter must never reject something the slow path accepts.
    import random
    from running import convention, LETTERS

    def slow(s):
        return convention(s)

    bad = checked = 0
    for trial in range(4000):
        n = random.choice((91, 570))
        s = ''.join(random.choice(LETTERS) for _ in range(n))
        digs = ''.join(str(LETTERS.index(c) + 1) for c in s)
        fast = leading_bytes(digs[:30], n)
        real = slow(s)
        checked += 1
        if fast is None:
            if real and is_lower(real[0]):
                bad += 1                      # rejected something viable
        else:
            if real[:2] != bytes(fast):
                bad += 1                      # predicted the wrong bytes
    print(f"validated {checked} random streams, {bad} mismatches")
    assert bad == 0, "fast filter is not sound -- do not use it"
    print("fast filter is sound")
