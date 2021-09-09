import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def home():
    categories = list(mongo.db.categories.find())
    return render_template("home.html", categories = categories)


@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        # check if user already exsists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        # check if password matched the confirm password entry
        password = request.form.get("password")
        confirm_password = request.form.get("password-confirm")

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))
        elif password != confirm_password:
            flash("Your password and confirmation do not match")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        # enter the new user to the users collection
        mongo.db.users.insert_one(register)
        flash("Registration Successful")

    return render_template("register.html")


@app.route("/login", methods = ["GET", "POST"])
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(host = os.environ.get("IP"),
            port = int(os.environ.get("PORT")),
            debug = True)
