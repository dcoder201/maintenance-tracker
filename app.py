# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS categories
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')

    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY, name TEXT, category_id INTEGER,
                 FOREIGN KEY(category_id) REFERENCES categories(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS reports
                 (id INTEGER PRIMARY KEY, date TEXT, floor TEXT, room TEXT,
                 category TEXT, item TEXT, condition TEXT, remarks TEXT)''')

    # Insert default data
    default_categories = ['IT', 'Electrical', 'Bio Medical', 'Furniture', 'Others']
    for cat in default_categories:
        try:
            c.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
        except sqlite3.IntegrityError:
            pass

    default_items = [
        ('TV', 1), ('TV Remote', 1), ('System', 1), ('Printer', 1),
        ('ELV port & cabling', 1), ('Telephone', 1), ('NCS', 1),
        ('PA System', 1), ('Projector', 1), ('Scanner', 1), ('Camera', 1),
        ('Wifi', 1), ('Access Door', 1), ('Room lights', 2), ('Bathroom lights', 2),
        ('Mirror lights', 2), ('Foor Lamps', 2), ('Plug Point', 2), ('Wall Plug Points', 2),
        ('Ceiling Fan', 2), ('Exhaust Fan', 2), ('AC', 2), ('Fridge', 2), ('Taps', 2),
        ('Health Faucet', 2), ('Flush Tank', 2), ('Wash Basin', 2), ('Shower', 2),
        ('Corridor Lights', 2), ('Water Heater', 2), ('Water Dispenser', 2), ('Lift', 2),
        ('common toilet lights', 2), ('Common Toilet Exhaust Fans', 2), ('BHU (Bed Head Unit)', 3),
        ('BHU-No Breakage', 3), ('BHU-Outlets-No breakage', 3),
        ('BHU Side Covers-Present', 3), ('BHU-Any Rust Present', 3), ('Vacuum', 3),
        ('vaccum-No breakage', 3), ('vaccum-Guage is working', 3), ('vaccum-ON/OFF Switch Working', 3),
        ('vaccum-Jar is present', 3), ('Oxygen ', 3), ('oxygen-No breakage', 3), ('oxygen-Guage is working', 3),
        ('oxygen-Flowmeter is present', 3), ('oxygen-Knob working', 3), ('oxygen-No breakage', 3),
        ('Patient Bed (Metal Type)', 3), ('Bush in Legs-Available', 3), ('patient bed-Wheels ', 3),
        ('patient bed-Key is present', 3), ('patient bed-2 No-Side Rails', 3), ('Head and Foot Rails', 3),
        ('Patient bed-Mattress', 3), ('Patient bed- Oxygen Tray', 3), ('Patient bed- IV Stand', 3),
        ('Patient bed-Urine Bag Holder', 3), ('Patient bed-Any Rust Present', 3), ('Cardiac Table ', 3),
        ('Cardiac Table-Wheels OK ', 3), ('Cardiac Table-Height  Adjustment ', 3),
        ('Cardiac Table-Inclination Working ', 3),
        ('Cardiac Table-Wooden Top is Fine', 3), ('Cardiac Table-Any Rust Present ', 3),
        ('Bystander Bed/Cot (Metal)', 3),
        ('Bystander Bed-Bush in Legs-Available', 3), ('Bystander Bed-Mattress OK', 3),
        ('Bystander Bed-Balancing Ok', 3), ('Bystander Bed-Physical Breakage Any', 3),
        ('Bystander Bed-Any Rust Present', 3),
        ('DINING TABLE WITH CHAIR', 4), ('CARDIAC TABLE', 4), ('ARM CHAIR', 4), ('ARMLESS CHAIR', 4),
        ('ALMIRAH', 4), ('NORMAL BED', 4), ('ADJUSTABLE BED', 4), ('BYSTANDER COT NORMAL', 4), ('BYSTADER COT WOODEN', 4),
        ('SOFA SET', 4)
    ]
    for item in default_items:
        try:
            c.execute(
                "INSERT INTO items (name, category_id) SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM items WHERE name=? AND category_id=?)",
                (item[0], item[1], item[0], item[1]))

        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()


@app.route('/')
def index():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute("SELECT * FROM categories")
    categories = c.fetchall()
    conn.close()
    return render_template('index.html', categories=categories)


@app.route('/get_items/<int:category_id>')
def get_items(category_id):
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT name FROM items WHERE category_id=?", (category_id,))
    items = [item[0] for item in c.fetchall()]
    conn.close()
    return jsonify(items=items)


@app.route('/submit', methods=['POST'])
def submit():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    # Get category name from ID
    category_id = request.form['category']
    c.execute("SELECT name FROM categories WHERE id=?", (category_id,))
    category_name = c.fetchone()[0]

    report_data = (
        datetime.now().strftime('%Y-%m-%d'),
        request.form['floor'],
        request.form['room'],
        category_name,
        request.form['item'],
        request.form['condition'],
        request.form['remarks']
    )

    c.execute('''INSERT INTO reports 
                 (date, floor, room, category, item, condition, remarks)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', report_data)


    conn.commit()
    conn.close()
    return redirect(url_for('view'))


@app.route('/view')
def view():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute("SELECT * FROM reports ORDER BY date DESC")
    reports = c.fetchall()
    conn.close()
    return render_template('view.html', reports=reports)


@app.route('/manage')
def manage():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute("SELECT * FROM categories")
    categories = c.fetchall()
    c.execute("SELECT items.name, categories.name FROM items JOIN categories ON items.category_id = categories.id")
    items = c.fetchall()
    conn.close()
    return render_template('manage.html', categories=categories, items=items)


@app.route('/add_category', methods=['POST'])
def add_category():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    new_category = request.form['new_category']
    try:
        c.execute("INSERT INTO categories (name) VALUES (?)", (new_category,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()
    return redirect(url_for('manage'))




@app.route('/add_item', methods=['POST'])
def add_item():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    new_item = request.form['new_item']
    category_id = request.form['category']

    # Check if item already exists in the category before inserting
    c.execute("SELECT COUNT(*) FROM items WHERE name = ? AND category_id = ?", (new_item, category_id))
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO items (name, category_id) VALUES (?, ?)", (new_item, category_id))
        conn.commit()

    conn.close()
    return redirect(url_for('manage'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
