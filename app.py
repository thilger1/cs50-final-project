from flask import Flask, render_template, flash, request, redirect, session
from flask_session import Session
import os, re, sqlite3
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import login_required, usd

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.jinja_env.filters["usd"] = usd
db = SQL("sqlite:///inventory.db")

@app.route('/', methods=["GET", "POST"])
def index():

    images = db.execute("SELECT * FROM products WHERE isMerch = 0")
    session["item"] = None

    if request.method == "POST":
        session["item"] = request.form.get("id")
        return redirect('/item')
    
    return render_template("index.html", images=images, usd=usd)

@app.route('/merch', methods=['GET', 'POST'])
def merch():

    images = db.execute("SELECT * FROM products WHERE isMerch = 1")
    session["item"] = None
        
    if request.method == "POST":
        session["item"] = request.form.get("id")
        return redirect('/item')

    return render_template("merch.html", images=images, usd=usd)

@app.route('/item', methods=['GET', "POST"])
def item():
    if 'cart' not in session:
        session['cart'] = []

    if request.method == "GET":
        item = db.execute("SELECT * FROM products WHERE productID = ?", session["item"])
        return render_template("item.html", item=item, usd=usd)

    if request.method == "POST":
        id = request.form.get("id")
        if id:
            session['cart'].append(id)

        flash("Added to cart")
        return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/cart', methods=["GET", "POST"])
def cart():

    if 'cart' not in session:
        session['cart'] = []

    if request.method == "POST":
        id = request.form.get("id")
        if id:
            session['cart'].remove(id)
        flash("Removed from cart")
        return redirect("/cart")

    items = db.execute("SELECT * FROM products WHERE productID IN (?)", session['cart'])

    if len(session['cart']) == 0:
        empty = True
    else:
        empty = False

    return render_template("cart.html", items=items, usd=usd, empty=empty)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

            try:
            #for product in session['cart']:
                #db.execute("UPDATE products SET inStock = 0")
                #db.execute("INSERT into ORDERS productID, userID, date")
                db.execute("UPDATE products,  (email, password) VALUES (?, ?)", email, hash)
                flash("Thank you for your order!")
                session["cart"] = None
                return redirect("/cart")
            
            except:
                flash("Email already exists!")
                return redirect("/register")
    return render_template("checkout.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "GET":

        return render_template("login.html")

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            flash("must provide email")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password")

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        if not rows:
            flash("Could not find email")
            return redirect("/login")
        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            flash("Invalid email and/or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["userID"]
        session["name"] = rows[0]["email"]

        # Redirect user to home page
        return redirect("/profile")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return redirect("/login")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    email = request.form.get("email")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    if request.method == "GET":
        return render_template("register.html")

    """Register user"""

    if request.method == "POST":
        if not email:
            flash("Must enter an email")
            return redirect("/register")
        if not len(password) > 5:
            flash("Password must be 6 or more characters long")
            return redirect("/register")

        if not re.search('[!@#$%&()\-_[\]{}"./<>?]', password):
            flash("Password must contain at least one symbol (not : or ;)")
            return redirect("/register")
        if not re.search('[0-9]', password):
            flash("Password must contain at least on number")
            return redirect("/register")
        if re.search('[:;]', password):
            flash("Password cannot contain : or ;")
            return redirect("/register")

        if not password == confirmation:
            flash("Passwords don't match")
            return redirect("/register")
        else:
            hash = generate_password_hash(password)
            try:
                db.execute("INSERT INTO users (email, password) VALUES (?, ?)", email, hash)
                flash("Successfully registered!")
                return redirect("/login")
            except:
                flash("Email already exists!")
                return redirect("/register")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/orders')
def orders():
    return render_template("orders.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")