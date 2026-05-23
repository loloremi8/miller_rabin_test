# Miller-Rabin primality test

## Overview

**Miller-Rabin** is a probabilistic algorithm for testing if a number is prime.

## Mathematics behind Miller-Rabin

The Miller-Rabin test is based on two fundamental properties of prime numbers:

### Fermat's little theorem

If $p$ is prime and $a$ is not divisible by $p$, then:

$$a^{p-1} \equiv 1 \pmod{p}$$

### Non-trivial square roots of unity

In the field $\mathbb{Z}_p$ (where $p$ is prime), the equation $x^2 \equiv 1 \pmod{p}$ has exactly two solutions: $x \equiv 1$ and $x \equiv -1$. If we find a value $x$ such that $x^2 \equiv 1 \pmod{p}$, but $x \not\equiv 1$, then $n$ is guaranteed to be composite.

## Why Miller-Rabin Matters

#### Problem with Fermat's test:

Carmichael numbers like $561 = 3\cdot11\cdot17$ satisfy:
$$a^{n-1} \equiv 1 \pmod{n} \text{ for ALL bases } a$$

This fools Fermat's test into thinking they are prime, even though they're composite.

#### Miller-Rabin's Solution:

By checking the square root chain, Miller-Rabin catches Carmichael numbers reliably.

Example: Testing if $n=561$ is prime with witness $a=100$:

First, decompose: $560 = 2^4 \cdot 35$ (so $r=4, d=35$)

Compute the chain by repeatedly squaring:
- $100^{35} \equiv 298 \pmod{561}$
- $100^{70} \equiv 166 \pmod{561}$
- $100^{140} \equiv 67 \pmod{561}$
- $100^{280} \equiv 1 \pmod{561}$
- $100^{560} \equiv 1 \pmod{561}$

So the chain is $298 \to 166 \to 67 \to 1 \to 1$.

Miller-Rabin check: By the square root property, whenever we see a $1$ in the chain, the previous number must be $\pm 1 \pmod{n}$.

Here: $67 \not\equiv \pm 1 \pmod{561}$, but $67^2 \equiv 1 \pmod{561}$.

This is impossible if $561$ were prime. Therefore, $561$ is definitely copmosite.

## The algorithm

1. Represent $n-1$ as $2^r \cdot d$, where $d$ is odd.
2. Pick a random witness $a \in [2, n-2]$.
3. Compute $x=a^d \pmod{n}$
4. Check if $x \equiv 1$ or $x \equiv n-1 \pmod{n}$. If yes, $n$ passes this round.
5. Square $x$ repeatedly ($r-1$ times). At each step, if $x \equiv -1 \pmod{n}$, $n$ passes this round.
6. If neither condition is met, $n$ is definitely composite.
7. Repeat steps 2-6 with $k$ different random witnesses:
    - If ANY witness proves compositness $\Rightarrow$ return False (definite)
    - If ALL $k$ witness pass $\Rightarrow$ return True (probably prime, error $\leq 4^{-k}$)

## Code structure

### Core funcitons

- `fast_power(base, exp, mod)`: Binary exponentiation computing $\text{base}^{\text{exp}} \pmod{m}$ in $O(log \ exp)$ time.
- `decompose(n)`: Extracts powers of 2 from $n-1$, returning ($r,d$), where $n-1=2^r \cdot d$.
- `is_composite_witness(a, n, r, d)`: Tests if witness $a$ proves $n$ is composite. Returns True if definite, False if $n$ passes this round.
- `miller_rabin(n, k)`: Main function. Tests $n$ against $k$ random witnesses. Probability of false positive $\leq 4^{-k}$.

### Utility and analysis

- `find_prime_number(bits)`: A Monte Carlo function that generates random odd numbers and tests them until a propbable prime is found.
- `empirical_error_rate()`: Validates the algorithm against Carmichael numbers (e.g. 561, 1729), which are composite numbers that satisfy Fermat's little theorem for all bases.
- `benchmark_comparison()`: Measures the execution time of Miller-Rabin versus Trial division.

## Understanding $k$ (rounds)

$k$ is the number of random witnesses tested. More witnesses $=$ more confident.

| $k$ | Error bound | Meaning |
|-----|-------------|--------|
| $k=5$ | $\leq 1/1,024$ | ~$0.1\%$ chance composite is missed |
| $k=10$ | $\leq 1/1,000,000$ | 1 in a million chance | 
| $k=20$ | $\leq 10^{-12}$ | Cryptographic security level |

In practice: $k=20$ is standard for RSA key generation.

## Complexity comparison

| Algorithm | Complexity | Best case | Worst case |
|-----------|------------|-----------|------------|
| Trial Division | $O(\sqrt(n))$ | $n$ has small factors | $n$ is prime |
| Miller-Rabin | $O(k \cdot log^3(n))$ | $k=5$, small $n$ | $k=20$, large $n$ | 

For numbers $>32$ bits, Miller-Rabin is 100-500x faster.