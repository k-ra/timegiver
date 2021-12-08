#THIS IS A WORK (MAJORLY) IN PROGRESS
#DON'T JUDGE
#PLEASE

# comment

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
#from helpers import apology, keyword
from helpers import apology
import smtplib

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

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def home():
    """Temporary Homepage"""
    return render_template("home.html")

@app.route("/orgregister", methods=["GET", "POST"])
def orgregister():
    """Register Organization"""
    if request.method == "POST":
        user = request.form.get("user")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # Check for: blank fields
        if not (user or name) or not(password or confirm):
            return apology("One or more fields are blank", 403)

        # Taken usernames
        elif user == db.execute("SELECT user FROM orgs WHERE user = ?", user):
            return apology("Your username is taken", 403)

        # Mismatching passwords
        elif password != confirm:
            return apology("Your passwords don't match", 403)

        # Insert into organization database
        else:
            db.execute("INSERT INTO orgs (user, name, email, hash) VALUES (?, ?, ?, ?)", user, name, email, generate_password_hash(password))
            session["org_id"] = db.execute("SELECT * FROM orgs WHERE user = ?", user)[0]["org_id"]
            return redirect("/orgregmore")
    else:
        return render_template("orgreg.html")

@app.route("/orgregmore", methods=["GET", "POST"])
def orgregmore():
    """Edit organization info"""
    if request.method == "POST":
        address = request.form.get("address")
        description = request.form.get("description")
        online = request.form.get("online")

        # Check for blank fields
        if not description:
            return apology("One or more required fields are blank", 403)

        # Insert into orginfo
        else:
            db.execute("INSERT INTO orginfo (org_id, online, description) VALUES (?, ?, ?)", session["org_id"], online, description)
            if address:
                 db.execute("UPDATE orginfo SET location = ? WHERE org_id = ?", address, session["org_id"])
            return redirect("/orglogin")
    else:
        return render_template("orgregmore.html")

@app.route("/orglogin", methods=["GET", "POST"])
def orglogin():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("user"):
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
        session["org_id"] = rows[0]["org_id"]

        # Redirect user to home page
        return redirect("/postopp")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("orglogin.html")

@app.route("/userregister", methods=["GET", "POST"])
def userregister():
    """Register User"""
    if request.method == "POST":
        user = request.form.get("user")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # blank field
        if not (user or name) or not(password or confirm):
            return apology("One or more fields are blank", 403)

        # username taken
        elif user == db.execute("SELECT user FROM users WHERE user = ?", user):
            return apology("Your username is taken", 403)

        # pass don't match
        elif password != confirm:
            return apology("Your passwords don't match", 403)

        # insert into thing
        else:
            db.execute("INSERT INTO users (user, name, email, hash) VALUES (?, ?, ?, ?)", user, name, email, generate_password_hash(password))
            session["org_id"] = db.execute("SELECT * FROM users WHERE user = ?", user)[0]["user_id"]
            return redirect("/userlogin")
    else:
        return render_template("userreg.html")

@app.route("/userlogin", methods=["GET", "POST"])
def userlogin():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("user"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE user = ?",
                          request.form.get("user"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to search page
        return redirect("/search")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("userlogin.html")

#Add Posting
@app.route("/postopp", methods=["GET", "POST"])
def postopp():
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

        #add to table
        db.execute("""INSERT INTO openings
                          (org_id, name, duration, date, type, description)
                          VALUES
                          (?, ?, ?, ?, ?, ?)""", session["org_id"], opp_name, duration, date, type, description)
        return redirect("/allposts")

    else:
        return render_template("postopp.html")

#SEARCH FUNCTION
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        #import values
        duration = request.form.get("duration")
        type = request.form.get("type")
        #check input
        if not duration :
            return apology("put in the time come on it's like the one thing we need")

        
        if type:
            table = db.execute("SELECT name, type, description, date, duration, org_id, id FROM openings WHERE duration < ? AND type = ?", duration, type)
        else:
            table = db.execute("SELECT name, type, description, date, duration, org_id, id FROM openings WHERE duration < ?", duration)
        # replace org_id with the name in the table, so we can reduce bulk on the html side
        for i in range(len(table)):
            table[i]['org_id'] = db.execute("SELECT name FROM orgs WHERE org_id = ?", table[i]['org_id'])[0]['name']

        return render_template("results.html", table=table)

    else:
        return render_template("search.html")

@app.route("/upcoming", methods=["GET", "POST"])
def upcoming():
    """Show all upcoming events the user has registered for"""
    events = {}

    event_ids = db.execute("SELECT DISTINCT opening_id FROM signup WHERE user_id = ?", session["user_id"])

    #check each symbol for real-time price, add to portfolio
    for i in range(len(event_ids)):
        event_info = db.execute("SELECT org_id, name, date, description, duration FROM openings WHERE id = ?", event_ids[i]['opening_id'])
        orgname = db.execute("SELECT name FROM orgs WHERE org_id = ?", event_info[0]['org_id'])[0]['name']
        
        #add all to new dictionary
        events[i] = [event_info[0]["date"], event_info[0]["name"], event_info[0]["description"], orgname, event_info[0]["duration"]]

    return render_template("upcoming.html", events=events)

@app.route("/allposts", methods=["GET", "POST"])
def allposts():
    """Show all postings from the organization, and responses from the user"""
    responses = {}
    allevents = db.execute("SELECT opening_id FROM signup WHERE opening_id IN (SELECT id FROM openings WHERE org_id = ?)", session["org_id"])

    # for each event, check if there are responses. if yes then put in table.
    for i in range(len(allevents)):
        event_id = allevents[i]['opening_id']
        event = db.execute("SELECT name FROM openings WHERE id = ?", event_id)[0]['name']
        user_id = db.execute("SELECT DISTINCT user_id FROM signup WHERE opening_id = ?", event_id)[0]['user_id']
        user_info = db.execute("SELECT name, email FROM users WHERE user_id = ?", user_id)
        # add all to new responses dictionary
        responses[i] = [event, user_info[0]['name'], user_info[0]['email']]

    # load all events for separate table
    events = db.execute("SELECT id, date, name, type, description, duration FROM openings WHERE org_id = ?", session["org_id"])
    return render_template("allposts.html", events=events, responses = responses)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        table = db.execute("SELECT id FROM openings")
        selection = None
        for i in table:
            if request.form["button_clicked"] == str(i["id"]):
                selection = i["id"]
                db.execute("INSERT INTO signup (opening_id, user_id) VALUES (?, ?)", selection, session["user_id"])
                return redirect("/upcoming") 
        return redirect("/search")

if __name__ == "__main__":
    app.run()

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")