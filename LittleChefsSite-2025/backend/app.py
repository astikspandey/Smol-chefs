from flask import Flask, request, jsonify, render_template
import sqlite3
from flask_cors import CORS
import webbrowser
import threading
import time
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)  # Allows frontend to talk to backend

DB_NAME = 'database.db'

# Load email credentials from environment variables
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                customer_email TEXT,
                items TEXT NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.get_json()
    customer_name = data.get("customer_name", "Anonymous")
    customer_email = data.get("customer_email", "")
    items = data.get("items", [])  # List of cart items
    total_amount = data.get("total_amount", 0)
    
    # Convert items list to JSON string for storage
    import json
    items_json = json.dumps(items)
    
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO orders (customer_name, customer_email, items, total_amount) 
            VALUES (?, ?, ?, ?)
        """, (customer_name, customer_email, items_json, total_amount))
        order_id = c.lastrowid
        conn.commit()
    
    # Auto-send email notification (simulated)
    send_order_notification(order_id, customer_name, items, total_amount)
    
    return jsonify({
        "message": "Order placed successfully!", 
        "order_id": order_id,
        "status": "sent"
    })

def send_order_notification(order_id, customer_name, items, total_amount):
    """Send order notification email to lumerskywalker@gmail.com"""
    # Email content
    subject = f"New Order #{order_id} from {customer_name}"
    body = f"Order ID: {order_id}\nCustomer: {customer_name}\n\nItems:\n"
    for item in items:
        body += f"  - {item['quantity']}x {item['name']} - ₹{item['price'] * item['quantity']}\n"
    body += f"\nTotal: ₹{total_amount}\n\nThis is an automated notification."

    # Email setup
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS  # <-- Use environment variable
    msg['To'] = EMAIL_ADDRESS    # <-- Use environment variable
    msg.set_content(body)

    # Send email using Gmail SMTP
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # <-- Use environment variable
            smtp.send_message(msg)
        print("✅ Email sent to lumerskywalker@gmail.com!")
    except Exception as e:
        print("❌ Failed to send email:", e)

@app.route('/orders', methods=['GET'])
def get_orders():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT id, customer_name, customer_email, items, total_amount, status, created_at FROM orders ORDER BY created_at DESC")
        orders = c.fetchall()
    
    # Convert to list of dictionaries for better JSON response
    orders_list = []
    for order in orders:
        orders_list.append({
            'id': order[0],
            'customer_name': order[1],
            'customer_email': order[2],
            'items': order[3],
            'total_amount': order[4],
            'status': order[5],
            'created_at': order[6]
        })
    
    return jsonify(orders_list)

def open_browser():
    """Opens the web browser after a short delay"""
    time.sleep(1.5)  # Wait for Flask to start
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    init_db()
    # Start browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    print("🍕 Little Chefs server starting...")
    print("🌐 Opening browser to http://127.0.0.1:5000/")
    app.run(debug=True, use_reloader=False)

# To run the app, use the command: python app.py