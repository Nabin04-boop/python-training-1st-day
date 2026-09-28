class Student:
    def __init__(self, name):
       self.name = name 
    def greet(self):
        return f" Hi, I am {self.name}"
s1 = Student("Nabin Rai")
print (s1.greet())
