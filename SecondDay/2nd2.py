numbers = (4, 7, 10, 13, 18, 21)
total_odd = 0
total_even = 0
for num in numbers:
   if num % 2 == 0:
     print(num, "is Even num!")
     total_even += 1
   else:
      print(num, "is Odd num!")
      total_odd += 1
print("The total Even Number:", total_even)
print("The toatl Odd Number", total_odd)
        