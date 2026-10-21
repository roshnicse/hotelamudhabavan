import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "database.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "hab-secure-restaurant-key-2026")

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin123")

# ---- Edit these to match the client ------------------------------------
RESTAURANT = {
    "name": "Hotel Amudhabawan",
    "short_name": "HAB",
    "full_name": "Hotel Amudhabawan (HAB) • 100% Pure Vegetarian",
    "tagline": "Taste Tradition. 100% Pure Vegetarian Excellence.",
    "est": "2008",
    "phone": "+91 94433 12345",
    "email": "contact@amudhabawan.com",
    "address": "Opp. Kongu Kalaiarangam, Sampath Nagar, Erode, Tamil Nadu - 638011",
    "hours": "Daily: 7:00 AM – 10:30 PM",
}

MENU = {
    "South Indian Specials & Tiffin": [
        ("Ghee Podi Roast", "Crispy golden roast laced with aromatic homemade podi and pure cow ghee", 110),
        ("Special Masala Dosa", "Crisp rice crepe stuffed with spiced potato masala, served with 3 chutneys & sambar", 95),
        ("Ghee Paper Roast", "Super thin and crispy large wafer-style dosa roasted in pure ghee", 130),
        ("Idly Vada Sambar (2+1)", "Steaming hot soft mallipoo idlies with crispy medu vada and piping hot sambar", 75),
        ("Onion Uthappam", "Thick fluffy fermented pancake topped with caramelized shallots and green chillies", 90),
        ("Rava Masala Dosa", "Crunchy semolina crepe filled with potato masala and cashews", 105),
    ],
    "Traditional Meals & Rice": [
        ("Amudhabawan Special Full Meals", "Unlimited South Indian meals on banana leaf with sambar, rasam, kootu, poriyal, appalam, payasam & curd", 150),
        ("Special Veg Dum Biryani", "Seeraga samba rice cooked with fresh farm vegetables and whole aromatic spices", 140),
        ("Ghee Sambar Rice", "Traditional temple-style sambar rice tempered with ghee and cashews", 90),
        ("Curd Rice with Pomegranate", "Creamy tempered curd rice with mustard, ginger, green chillies & pomegranate", 80),
        ("Veg Fried Rice", "Wok-tossed long-grain basmati with crisp shredded vegetables", 140),
    ],
    "Soups": [
        ("Mushroom Soup", "Rich creamy soup loaded with fresh button mushrooms and cracked pepper", 90),
        ("Veg Manchow Soup", "Spicy Indo-Chinese broth with minced vegetables topped with crispy fried noodles", 85),
        ("Classic Tomato Soup", "Velvety fresh country tomato broth garnished with fried bread croutons", 80),
        ("Hot & Sour Veg Soup", "Tangy and spicy vegetable broth infused with ginger, garlic and soy", 85),
    ],
    "Dry Starters": [
        ("Gobi 65", "Crispy golden fried cauliflower florets tossed with curry leaves and green chillies", 120),
        ("Paneer Manchurian", "Crispy cottage cheese cubes tossed in spicy tangy Manchurian sauce", 160),
        ("Chilli Mushroom", "Batter-fried button mushrooms sautéed with bell peppers and spring onions", 150),
        ("Baby Corn Fry", "Crispy golden baby corn fingers seasoned with fragrant southern spices", 130),
        ("Aloo Jeera", "Baby potatoes roasted with fragrant cumin seeds, green chillies and fresh coriander", 110),
        ("Veg Ball Manchurian", "Minced vegetable dumplings tossed in garlic-flavoured Indo-Chinese gravy or dry", 130),
        ("Paneer Tikka", "Clay-oven roasted cottage cheese marinated in spiced curd and herbs", 180),
    ],
    "North Indian Gravies & Breads": [
        ("Paneer Butter Masala", "Rich tomato-cashew gravy with melt-in-the-mouth paneer cubes and butter finish", 170),
        ("Kadai Vegetable", "Assorted garden veggies cooked in a spicy freshly ground kadai masala", 150),
        ("Dal Tadka", "Yellow lentils tempered with ghee, cumin seeds, garlic and dry red chillies", 130),
        ("Butter Naan", "Tandoor baked refined flour bread brushed with fresh butter", 55),
        ("Garlic Naan", "Charred tandoor naan infused with fresh minced garlic and coriander", 65),
        ("Malabar Parotta (2 Pcs)", "Flaky layered South Indian flatbread served with vegetable kurma", 70),
    ],
    "Desserts & Sweets": [
        ("Traditional Payasam (Daily Special)", "Rich slow-simmered payasam with roasted cashews, raisins and cardamom", 60),
        ("Gulab Jamun (2 Pcs)", "Soft khoya dumplings soaked in warm rose and cardamom scented sugar syrup", 60),
        ("Special Milk Sweets Platter", "Assorted traditional Indian ghee and milk sweets", 100),
        ("Vanilla / Pista Ice Cream", "Creamy churned ice cream scoop", 70),
    ],
    "Beverages": [
        ("South Indian Degree Filter Coffee", "Signature decoction brewed with fresh milk in traditional brass davarah", 40),
        ("Fresh Lime Soda (Sweet / Salt)", "Refreshing fizzy soda with fresh squeezed lemon juice and mint", 50),
        ("Sweet Lassi / Mango Lassi", "Thick churned creamy yogurt beverage", 70),
        ("Fresh Fruit Juice (Seasonal)", "Freshly pressed natural fruit juice (Orange / Mosambi / Apple)", 80),
        ("Masala Tea", "Aromatic brewed tea with crushed ginger and cardamom", 35),
    ],
}

SIGNATURE_DISHES = [
    {
        "name": "Ghee Podi Roast",
        "price": 110,
        "image": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?q=80&w=600&auto=format&fit=crop",
        "desc": "Crispy golden dosa generously roasted in pure cow ghee and signature spicy podi."
    },
    {
        "name": "Amudhabawan Full Meals",
        "price": 150,
        "image": "https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?q=80&w=600&auto=format&fit=crop",
        "desc": "Grand traditional South Indian unlimited feast served on a fresh banana leaf."
    },
    {
        "name": "Paneer Butter Masala",
        "price": 170,
        "image": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?q=80&w=600&auto=format&fit=crop",
        "desc": "Fresh cottage cheese in a silky tomato, cashew and butter rich gravy."
    },
    {
        "name": "Gobi 65",
        "price": 120,
        "image": "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?q=80&w=600&auto=format&fit=crop",
        "desc": "Crunchy deep-fried cauliflower tossed with southern spices and curry leaves."
    },
    {
        "name": "Degree Filter Coffee",
        "price": 40,
        "image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?q=80&w=600&auto=format&fit=crop",
        "desc": "Signature hot degree filter coffee brewed from freshly roasted beans."
    }
]


def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, email TEXT,
            date TEXT, time TEXT, guests INTEGER, notes TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        con.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, message TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        con.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone TEXT,
            order_type TEXT,
            table_no TEXT,
            items TEXT,
            total_price REAL,
            status TEXT DEFAULT 'Received',
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")


@app.context_processor
def inject_globals():
    return {"r": RESTAURANT}


@app.route("/")
def index():
    return render_template("index.html", menu=MENU, signatures=SIGNATURE_DISHES)


@app.route("/quick-reserve", methods=["POST"])
def quick_reserve():
    f = request.form
    date = f.get("date", "").strip()
    time = f.get("time", "").strip()
    guests = f.get("guests", "2").strip()
    name = f.get("name", "Guest Customer").strip()
    phone = f.get("phone", "+91 98765 00000").strip()

    if not (date and time):
        flash("Please select date and time for table reservation.", "error")
        return redirect(url_for("index"))

    try:
        guests_int = int(guests)
    except ValueError:
        guests_int = 2

    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO reservations (name, phone, email, date, time, guests, notes) VALUES (?,?,?,?,?,?,?)",
            (name, phone, "", date, time, guests_int, "Quick Table Booking from Homepage Bar"))
    flash(f"Table requested for {guests_int} guests on {date} at {time}! We will confirm shortly.", "ok")
    return redirect(url_for("reservation"))


@app.route("/menu")
def menu():
    return render_template("menu.html", menu=MENU)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        f = request.form
        if not (f.get("name", "").strip() and f.get("message", "").strip()):
            flash("Please enter your name and a message.", "error")
            return redirect(url_for("contact"))
        with sqlite3.connect(DB) as con:
            con.execute("INSERT INTO messages (name, email, message) VALUES (?,?,?)",
                        (f["name"].strip(), f.get("email", "").strip(), f["message"].strip()))
        flash("Message sent. We will reply soon.", "ok")
        return redirect(url_for("contact"))
    return render_template("contact.html")


@app.route("/reservation", methods=["GET", "POST"])
@app.route("/reserve", methods=["GET", "POST"])
def reservation():
    if request.method == "POST":
        f = request.form
        needed = ("name", "phone", "date", "time", "guests")
        if not all(f.get(k, "").strip() for k in needed):
            flash("Please fill in name, phone, date, time and number of guests.", "error")
            return redirect(url_for("reservation"))
        with sqlite3.connect(DB) as con:
            con.execute(
                "INSERT INTO reservations (name, phone, email, date, time, guests, notes) VALUES (?,?,?,?,?,?,?)",
                (f["name"].strip(), f["phone"].strip(), f.get("email", "").strip(),
                 f["date"], f["time"], int(f["guests"]), f.get("notes", "").strip()))
        flash("Table requested. We will call to confirm your booking.", "ok")
        return redirect(url_for("reservation"))
    return render_template("reservation.html")


@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        f = request.form
        customer_name = f.get("customer_name", "").strip()
        phone = f.get("phone", "").strip()
        order_type = f.get("order_type", "").strip()
        table_no = f.get("table_no", "").strip()

        if not (customer_name and phone):
            flash("Please enter your name and phone number.", "error")
            return redirect(url_for("order"))

        names = f.getlist("item_name")
        prices = f.getlist("item_price")
        qtys = f.getlist("item_qty")

        selected_items = []
        total_price = 0.0

        for n, p, q in zip(names, prices, qtys):
            try:
                qty_int = int(q)
                price_float = float(p)
                if qty_int > 0:
                    subtotal = qty_int * price_float
                    total_price += subtotal
                    selected_items.append(f"{qty_int}x {n} (₹{int(subtotal)})")
            except (ValueError, TypeError):
                continue

        if not selected_items:
            flash("Please select at least 1 item to place an order.", "error")
            return redirect(url_for("order"))

        items_str = ", ".join(selected_items)

        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""INSERT INTO orders (customer_name, phone, order_type, table_no, items, total_price, status)
                           VALUES (?, ?, ?, ?, ?, ?, 'Received')""",
                        (customer_name, phone, order_type, table_no, items_str, total_price))
            order_id = cur.lastrowid

        flash(f"Order #{order_id} placed successfully! Total: ₹{int(total_price)}. Our chefs are on it!", "ok")
        return redirect(url_for("order"))

    return render_template("order.html", menu=MENU)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "").strip()
        if u == ADMIN_USER and p == ADMIN_PASS:
            session["is_admin"] = True
            flash("Welcome to the Hotel Amudhabawan Staff Dashboard.", "ok")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid staff username or password. Please try again.", "error")
            return redirect(url_for("admin_login"))

    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("You have been securely logged out.", "ok")
    return redirect(url_for("admin_login"))


@app.route("/admin")
def admin_dashboard():
    if not session.get("is_admin"):
        flash("Restricted area. Please log in with staff credentials.", "error")
        return redirect(url_for("admin_login"))

    with sqlite3.connect(DB) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        reservations = cur.execute("SELECT * FROM reservations ORDER BY id DESC").fetchall()
        orders = cur.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
        messages = cur.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()

    return render_template("admin.html", reservations=reservations, orders=orders, messages=messages)


@app.route("/admin/delete-reservation/<int:id>", methods=["POST"])
def delete_reservation(id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    with sqlite3.connect(DB) as con:
        con.execute("DELETE FROM reservations WHERE id = ?", (id,))
    flash(f"Reservation #{id} deleted.", "ok")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/delete-order/<int:id>", methods=["POST"])
def delete_order(id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    with sqlite3.connect(DB) as con:
        con.execute("DELETE FROM orders WHERE id = ?", (id,))
    flash(f"Order #{id} deleted.", "ok")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/delete-message/<int:id>", methods=["POST"])
def delete_message(id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    with sqlite3.connect(DB) as con:
        con.execute("DELETE FROM messages WHERE id = ?", (id,))
    flash(f"Message #{id} deleted.", "ok")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/order-status/<int:id>", methods=["POST"])
def update_order_status(id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    new_status = request.form.get("status", "Received")
    with sqlite3.connect(DB) as con:
        con.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, id))
    flash(f"Order #{id} status updated to {new_status}.", "ok")
    return redirect(url_for("admin_dashboard"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
