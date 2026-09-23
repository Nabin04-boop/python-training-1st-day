#1. Defined Helpers Function
def check_even_odd(n):
    return "even" if n % 2 == 0 else "odd"
#2. Loop & count aggregates
number = [4, 7, 10, 13, 18, 21 ]
evens, odds= 0, 0
for num in number:
    result = check_even_odd(num)
    print(f"{num} is {result}")
    if result == "even": evens +=1 
    else: odds += 1