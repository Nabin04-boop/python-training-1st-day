#1.  creation of types
fruits = ("apple", "banana", "cherry")
single = (10,)
mixed = ("prajwol", 25, "developr")
#2. accessing & stiching
print(fruits[0],fruits[-1])
print(fruits[0:2])
#3. unpacking
name, age, role = mixed
print(f"{name} is {age} as {role}")
#4. opertaing & methods
nums= (4,2,3,2)
print("count of 2 ", nums.count(2))
combined = fruits + ("mango",)
print("total items:", len(combined))
#5. nested tuples
nested = ("point",(3,4))
print("x:", nested[1][0])