# Benchmark 3: Heavy object creation
# Measures: allocator pressure (Python uses refcounting + GC)
# 10 million iterations

result = 0
i = 0
while i < 10000000:
    result = (i * 2) + 1
    i = i + 1
print(result)
