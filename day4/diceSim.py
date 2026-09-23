import math, random
roll1 = random.randint(1,6)
roll2 = random.randint(1,6)
print(f'Roll 1; {roll1} | Roll2; {roll2}')
total_sum = roll1 + roll2
root_value = math.sqrt(total_sum)
print(f"square root: {root_value:.4f}")
