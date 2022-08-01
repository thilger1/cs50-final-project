from flask import Flask, render_template, flash, request, redirect, session
from flask_session import Session
import os, sqlite3
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/')
def index():
    db = SQL("sqlite:///inventory.db")
    images = db.execute("SELECT name, price, description, inStock, image1, category FROM products")
    return render_template("index.html", images=images)

if __name__ == "__main__":
    app.run(debug=True)