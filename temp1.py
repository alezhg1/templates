def f(N):
    # binary representation without '0b'
    b = bin(N)[2:]
    if N % 2 == 0:          # even
        b = b + '10'
    else:                   # odd
        b = '1' + b + '00'
    return int(b, 2)

def find_min_N(limit=10**9):
    N = 1
    while True:
        if f(N) > 10**7:
            return N
        N += 1

print(find_min_N())