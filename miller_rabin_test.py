import random
import time

# =========================== #
# CORE MILLER-RABIN ALGORITHM #
# =========================== #


def fast_power(base: int, exponent: int, modulus: int) -> int:
    """
    Computes (base ^ exponent) % modulus using binary (right to left) exponentiation
    At each step, if the current bit of exponent is set, multiply result by base, then square base and shift exponent right by one bit

    Time complexity ~ O(log exp)

    Input: base, exponent, modulus - non-negative integers, modulus > 1
    Output: (base ^ exponent) % modulus
    """
    result = 1
    base = base % modulus
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent //= 2
    return result


def decompose(n: int) -> tuple:
    """
    Writes n - 1 as 2^r * d, where d is odd

    Input: n - odd integer >= 3
    Output: (r, d) such that n - 1 = 2^r * d and d is odd
    """
    r = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        r += 1
    return r, d


def is_composite_witness(a: int, n: int, r: int, d: int) -> bool:
    """
    Tests whether "a" is a Miller-Rabin witness to the compositeness of n
    Given n - 1 = 2^r * d, d ood, computes a^d mod n, then repeatedly sqruares up to r - 1 times
    If neither 1 or n-1 appears at the right moment, n is definitelly composite

    Input: a - witness candidate (2 <= a <= n-2)
           n - number being tested
           r, d - from decompose(n): n - 1 = 2^r * d, d odo
    Output: True - if a proves n is composite, this is definitive
            False - if n passes this test, is a chance of being a prime
    """
    x = fast_power(a, d, n)

    if x == 1 or x == n - 1:
        return False

    for _ in range(r - 1):
        x = (x * x) % n
        if x == n - 1:
            return False

    return True  # a is a witness: n is definitelly composite


def miller_rabin(n: int, k: int = 20) -> int:
    """
    Miller-Rabin probabilistic primality test
    Tests n against k independently chosen random witnesses
    A composite number passes one round with probability at most 1/4, so the false-prime probability is at most 4^(-k)

    Input: n - integer to test
           k - number of round (default 20, error <= 4^-20 ~ 10^-12)

    Output: False - if n is definitely composite
            True - if n is probably prime
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    r, d = decompose(n)

    for _ in range(k):
        a = random.randint(2, n - 2)
        if is_composite_witness(a, n, r, d):
            return False

    return True


# ===================== #
# MONTE CARLO FUNCTIONS #
# ===================== #


def find_prime_number(bits: int, k: int = 20) -> int:
    """
    Generates a random prime with approximately 'bits' bits using Monte Carlo
    Repeatedly generates random odd numbers of the specified bit length and tets them with Miller-Rabin until one passes

    Input: bits - desired bit length (64, 128, etc.)
           k    - confidence parameter (error within <= 4^(-k))
    Output: A number n with 'bits' bits that is probably prime
    """
    while True:
        # generates random odd number with 'bits' bits
        n = random.getrandbits(bits)
        n |= 1 << (bits - 1)  # Set higher bit
        n |= 1  # Set lower bit - will be odd

        if miller_rabin(n, k):
            return n


def empirical_error_rate(composites: list[int], k_values: list[int]) -> None:
    """
    Empirically test Miller-Rabin's error rate on known composites
    For each k, run M-R 'trials' times on each composite
    Count how often it incorrectly says 'prime'

    Monte Carlo - we sample multiple runs ro estimate the true error rate

    Input: composites - list of know composite numbers
           k_values   - list of confidence parameters to test ([5, 10, 20], etc.)
    Output: prints a table of error rates
    """
    trials = 100

    print(
        f"{'k':<5} {'Error rate':<15} {'Errors':<10} {'/':<4} {'Trials':<10} {'Within bound':<5}"
    )
    print("-" * 70)

    for k in k_values:
        errors = 0
        for _ in range(trials):
            for composite in composites:
                if miller_rabin(composite, k):  # Wrongly says "prime"
                    errors += 1

        error_rate = errors / (trials * len(composites))
        bound = 4.0 ** (-k)
        within = "YES" if error_rate <= bound else "NO"

        print(f"{k:<5} {errors:<15} {error_rate:<15.2e} {bound:<15.2e} {within:<15}")


# ========================================= #
# BENCHMARK: MILLER-RABIN VS TRIAL DIVISION #
# ========================================= #


def trial_division(n: int) -> bool:
    """
    Simple trial division primality test for comparison of speed

    Time complexity ~ O(sqrt(n))

    Input: n - number to test
    Output: True if n is prime, False if composite
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2

    return True


def benchmark_comparison(test_numbers: list) -> None:
    """
    Compares runtime of M-R vs trial division

    Input: test_numbers - list of integers to test
    Output: Prints timing comparison table
    """
    print(
        f"\n{'Number':<12} {'Trial division (mics)':<22} {'Miller-Rabin (mics)':<20} {'Diffrence':<10}"
    )
    print("-" * 70)

    for n in test_numbers:
        # Trial division
        start = time.perf_counter()
        for _ in range(100):
            trial_division(n)
        td_time = (time.perf_counter() - start) * 10000  # Convert to microseconds

        # Miller-Rabin
        start = time.perf_counter()
        for _ in range(100):
            miller_rabin(n, k=20)
        mr_time = (time.perf_counter() - start) * 10000

        difference = td_time / mr_time if mr_time > 0 else float("inf")

        print(f"{n:<12} {td_time:<22.3f} {mr_time:<20.3f} {difference:.2f}x")


# ==== #
# MAIN #
# ==== #


def main() -> None:
    """
    Runs all functions
    """
    print("=" * 70)
    print("MILLER-RABIN PRIMALITY TEST")
    print("=" * 70)

    # FIRST CHECK
    print("\n1. Known values check")
    print("=" * 70)
    known_primes = [2, 3, 5, 7, 11, 97, 104729, 15485863]
    known_composites = [4, 9, 15, 100, 561, 1729]

    print("Testing known primes:")
    for p in known_primes:
        result = miller_rabin(p, k=20)
        status = "YES" if result else "NO"
        print(f"    {status}:  miller_rabin({p}) = {result}")

    print("\nTesting known composites:")
    for c in known_composites:
        result = miller_rabin(c, k=20)
        status = "YES" if not result else "NO"
        print(f"    {status}:  miller_rabin({c}) = {result}")

    # MONTE CARLO - Generate random primes
    print("\n" + "=" * 70)
    print("2. MONTE CARLO: Generate random primes")
    print("=" * 70)
    for bits in [8, 16, 32]:
        start = time.perf_counter()
        p = find_prime_number(bits, k=20)
        elapsed = time.perf_counter() - start
        print(f"    {bits}-bit prime: {p} (generated in {elapsed * 1000:.2f} ms)")

    # EMPIRICAL ERROR RATE
    print("\n" + "=" * 70)
    print("3. EMPIRICAL ERROR RATE")
    print("=" * 70)
    print("Testing against known composites: \n")
    composites = [561, 1105, 1729, 2465, 2821, 6601, 15841]
    empirical_error_rate(composites, k_values=[5, 10, 15, 20])

    # BENCHMARK: M-R vs T-D
    print("\n" + "=" * 70)
    print("4. BENCHMARK: Miller-Rabin vs Trial division")
    print("=" * 70)
    test_numbers_benchmarks = [104729, 1299709, 15485863]
    print("(100 tests per algorithm, time in microseconds)")
    benchmark_comparison(test_numbers_benchmarks)


if __name__ == "__main__":
    main()