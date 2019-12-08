import math
import sys

def get_digit(n, d):
    return math.floor(n / pow(10,d)) % 10

def is_valid(n, size):
    prev = get_digit(n, size-1)
    repeat_digit = None
    repeat_len = 0
    has_double = False
    for idx in reversed(range(0,size-1)):
        d = get_digit(n, idx)
        #print("{},{},{}".format(d, repeat_digit, repeat_len))
        if d < prev:
            return False
        if d == prev:
            if repeat_digit == None:
                repeat_digit = d
                repeat_len = 1
            elif repeat_digit == d:
                repeat_len += 1
        else:
            if repeat_len == 1:
                has_double = True
            repeat_digit = None
        prev = d
    if repeat_len == 1:
        has_double = True
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

def find_start(n, size):
    prev = get_digit(n, size-1)
    res = prev * pow(10, size-1)
    use_prev = False
    for idx in reversed(range(0,size-1)):
        d = get_digit(n, idx)
        if use_prev or d < prev:
            res += prev * pow(10,idx)
            use_prev = True
        else:
            res += d * pow(10,idx)
            prev = d
    return res

def test_range(first_number, last_number):
    count = 0
    n = find_start(first_number, 6)
    while n < last_number + 1:
        if is_valid(n, 6):
            count += 1
            print("{} yes".format(n))
        else:
            print(n)
        n = next_candidate(n)
    print("Count: {}".format(count))

test_range(int(sys.argv[1]), int(sys.argv[2]))
