import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods = ["GET"])
@login_required
def index():

    """Show portfolio of stocks"""

    total_quantity = 0.0
    positions = db.execute("SELECT symbol, SUM(quantity) AS total_quantity FROM trades WHERE id = ? GROUP BY symbol ORDER BY symbol", session["user_id"])
    print(positions)

    ucash = 0.0
    users_cash = db.execute(
            "SELECT username, cash FROM users WHERE id = ?", session["user_id"])
    print(users_cash)
    ucash = float(users_cash[0]["cash"])
    ucash_quantity = round(ucash,4)
    ucash_dollars = usd(ucash)
    print(ucash_quantity)
    print(ucash_dollars)
    uname = users_cash[0]["username"]

    portfolio_total = 0.0

    for i in range(len(positions)):
        quote = lookup(positions[i]["symbol"])
        positions[i]["symbol"] = quote["symbol"]
        positions[i]["price"] = usd(quote["price"])
        positions[i]["quantity"] = positions[i]["total_quantity"]
        temp_value = float(quote["price"] * positions[i]["total_quantity"])
        positions[i]["value"] =  usd(quote["price"] * positions[i]["total_quantity"])
        portfolio_total += temp_value
        print(portfolio_total)

    portfolio_total = usd(portfolio_total + ucash)

    return render_template("index.html", positions=positions, ucash=ucash, ucash_quantity=ucash_quantity, ucash_dollars=ucash_dollars, portfolio_total=portfolio_total, username=uname)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("Must provide symbol")

        #check for valid symbol via lookup
        elif not lookup(request.form.get("symbol")):
            return apology("Enter valid symbol")

        elif not request.form.get("shares"):
            return apology("please enter number of shares")

        elif not request.form.get("shares").isdigit():
            return apology("Enter positive integer")

        elif int(request.form.get("shares")) <= 0:
            return apology("Enter positive integer")

        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        shares = int(request.form.get("shares"))
        print(symbol, quote, shares)
        # Query database for username
        users_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"])
        print(users_cash)
        available_cash = users_cash[0]["cash"]
        print(available_cash)
        stock_price = quote["price"]
        amount = stock_price * shares
        print(amount)
        remaining_cash = available_cash - amount
        print(remaining_cash)
        if (amount > available_cash):
            return apology("Insufficient funds", 403)
        else:
            db.execute("INSERT INTO trades (id, symbol, quantity, trade_price, Buy_Sell) VALUES(?, ?, ?, ?, ?)", session["user_id"], quote["symbol"], shares, quote["price"], 'Buy')
            db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", amount, session["user_id"])

            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    trades = db.execute("SELECT * FROM trades WHERE id = ? ORDER BY timestamp", session["user_id"])
    print(trades)
    for i in range(len(trades)):
        temp_amount = 0.0
        trades[i]["trade_id"] = trades[i]["trade_id"]
        trades[i]["timestamp"] = trades[i]["timestamp"]
        trades[i]["Buy_Sell"] = trades[i]["Buy_Sell"]
        trades[i]["symbol"] = trades[i]["symbol"]
        trades[i]["quantity"] = trades[i]["quantity"]
        trades[i]["trade_price"] = trades[i]["trade_price"]
        temp_amount = -1 * (trades[i]["trade_price"] * trades[i]["quantity"])
        trades[i]["trade_amount"] = usd(temp_amount)
        trades[i]["trade_price"] = usd(trades[i]["trade_price"])

    return render_template("history.html", trades=trades)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

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

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Profile"""

    if request.method == "POST":
        user_profile = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        user_id = user_profile[0]["id"]
        user_name = user_profile[0]["username"]

        return render_template("update.html", user_id=user_id, user_name=user_name)

    # User reached route via GET (as by clicking a link or via redirect)

    else:
        user_profile = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        print(user_profile)

        user_id = user_profile[0]["id"]
        user_name = user_profile[0]["username"]

        return render_template("profile.html", user_id=user_id, user_name=user_name)

@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """Password Update"""

    if request.method == "POST":
        # Ensure current password was submitted
        if not request.form.get("password"):
            return apology("must provide current password", 403)

        # Ensure new password was submitted
        elif not request.form.get("password_update"):
            return apology("must provide new password", 403)

        # Ensure new password was confirmed
        elif not request.form.get("confirm"):
            return apology("Must confirm new password", 403)

        user_profile = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        user_id = user_profile[0]["id"]
        user_name = user_profile[0]["username"]

        # Ensure current password is correct
        if not check_password_hash(user_profile[0]["hash"], request.form.get("password")):
            return apology("invalid password", 403)

        # Ensure password is entered and confirmed
        password_update = request.form.get("password_update")
        confirm = request.form.get("confirm")

        if password_update != confirm:
            return apology("Passwords do not match")

        # add to user table

        hash = generate_password_hash(request.form.get("password_update"))
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)

    else:
        return apology("invalid access", 403)


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("Must provide symbol", 400)

        #check for valid symbol via lookup
        elif not lookup(request.form.get("symbol")):
            return apology("Enter valid symbol", 400)

        symbol = request.form.get("symbol")
        quote = lookup(symbol)

        return render_template("quoted.html", quote=quote)

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password was confirmed
        elif not request.form.get("confirmation"):
            return apology("Must confirm password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username is unique
        if len(rows) != 0:
            return apology("username already exists", 400)

        # Ensure password is entered and confirmed
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        if password != confirm:
            return apology("Passwords do not match")

        # add to user table
        name = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))
        cash = 10000.00
        db.execute("INSERT INTO users (username, hash, cash) VALUES(?, ?, ?)", name, hash, cash)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
        # User reached route via POST (as by submitting a form via POST)

    if request.method == "POST":
        # Ensure symbol was submitted

        print_symbol = request.form.get("symbol")
        print(print_symbol)

        if not request.form.get("symbol"):
            return apology("Must provide symbol")

        #check for valid symbol via lookup
        elif not lookup(request.form.get("symbol")):
            return apology("Enter valid symbol")

        elif not request.form.get("shares"):
            return apology("please enter number of shares")

        elif request.form.get("shares", type=int) <= 0:
            return apology("Enter positive integer")

        total_quantity = 0.0
        sell_quantity = 0.0
        sell_symbol = request.form.get("symbol")
        sell_symbol = sell_symbol.upper()
        sell_quantity = request.form.get("shares", type=int)

        sale = db.execute("SELECT symbol, SUM(quantity) AS total_quantity FROM trades WHERE id = ? AND symbol = ? GROUP BY symbol ORDER BY symbol", session["user_id"], sell_symbol)
        print(sale)

        if sell_quantity > int(sale[0]["total_quantity"]):
            return apology("Inadequate holdings")
        else:
            quote = lookup(sale[0]["symbol"])
            sale[0]["symbol"] = quote["symbol"]
            sale[0]["price"] = usd(quote["price"])
            sale[0]["quantity"] = -1 * sell_quantity
            temp_value = float(quote["price"] * sell_quantity)
            sale[0]["value"] =  usd(quote["price"] * sell_quantity)
            db.execute("INSERT INTO trades (id, symbol, quantity, trade_price, Buy_Sell) VALUES(?, ?, ?, ?, ?)", session["user_id"], quote["symbol"], sale[0]["quantity"], quote["price"], 'Sell')
            db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", temp_value, session["user_id"])

            return redirect("/")


        # User reached route via GET (as by clicking a link or via redirect)
    else:
        total_quantity = 0.0
        temp_value = 0.0
        portfolio_total = 0.0
        positions = db.execute("SELECT symbol, SUM(quantity) AS total_quantity FROM trades WHERE id = ? GROUP BY symbol ORDER BY symbol", session["user_id"])
        print(positions)

        for i in range(len(positions)):

            quote = lookup(positions[i]["symbol"])
            positions[i]["symbol"] = quote["symbol"]
            positions[i]["price"] = usd(quote["price"])
            positions[i]["quantity"] = positions[i]["total_quantity"]
            temp_value = float(quote["price"] * positions[i]["total_quantity"])
            positions[i]["value"] =  usd(quote["price"] * positions[i]["total_quantity"])
            portfolio_total += temp_value
            print(portfolio_total)

        return render_template("sell.html", positions=positions, portfolio_total=portfolio_total)
