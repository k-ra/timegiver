#THIS IS A WORK (MAJORLY) IN PROGRESS
#DON'T JUDGE
#PLEASE

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///timegiver.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def orgregister():
    """Temporary Homepage"""
    return render_template("temphome.html")


@app.route("/orgregister", methods=["GET", "POST"])
def orgregister():
    """Register Organization"""
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # blank field
        if not user:
            return apology("One or more fields are blank", 403)

        # username taken
        elif user == db.execute("SELECT username FROM users WHERE username = ?", user):
            return apology("Your username is taken", 403)

        # pass is empty
        elif not password:
            return apology("Please input a password", 403)

        # pass don't match
        elif password != confirm:
            return apology("Your passwords don't match", 403)

        # insert into thing
        else:
            db.execute("INSERT INTO orgs (user, hash) VALUES (?, ?)", user, generate_password_hash(password))
            session['user_id'] = user

            return redirect("/login")

    else:
        return render_template("orgregister.html")

@app.route("/orglogin", methods=["GET", "POST"])
def orglogin():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM orgs WHERE user = ?",
                          request.form.get("user"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

#personal touch
@app.route("/newthing", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        #import values
        opp_name = request.form.get("name")
        duration = request.form.get("duration")
        date = request.form.get("date")
        type = request.form.get("type")
        description = request.form.get("description")

        #check input
        if not (duration or opp_name or date):
            return apology("One or more required fields are blank")

        #probably check more things
            #TODO

        #add to table
        db.execute("""INSERT INTO openings
                          (org_id, name, duration, date, type, description)
                          VALUES
                          (?, ?, ?, ?, ?, ?)""", session["user_id"], opp_name, duration, date, type, description)
        return redirect("/")

    else:
        return render_template("addthing.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        #import values
        duration = request.form.get("duration")
        date = request.form.get("date")
    
        #check input
        if not duration :
            return apology("put in the time come on it's like the one thing you can do")

        #probably check more things
            #TODO

        #get things within that duration
        db.execute("SELECT id, org_id, name, description FROM openings WHERE duration < ?", duration)
    
        return redirect("/")

    else:
        return render_template("search.html")