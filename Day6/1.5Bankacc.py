class BankAccount:
    def __init__ (self):
        self.balance = 0
    def deposit(self, amount):
        self.balance += amount
    def withdraw(self, amount):
      if amount>self.balance:
        print("ERROR: Insufficient funds!!!")
      else:
        self.balance -= amount
    def check_balance(self):
       print(self.balance)

acc = BankAccount()
acc.deposit(10000)
acc.withdraw(12000)
acc.check_balance()
