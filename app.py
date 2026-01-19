from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "replace_this_with_a_strong_random_secret"

# ---------- MySQL connection ----------

db = pymysql.connect(
    host="localhost",
    user="root",
    password="Deepk9@7011",
    database="accesseasedb"
)

cursor = db.cursor(pymysql.cursors.DictCursor)
# --------------------------------------


@app.route("/")
def home():
    return render_template("Home.html")


# ---------- SIGNUP ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        db.commit()

        flash("Signup successful! Please login.")
        return redirect(url_for('login'))

    return render_template('signup.html')


# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash("Login successful!")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password.")

    return render_template("login.html")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))



# ---------- Pages ----------
@app.route("/product")
def product():
    return render_template("product.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/cart")
def cart():
    return render_template("cart.html")

@app.route("/checkout")
def checkout():
    return render_template("checkout.html")

@app.route("/order")
def order():
    return render_template("order.html")

@app.route("/track")
def track():
    return render_template("track.html")

@app.route("/mobile")
def mobile():
    return render_template("mobile.html")

@app.route("/laptop")
def laptop():
    return render_template("laptop.html")

@app.route("/watch")
def watch():
    return render_template("watch.html")

@app.route("/earbuds")
def earbuds():
    return render_template("earbuds.html")

@app.route("/speaker")
def speaker():
    return render_template("speaker.html")


if __name__ == "__main__":
    app.run(debug=True)
