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
@app.route("/home_page")
def home_page():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("add_profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                        request.form.get("username")))
                        return redirect(url_for("dashboard", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))
    

@app.route("/profile", methods=["GET", "POST"])
def add_profile():
    if request.method == "POST":
        smoker = "yes" if request.form.get("smoker") else "no"
        profile = {
            "profile_name": request.form.get("profile_name"),
            "age": str(request.form['age']),
            "height": str(request.form['height']),
            "weight": int(request.form['weight']),
            "smoker": smoker,
            "username": session['user'],
            "my_intentions": none
        }
        mongo.db.profile_name.insert_one(profile)
        return redirect(url_for("dashboard"))
    return render_template("profile.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/my_profile/<username>", methods=["GET", "POST"])
def my_profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    users_profile = mongo.db.profile_name.find_one({'username': session['user']})
    return render_template("my_profile.html", users_profile=users_profile)


@app.route("/choose_intentions", methods=["GET", "POST"])
def choose_intentions():
    return render_template("choose_intentions.html")


@app.route("/exercise")
def exercise():
    exercises = mongo.db.exercise_intentions.find()
    print('EXERCISE: ', exercise)
    return render_template("exercise.html", exercises=exercises)

@app.route("/add_intention/", methods=["GET", "POST"])
def add_intention():
    if request.method == "POST":
        new_intention = {
            "action_name": mongo.db.exercise_intentions.find({ _id: {type: "objectId"}})
        }
        print()
        mongo.db.profile_name.insert_one(new_intention)
        flash("New Intention Added")
        return redirect(url_for("my_intentions"))
    return render_template("my_intentions.html")
    



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)