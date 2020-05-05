import os

from flask import Flask, session, request, render_template, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



@app.route("/")
@login_required

#homepage
def index():
	return render_template("index.html")

#login page
@app.route("/login", methods=["GET", "POST"])
def login():

	session.clear()
	username = request.form.get("username")

	#if the method is post (by submitting the form)
	if request.method =="POST":

		#if username field is empty
		if not request.form.get("username"):
			return render_template("error.html", message="Enter your username!")

		#if password field is empty
		if not request.form.get("password"):
			return render_template("error.html", message="Enter your password!")

		#Query db for username
		rows = db.execute("SELECT * FROM users WHERE username = :username",
                {"username": username})
        
        result = rows.fetchone()

        #Ensure username exists and password is same
        if not result or not result[2]== request.form.get("password"):
        	return render_template("error.html", message="Wrong username or password")

        #allot the user a session
        session.["user_id"] = result[0]
        session.["user_name"] = result[1]

        #redirect to homepage
        return redirect("/")

    #if the method is GET(the user didn't submit the login form)
	else:
		return render_template("login.html")

#logout page
@app.route("/logout")
def logout():
	session.clear()

	#redirect user to the login page
	return redirect("/")

#registration page
@app.route("/registration", methods=["GET", "POST"])
def registration():

	session.clear()

	#if the user submits the form(via POST)
	if request.method == "POST":

		#Ensure username was submitted
		if not request.form.get("username"):
			return render_template("error.html",message="oops! your forgot to provide a username")

		#Query databse for username
		userCheck = db.execute("SELECT * from users WHERE username=:username",{"username":request.form.get("username")})

		#check if username already exists
		if userCheck is not None:
			return render_template("error.html", message="oops! username already exists")

		#check if password is provided
		if not request.form.get("password"):
			return render_template("error.html", message="You MUST provide password! Duh!")

		#ensure confirmation was submitted
		if not request.form.get("confirmation"):
			return render_template("error.html", message="You MUST confirm the password! FOOl!")

		#ensure the provided passwords are same
		if not request.form.get("password") == request.form.get("confirmation"):
			return render_template("error.html", message="Password is not same!")

		#insert user into DB
		db.execute("INSERT into users (username, password) values (:username, :password)",
			{"username":request.form.get("username"), "password":request.form.get("password")})

		#commit changes to databse
		db.commit()

		flash('Account created', 'info')

		#redirect to the login page
		return redirect("/login")

	#if the user reached the route via GET
	else:
		return render_template("registration.html")