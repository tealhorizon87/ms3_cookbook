import os
from datetime import datetime
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
    recipes = list(mongo.db.recipes.find(
        {"is_private": "off"}).sort("date_created", -1).limit(20))
    return render_template("home.html", recipes = recipes)


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
            "email": request.form.get("email"),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        # enter the new user to the users collection
        mongo.db.users.insert_one(register)
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful")
        return redirect(url_for("profile", username = session["user"]))


    return render_template("register.html")


@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        # check if user already exsists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # check password is correct
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    # Add user to session cookies
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome back, {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "profile", username = session["user"]))
            else:
                flash("Incorrect uername and/or password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods = ["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        recipes = list(mongo.db.recipes.find({"created_by": session["user"]}))
        return render_template("profile.html", username = username, recipes = recipes)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("home"))


@app.route("/recipe/<recipe_id>", methods = ["GET", "POST"])
def recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipe.html", recipe = recipe)


@app.route("/add_recipe", methods = ["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        is_private = "on" if request.form.get("is_private") else "off"
        recipe = {
            "recipe_title": request.form.get("title"),
            "category_name": request.form.get("category_name"),
            "recipe_description": request.form.get("description"),
            "difficulty": request.form.get("difficulty"),
            "is_private": is_private,
            "servings": request.form.get("servings"),
            "prep_time": request.form.get("prep-time"),
            "cook_time": request.form.get("cook-time"),
            "dietary_requirements": request.form.get("diet"),
            "allergens": request.form.get("allergens").split("*"),
            "ingredients": request.form.get("ingredients").split("*"),
            "steps": request.form.get("steps").split("*"),
            "created_by": session["user"],
            "date_created": datetime.now()
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe successfully uploaded!")
        return redirect(url_for("home"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    diets = mongo.db.diet.find().sort("diet_name", 1)
    return render_template(
        "add-recipe.html", categories = categories, diets = diets)


@app.route("/edit_recipe/<recipe_id>", methods = ["GET", "POST"])
def edit_recipe(recipe_id):
    if request.method == "POST":
        is_private = "on" if request.form.get("is_private") else "off"
        submit = {
            "recipe_title": request.form.get("title"),
            "category_name": request.form.get("category_name"),
            "recipe_description": request.form.get("description"),
            "difficulty": request.form.get("difficulty"),
            "is_private": is_private,
            "servings": request.form.get("servings"),
            "prep_time": request.form.get("prep-time"),
            "cook_time": request.form.get("cook-time"),
            "dietary_requirements": request.form.get("diet"),
            "allergens": request.form.get("allergens").split("*"),
            "ingredients": request.form.get("ingredients").split("*"),
            "steps": request.form.get("steps").split("*"),
            "created_by": session["user"],
            "date_created": datetime.now()
        }
        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, submit)
        flash("Recipe updated")
        return redirect(url_for("profile", username = session['user']))

    categories = mongo.db.categories.find().sort("category_name", 1)
    diets = mongo.db.diet.find().sort("diet_name", 1)
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    allergens = '*'.join(recipe["allergens"])
    ingredients = '*'.join(recipe["ingredients"])
    steps = '*'.join(recipe["steps"])
    return render_template("edit-recipe.html",
        recipe = recipe, diets = diets, categories = categories,
        allergens = allergens, ingredients = ingredients, steps = steps)


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("profile", username = session['user']))


@app.route("/search", methods = ["GET", "POST"])
def search():
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find(
        {"is_private": "off", "$text": {"$search": query}}))
    if recipes:
        return render_template("home.html", recipes = recipes)
    else:
        flash("No results found")
        return redirect(url_for("home"))

    
if __name__ == "__main__":
    app.run(host = os.environ.get("IP"),
            port = int(os.environ.get("PORT")),
            debug = True)
