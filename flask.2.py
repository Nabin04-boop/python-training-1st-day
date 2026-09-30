# import flask
from flask import Flask, request
from flask import render_template

#initiate flask
app = Flask(__name__)

# define routes first of all default route as /
@app.route('/')
def home():
    return "Web development in python updated 123"

@app.route("/summit/<name>")
def summit(name):
    return f"Hello, {name}!"

@app.route("/add/<int:a>/<int:b>")
def add(a, b):
    return f"{a} + {b} = {a + b}"

@app.route("/sub/<int:a>/<int:b>")
def sub(a, b):
    return f"{a} - {b} = {a - b}"

@app.route("/template")
def template():
    return render_template("index.html", name="Nabin")

@app.route("/newtemplate")
def newtemplate():
    return render_template("page.html")

@app.route("/greet", methods = ["GET", "POST"])
def greet():
    if request.method == "POST":
        name = request.form["name"]
        return f"Hello, {name}!!"
    return render_template("form.html")

# run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
