from flask import Flask, render_template, flash, request, redirect, session, url_for
from flask_session import Session
import os, re, sqlite3
from datetime import date
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import login_required, usd

UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


app.jinja_env.filters["usd"] = usd
db = SQL("sqlite:///inventory.db")

@app.route('/', methods=["GET", "POST"])
def index():

    images = db.execute("SELECT * FROM products WHERE isMerch = 0 AND inStock = 1 ORDER BY productID DESC")
    session["item"] = None

    if request.method == "POST":
        if request.form.get("id") == 'admin':
            return redirect('/newfile')
        if id:
            session["item"] = request.form.get("id")
            return redirect('/item')

    return render_template("index.html", images=images, usd=usd)

@app.route('/merch', methods=['GET', 'POST'])
def merch():

    images = db.execute("SELECT * FROM products WHERE isMerch = 1 AND inStock = 1 ORDER BY productID DESC")
    session["item"] = None
        
    if request.method == "POST":
        if request.form.get("id") == 'admin':
            return redirect('/newfile')
        if id:
            session["item"] = request.form.get("id")
            return redirect('/item')

    return render_template("merch.html", images=images, usd=usd)

@app.route('/item', methods=['GET'])
def get_item():

    if request.method == "GET":
        carted = False
        if not 'cart' in session:
            session['cart'] = []
        item = db.execute("SELECT * FROM products WHERE productID = ?", session["item"])
        
        if session['cart'] != None:
            if session['item'] in session['cart']:
                carted = True

    return render_template("item.html", item=item, carted=carted, usd=usd)

@app.route('/item', methods=['POST'])
@login_required
def post_item():
    if not 'cart' in session or (session['cart'] == None):
        session['cart'] = []
    if session['user_id'] == "admin":
        id = request.form.get("id")
        if id:
            db.execute("UPDATE products SET inStock = 0 WHERE productID = ?", id)
            flash("Item removed from store")
            return redirect("/")

    if request.method == "POST":
        id = request.form.get("id")
        if id:
            session['cart'].append(id)

        flash("Added to cart")
        return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/cart', methods=["GET", "POST"])
@login_required
def cart():
    if not 'cart' in session:
        session['cart'] = []

    if request.method == "POST":
        id = request.form.get("id")
        if id:
            session['cart'].remove(id)
        flash("Removed from cart")
        return redirect("/cart")
            
    if session['cart'] == []:
        empty = True
    else:
        empty = False
    
    if not empty:
        print(session['cart'])
        items = db.execute("SELECT * FROM products WHERE productID IN (?)", session['cart'])
        total = sum([x['price'] for x in items])
        session['total'] = total
    else:
        items = []
        total = 0
        session['total'] = total

    return render_template("cart.html", items=items, usd=usd, empty=empty, total=total)

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    
    if request.method == "POST":
        email = request.form.get('email')
        user_ID = session['user_id']
        first = request.form.get("first")
        last = request.form.get("last")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        zip = int(request.form.get("zip"))
            #adding order
        if not re.search('@', email):
            flash('Email must follow proper format, i.e. "@example.com"')
            return redirect("/checkout")
        try:
            db.execute("INSERT INTO orders (userID, date, amount, placed) VALUES (?, ?, ?, ?)", user_ID, date.today(), session['total'], 0)
                    #adding shipping to order
            db.execute("INSERT INTO shipping (userID, first, last, address, city, state, zip) VALUES (?, ?, ?, ?, ?, ?, ?)", user_ID, first, last, address, city, state, zip)
                    #adding bought items - need to get orderID that was just created
            order_ID = db.execute("SELECT MAX(id) AS id FROM orders WHERE userID = ?", user_ID)
            order_ID = order_ID[0]['id']
            for item in session['cart']:
                db.execute("INSERT INTO bought (productID, orderID, userID) VALUES (?, ?, ?)", item, order_ID, user_ID)
                db.execute("UPDATE products SET inStock = 0 WHERE productID = ?", item)
                session['cart'] = []

            flash("Successfully ordered, thank you!")
            return redirect("/cart")

        except:
            flash("Sorry, could not place order at this time")
            return redirect("/cart")

    return render_template("checkout.html")
@app.route("/login", methods=["GET", "POST"])
def login():
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
        
        if request.form.get('email') == 'admin':
            session["user_id"] = "admin"
        else:
            session["user_id"] = rows[0]["id"]
        return redirect("/profile")

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

@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    admin = False
    if session["user_id"] == "admin":
        admin = True
    if request.method == 'POST':
        item = request.form.get("id")
        db.execute("UPDATE products SET inStock = 1 WHERE productID = ?", item)
        flash("Re-added to store")
        return redirect("/profile")
    #need to join product info from products ordered with order info to give relevant info - repeat for admin side orders
    # add "filled" BIT section to orders to easily change whether orders appear as filled or not
    products = db.execute("SELECT DISTINCT products.name, orders.date, products.price FROM orders JOIN bought ON orders.userID = bought.userID JOIN products ON products.productID = bought.productID WHERE orders.userID = ?", session['user_id'])
    outStock = db.execute("SELECT * FROM products WHERE inStock = 0 ORDER BY productID DESC")
    print(products)
    return render_template("profile.html", products=products, usd=usd, admin=admin, outStock=outStock)

@app.route('/orders', methods=["GET", "POST"])
@login_required
def orders():
    if request.method == 'GET':
        unfilled = db.execute("SELECT id, date FROM orders WHERE placed = 0")
        filled = db.execute("SELECT id, date FROM orders WHERE placed = 1")
        return render_template("orders.html", filled=filled, unfilled=unfilled, usd=usd)
    if request.method == 'POST':
        id = request.form.get('id')
        placed = db.execute("SELECT placed FROM orders WHERE id = ?", id)
        placed = placed[0]['placed']
        print(placed)
        if placed == 0:
            placed = 1
        else:
            placed = 0
        db.execute("UPDATE orders SET placed = ? WHERE id = ?", placed, id)
        flash('Updated order status')
        return redirect('/orders')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/newitem', methods=['GET', 'POST'])
@login_required
def newitem():
    if request.method == 'POST':
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        type = request.form.get('type')
        if type == 'merch':
            type = 1
        else:
            type = 0
        if 'file' not in request.files:
            flash('No file')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.execute("INSERT INTO products (name, price, description, inStock, isMerch, image) VALUES (?, ?, ?, ?, ?, ?)", name, price, description, 1, type, filename)
            return redirect("/")
    return render_template('newitem.html')

@app.route('/info', methods=['GET', 'POST'])
@login_required
def info():
    if request.method == "POST":
        session['order'] = request.form.get('order')
        return redirect('/info')
    if request.method == "GET":
        order = session['order']
        print(order)
        shipping = db.execute("SELECT * FROM shipping WHERE id = ?", order)
        print(shipping)
        total = db.execute("SELECT amount FROM orders WHERE id = ?", order)
        print(total)
        products = db.execute("SELECT products.name FROM products JOIN bought ON products.productID = bought.productID WHERE bought.orderID = ?", order)
        print(products)
        return render_template('info.html', products=products, shipping=shipping, total=total, order=order, usd=usd)