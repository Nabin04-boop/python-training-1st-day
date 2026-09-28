class Fruit:
    def __init__(self, name):
       self.name = name 

    def describe(self):
        return f"This fruit is called {self.name}"
    

f1 = Fruit("kiwi")
f2 = Fruit("mango")


print(f1.describe())
print(f2.describe())
