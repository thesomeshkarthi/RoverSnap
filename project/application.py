import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, nasa

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///roversnap.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show portfolio of stocks"""

    if request.method == "POST":
        userId = session["user_id"]
        rows = db.execute("SELECT username FROM users WHERE id = ?", userId)
        username = rows[0]["username"]
        db.execute("DELETE FROM ? WHERE id > 0", username)
        rover = request.form.get("rover")

        if rover == "Curiosity":
            cur = "selected"
            opp = None
            spi = None

        elif rover == "Spirit":
            cur = None
            opp = None
            spi = "selected"

        elif rover == "Opportunity":
            cur = None
            opp = "selected"
            spi = None

        if not request.form.get("date"):
            flash("Must provide valid date")
            return render_template("index.html", cur=cur, opp=opp, spi=spi)

        date = request.form.get("date")

        quote = nasa(rover, date)

        if len(quote["photos"]) == 0:
            flash("No photos taken on this date")
            return render_template("index.html", cur=cur, opp=opp, spi=spi, date=date)

        for capture in quote["photos"]:
            image = capture["img_src"]
            sol = capture["sol"]
            camera = capture["camera"]["name"]
            db.execute("INSERT INTO ? (image, sol, camera, date, rover) VALUES (?, ?, ?, ?, ?)", username, image, sol, camera, date, rover)

        query = db.execute("SELECT * FROM ?", username)

        return render_template("index.html", cur=cur, opp=opp, spi=spi, date=date, query=query)
    else:
        # Save all useful information in variables
        userId = session["user_id"]
        return render_template("index.html")


@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":
        userId = session["user_id"]
        rows = db.execute("SELECT username FROM users WHERE id = ?", userId)
        username = rows[0]["username"]
        image = request.form.get("image")
        rover = request.form.get("rover")
        capturedate = request.form.get("date")
        camera = request.form.get("camera")
        sol = request.form.get("sol")
        currentdate = datetime.today().strftime('%Y-%m-%d')

        if not request.form.get("title"):
            title = str("Capture from " + currentdate)
        else:
            title = request.form.get("title")

        if not request.form.get("caption"):
            caption = "Image retrieved through NASA API"
        else:
            caption = request.form.get("caption")

        db.execute("INSERT INTO scrapbook (username, userid, image, sol, camera, currentdate, capturedate, rover, title, caption) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", username, userId, image, sol, camera, currentdate, capturedate, rover, title, caption)

        return '', 204
    else:
        return '', 204


@app.route("/update", methods=["GET", "POST"])
def update():

    if request.method == "POST":

        photoId = request.form.get("id")
        currentdate = datetime.today().strftime('%Y-%m-%d')

        if not request.form.get("title"):
            title = str("Capture from " + currentdate)
        else:
            title = request.form.get("title")

        if not request.form.get("caption"):
            caption = "Image retrieved through NASA API"
        else:
            caption = request.form.get("caption")

        db.execute("UPDATE scrapbook SET title = ?, caption = ? WHERE id = ?", title, caption, photoId)

        return '', 204
    else:
        return '', 204


@app.route("/delete", methods=["GET", "POST"])
def delete():

    if request.method == "POST":
        photoid = request.form.get("id")
        db.execute("DELETE FROM scrapbook WHERE id = ?", photoid)
        flash("Deleted successfully.", "success")
        return redirect("/scrapbook")
    else:
        return redirect("/scrapbook")


@app.route("/scrapbook", methods=["GET", "POST"])
@login_required
def scrapbook():

    if request.method == "POST":

        if not request.form.get("username"):
            userdisplay = "My"
            view = request.form.get("view")
            switch = request.form.get("switch")


            if switch == "yes":
                if view == "GALLERY":
                    view = "CLASSIC"
                else:
                    view = "GALLERY"


            userId = session["user_id"]
            status = "disabled"

            if view == "CLASSIC":
                gallery = db.execute("SELECT * FROM scrapbook WHERE userid = ? ORDER BY id DESC", userId)
                return render_template("scrapbook.html", userdisplay=userdisplay, gallery=gallery, status=status, view=view)

            query = db.execute("SELECT * FROM scrapbook WHERE userid = ? ORDER BY id DESC", userId)
            return render_template("scrapbook.html", userdisplay=userdisplay, query=query, status=status, view=view)

        username = request.form.get("username").lower().strip()

        userId = session["user_id"]
        rows = db.execute("SELECT username FROM users WHERE id = ?", userId)
        checkusername = rows[0]["username"]

        if username == checkusername:
            userdisplay = "My"
            view = request.form.get("view")
            switch = request.form.get("switch")


            if switch == "yes":
                if view == "GALLERY":
                    view = "CLASSIC"
                else:
                    view = "GALLERY"


            userId = session["user_id"]
            status = "disabled"

            if view == "CLASSIC":
                gallery = db.execute("SELECT * FROM scrapbook WHERE userid = ? ORDER BY id DESC", userId)
                return render_template("scrapbook.html", userdisplay=userdisplay, gallery=gallery, status=status, view=view)

            query = db.execute("SELECT * FROM scrapbook WHERE userid = ? ORDER BY id DESC", userId)
            return render_template("scrapbook.html", userdisplay=userdisplay, query=query, status=status, view=view)


        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) == 0:
            flash("User does not exist.", "danger")
            return redirect("/scrapbook")

        userdisplay = username[0].upper() + username[1:].lower() + "'s"

        view = request.form.get("view")
        status = ""
        switch = request.form.get("switch")

        if switch == "yes":
            if view == "GALLERY":
                view = "CLASSIC"
            else:
                view = "GALLERY"


        if view == "CLASSIC":
            gallery = db.execute("SELECT * FROM scrapbook WHERE username = ? ORDER BY id DESC", username)
            return render_template("scrapbook.html", username=username, userdisplay=userdisplay, gallery=gallery, status=status, view=view)
        else:
            userLoad = db.execute("SELECT * FROM scrapbook WHERE username = ? ORDER BY id DESC", username)
            return render_template("scrapbook.html", username=username, userdisplay=userdisplay, userLoad=userLoad, status=status, view=view)

    else:
        userdisplay = "My"
        view = "GALLERY"
        userId = session["user_id"]
        query = db.execute("SELECT * FROM scrapbook WHERE userid = ? ORDER BY id DESC", userId)
        status = "disabled"
        return render_template("scrapbook.html", userdisplay=userdisplay, query=query, status=status, view=view)



@app.route("/about", methods=["GET", "POST"])
@login_required
def about():
    return render_template("about.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    #Store Flash message if exists and clear session information
    if session.get("_flashes"):
        flashes = session.get("_flashes")
        session.clear()
        session["_flashes"] = flashes
    else:
        session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username.", "danger")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password.", "danger")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Incorrect username and/or password.", "danger")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    flash("Logged out successfully.", "success")

    if session.get("_flashes"):
        flashes = session.get("_flashes")
        session.clear()
        session["_flashes"] = flashes
    else:
        session.clear()

    # Redirect user to login form
    return redirect("/login")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # If form was submitted, following code is executed
    if request.method == "POST":
        # Check to see if username is not empty
        if not request.form.get("username"):
            flash("Must provide username.")
            return redirect("/register")

        # Check to see if password is not empty
        if not request.form.get("password"):
            flash("Must provide password.")
            return redirect("/register")

        if len(request.form.get("password")) < 5:
            flash("Password must be over 5 characters long.")
            return redirect("/register")

        username = request.form.get("username").lower().strip()
        password = request.form.get("password")
        capitalExists = "False"

        for i in range(len(password)):
            if ord(password[i]) > 64 and ord(password[i]) < 91:
                capitalExists = "True"

        if capitalExists == "False":
            flash("Password must include at least 1 capital letter")
            return redirect("/register")

        validUsername = "True"

        for i in range(len(username)):
            if ord(username[i]) < 48:
                validUsername = "False"
            elif ord(username[i]) > 57 and ord(username[i]) < 97:
                validUsername = "False"
            elif ord(username[i]) > 122:
                validUsername = "False"

        if validUsername != "True":
            flash("Username must only contain numbers and letters")
            return redirect("/register")

        # Check to see if confirmation is not empty and confirmation is equal to the password
        if not request.form.get("confirmation") or request.form.get("confirmation") != request.form.get("password"):
            flash("Passwords do not match.")
            return redirect("/register")

        # Check to see if username exists in database and store in rows
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # If a row is found, display error as username was found and already exists
        if len(rows) != 0:
            flash("Username already exists.")
            return redirect("/register")

        # Hash password and store in new variable
        hashedpassword = generate_password_hash(request.form.get("password"))

        # Insert new hash and password into database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hashedpassword)

        db.execute("CREATE TABLE ? (id INTEGER, image TEXT NOT NULL, sol TEXT NOT NULL, camera TEXT NOT NULL, date TEXT NOT NULL, rover TEXT NOT NULL, PRIMARY KEY(id))", username)

        #Flash message success on login page
        flash("Registration successful! Login to proceed.", "success")

        # Redirect to login to login with new username and password
        return redirect("/login")

    # If initially redirected with no form, load the register.html form
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
