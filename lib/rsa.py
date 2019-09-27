import math
import random


def fastPow(n, d, mod):
    res = 1
    while (d):
        if (d & 1):
            res *= n
            res %= mod
        n *= n
        n %= mod
        d >>= 1
    return res


def isPrime(num, test_count=10):
    for _ in range(test_count):
        rnd = random.randint(1, num - 1)
        if (fastPow(rnd, (num - 1), num) != 1):
            return False
    return True


def generatePrime(bit=128):
    candidate = random.randint(1 << (bit - 1), (1 << bit) - 1)
    while not isPrime(candidate):
        candidate = random.randint(1 << (bit - 1), (1 << bit) - 1)
    return candidate


def gcd(a, b):
    while (a > 0 and b > 0):
        if (a > b):
            a %= b
        else:
            b %= a
    return max(a, b)



def gcdex(a, b):
    if b == 0:
        return a, 1, 0
    else:
        d, x, y = gcdex(b, a % b)
        return d, y, x - y * (a // b)


def lcm(a, b):
    return a * b // gcd(a, b)


def generatePublic(n):
    candidate = random.randint(1, n - 1)
    while (gcd(n, candidate) != 1):
        candidate = random.randint(2, n - 1)
    return candidate


def generatePrivate(e, mod):
    _, x, _ = gcdex(e, mod)
    return (x % mod + mod) % mod


def rsa(BIT_COUNT=256):
    p, q = generatePrime(), generatePrime()
    n = p * q
    totient = lcm((p - 1), (q - 1))
    e = generatePublic(totient)
    r = generatePrivate(e, totient)
    return {"public": e, "private": r, "module": n}

def hashOfString(message):
    result = 0
    for i in range(len(message)):
        result += ord(message[i])
        result *= 256
    return result

def stringFromHash(message):
    result = ""
    while (message):
        result += chr(message % 256)
        message //= 256
    return result[::-1]

def encrypt(message, public, module):
    return hex(fastPow(hashOfString(message), public, module))

def decrypt(message, private, module):
    return stringFromHash(fastPow(int(message, 0), private, module))
