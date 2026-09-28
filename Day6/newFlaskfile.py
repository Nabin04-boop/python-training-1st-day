from flask import Flask 
app= Flask(__name__)
@app.route("/")
def home():
    return "Hello World!!"

@app.route("/greet/<name>")
def greet(name):
    return "Hello, {name}!! "

@app.route("/add/<int:a>/<int:b>")
def add(a, b):
    return f"{a} + {b} = {a + b}"

@app.route("/sub/<int:c>/<int:d>")
def add(c, d):
    return f"{c} - {d} = {c - d}"

if __name__=="__main__":
    app.run(debug=True)