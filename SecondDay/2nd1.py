def ask_question(question):
   msg = input(question + "")
   return msg
name = ask_question("What is your name??")
print("Hello!!", name)