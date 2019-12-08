import math
import sys

def get_digit(n, d):
    return math.floor(n / pow(10,d)) % 10

def is_valid(n):
    prev = get_digit(n, 5)
    has_double = False
    for idx in reversed(range(0,5)):
        d = get_digit(n, idx)
        if d < prev:
            return False
        if d == prev:
            has_double = True
        prev = d
    return has_double

def next_candidate(n):
    res = 0
    d = get_digit(n, 0)
    if d + 1 > 9:
        high = next_candidate(math.floor(n/10))
        res = get_digit(high,0) + high * 10
    else:
        res = d + 1 + math.floor(n/10) * 10
    return res

def test_range(first_number, last_number):
    count = 0
    n = first_number
    while n < last_number + 1:
        if is_valid(n):
            count += 1
            #print(n)
        n = next_candidate(n)
    print("Count: {}".format(count))

test_range(int(sys.argv[1]), int(sys.argv[2]))
