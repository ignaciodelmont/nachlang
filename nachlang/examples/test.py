# counter = 1

# while counter < 100000000:
#     counter = counter + 1

# print(counter)

def fib(n):
    if n == 0 or n == 1:
        return 1
    
    a = 1
    b = 1
    i = 2

    res = 0

    while i <= n:
        res = a + b
        a = b
        b = res
        i = i + 1

    return res

print(fib(70))
