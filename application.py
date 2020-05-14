import os, json

from flask import Flask, session, request, render_template, redirect, flash
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
def index():
	return render_template("registration.html")

#login page
@app.route("/login", methods=["GET", "POST"])
def login():

	session.clear()

	#if the method is post (by submitting the form)
	if request.method =="POST":
		lu = request.form.get("login-username")
		lp = request.form.get("login-password")

		#if username field is empty
		if not lu:
			return render_template("error.html", message="Enter your username!")

		#if password field is empty
		if not lp:
			return render_template("error.html", message="Enter your password!")

		#Query db for username
		rows = db.execute("SELECT * FROM users WHERE username = :a", {"a": lu})
		result = rows.fetchone()

		if result:
			if result.username == lu and result.password == lp:
				session["username"] = lu
				return render_template("search.html")

		return render_template("error.html", message="Wrong username/password")
		

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
		u = request.form.get("username")
		p = request.form.get("password")

		#Ensure username was submitted

		if not u:
			return render_template("error.html", message="please enter a valid username")

		#Query databse for username
		userCheck = db.execute("SELECT username from users").fetchall()

		#check if username already exists
		for i in range(len(userCheck)):
			if userCheck[i]["username"] == u:
				return render_template("error.html", message="username already exists!")

		#check if password is provided
		if not p:
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

		session["username"] = u
		#commit changes to databse
		db.commit()

		

		#redirect to the login page
		return render_template("login.html")

	#if the user reached the route via GET
	else:
		return render_template("registration.html")

@app.route("/search", methods=["GET","POST"])
def search():
	
	sb = request.args.get("text")
	if sb=="":
		return render_template("error.html", message="Please provide the name of the book!")

	#to use 'LIKE' keyword
	query = ("%" + sb + "%").title()
	
	#select all the books that has similar name as the inputted one
	rows = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn LIKE :query OR title LIKE :query OR author LIKE :query LIMIT 15",{"query": query})
	#check if the book exist
	if rows.rowcount==0:
		return render_template("error.html", message="No book exist!")

	#fetch all the results
	books = rows.fetchall()
	return render_template("search.html", books=books)

@app.route("/book/<isbn>", methods=["GET", "POST"])
def book(isbn):

	current_user = session.get("u")

	#fetch data from the review form
	comment = request.form.get("comment")
	rating = request.form.get("rating")

	#
	rows = db.execute("SELECT * from books WHERE isbn=:isbn", {"isbn" : isbn})
	isbn = rows.fetchone()
	isbn = isbn[0]

	rows_rev = db.execute("SELECT * from reviews WHERE isbn=:isbn AND username=:username", {"isbn":isbn, "username":current_user})


	return render_template("error.html", message=rows_rev)




