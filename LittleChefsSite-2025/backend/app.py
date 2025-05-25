import os
import sqlite3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import smtplib
from email.message import EmailMessage

DB_NAME = '/tmp/database.db'  # Use /tmp for Render compatibility

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            customer_email TEXT,
            items TEXT,
            total_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def send_order_notification(order_id, customer_name, items, total_amount):
    EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Email credentials not set. Skipping email notification.")
        return

    subject = f"New Order #{order_id} from {customer_name}"
    body = f"Order ID: {order_id}\nCustomer: {customer_name}\n\nItems:\n"
    for item in items:
        body += f"  - {item['quantity']}x {item['name']} - ₹{item['price'] * item['quantity']}\n"
    body += f"\nTotal: ₹{total_amount}\n\nThis is an automated notification."

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Email sent!")
    except Exception as e:
        print("❌ Failed to send email:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.get_json()
    customer_name = data.get('customer_name', '')
    customer_email = data.get('customer_email', '')
    items = data.get('items', [])
    total_amount = data.get('total_amount', 0)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (customer_name, customer_email, items, total_amount) VALUES (?, ?, ?, ?)",
        (customer_name, customer_email, str(items), total_amount)
    )
    order_id = c.lastrowid
    conn.commit()
    conn.close()

    send_order_notification(order_id, customer_name, items, total_amount)

    return jsonify({'success': True, 'order_id': order_id})

@app.route('/orders', methods=['GET'])
def get_orders():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, customer_name, items, total_amount, created_at FROM orders ORDER BY created_at DESC")
    orders = [
        {
            'id': row[0],
            'customer_name': row[1],
            'items': row[2],
            'total_amount': row[3],
            'created_at': row[4]
        }
        for row in c.fetchall()
    ]
    conn.close()
    return jsonify(orders)

if __name__ == '__main__':
    init_db()
    app.run()