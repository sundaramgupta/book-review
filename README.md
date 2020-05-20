<h1> CS50s Web Programming with Python and JavaScript </h1>
This web application is a part of an online course by Harvard University
<h1> Use the app </h1>
https://book-review-goodreads.herokuapp.com/
<h1> Features </h1>
<ul>
  <li>Register</li>
  <li>Login</li>
  <li>Search for books by name, author or ISBN</li>
  <li>Write a review</li>
  <li>Real-time Goodreads average rate and review count</li>
  <li>Json response if made a GET request to /api/isbn route</li>
 </ul>
<h1> Set up your own environment </h1> 


1. Clone the repo ```git clone https://github.com/sundaramgupta/book-review.git```
2. Install all the dependencies ```pip install -r requirements.txt``` 

3. set ENV Variables (for windows)
```bash
set FLASK_APP = application.py
set DATABASE_URL = Heroku Postgres DB URI
set GOODREADS_KEY = Goodreads API Key
```

4. Use ```flask run```
  
