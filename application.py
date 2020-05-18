import os, json, requests

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

@app.route("/temp")
def temp():
	return render_template("search.html")

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
				return redirect("temp")

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



@app.route("/search", methods=["GET"])
def search():
	if request.method == "GET":
		sb = request.args.get("text")
		if not sb:
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
		return render_template("results.html", books=books,sb=sb)

@app.route("/book/<isbn>", methods=["GET", "POST"])
def book(isbn):
	rows = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn LIKE :isbn",{"isbn": isbn})
	books = rows.fetchall()

	


	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "XjytnMTBuDsGMM2lWu33w", "isbns": isbn})
	res = res.json()
	avg_rating= res['books'][0]['average_rating']
	rate_count = res['books'][0]['work_ratings_count']
	return render_template("info.html", avg_rating=avg_rating, rate_count=rate_count, books=books)
	


	"""
	session["review"]=[]

	#fetch data from the review form



	rows_rev = db.execute("SELECT * from reviews WHERE isbn=:isbn AND username=:username", {"isbn":isbn, "username":username})
	if rows_rev.rowcount is None and request.method == "POST":


		review = request.form.get("comment")
		rating = request.form.get("rating")

		db.execute("INSERT into reviews (isbn,review, rating, username) Values (:isbn, :review, :rating,:username)",{"isbn": isbn, "review": review, "rating":rating, "username":username})
		db.commit()
	if rows_rev.rowcount and request.method == "POST":
	 	return render_template("error.html", message="sorry you cannot add another review")


	#goodreads

	key = os.getenv("GOODREADS_KEY")
	query = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":key, "isbns": isbn})

	response = query.json()
	arresponse = response['books'][0] ['ar']
	count = response['books'][0]['count']

	reviews = db.execute("SELECT * from books WHERE isbn=:isbn", {"isbn" : isbn}).fetchall()
	for y in reviews:
		session['reviews'].append(y)
	data = db.execute("SELECT * from books WHERE isbn=:isbn", {"isbn" : isbn}).fetchone()
	return render_template("book.html",data=data,reviews=session['reviews'],ar=ar,count=count,username=username,warning=warning)

	"""






