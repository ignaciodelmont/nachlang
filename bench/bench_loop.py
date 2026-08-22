# Benchmark 2: Iterative loop with an accumulator
# Measures: tight loop performance, arithmetic, variable mutation
# 100 million iterations summing into an accumulator

sum = 0
i = 0
while i < 100000000:
    sum = sum + i
    i = i + 1
print(sum)
