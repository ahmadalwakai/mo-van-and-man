from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
import psycopg2
import hashlib
import os
import smtplib
from email.mime.text import MIMEText
import requests
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize the app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# ----------------- Database Connection -----------------
def connect_db():
    return psycopg2.connect(
        dbname="transport",
        user="postgres",
        password="Aa234311Aa@@@",
        host="localhost",
        port="5432"
    )

# ----------------- Email Notification -----------------
def send_email(subject, body, to_email):
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = to_email

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_address, email_password)
        server.sendmail(email_address, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

# ----------------- Distance Calculation -----------------
def calculate_distance(pickup_location, dropoff_location):
    api_key = os.getenv('ORS_API_KEY')
    geocode_url = "https://api.openrouteservice.org/geocode/search"
    directions_url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {"Authorization": api_key}

    try:
        # Get coordinates for pickup location
        pickup_response = requests.get(geocode_url, headers=headers, params={"text": pickup_location})
        pickup_response.raise_for_status()
        pickup_data = pickup_response.json()
        pickup_coords = pickup_data['features'][0]['geometry']['coordinates']

        # Get coordinates for dropoff location
        dropoff_response = requests.get(geocode_url, headers=headers, params={"text": dropoff_location})
        dropoff_response.raise_for_status()
        dropoff_data = dropoff_response.json()
        dropoff_coords = dropoff_data['features'][0]['geometry']['coordinates']

        # Calculate distance between coordinates
        directions_response = requests.post(
            directions_url,
            headers=headers,
            json={
                "coordinates": [pickup_coords, dropoff_coords]
            }
        )
        directions_response.raise_for_status()
        directions_data = directions_response.json()
        distance_meters = directions_data['routes'][0]['summary']['distance']
        distance_miles = distance_meters / 1609.34

        return round(distance_miles, 2)

    except (IndexError, KeyError, requests.RequestException) as e:
        print(f"Error calculating distance: {e}")
        flash("Service error while calculating distance. Please try again later.", "danger")
        return 0

# ----------------- Home Route -----------------
@app.route('/')
def home():
    return render_template('index.html')

# ----------------- Registration & Login -----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        email = request.form['email']
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', (username, password, email))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash('Username or email already exists. Please try another one.', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Login successful!', 'success')
            return redirect(url_for('customer_portal'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

# ----------------- Place Order -----------------
@app.route('/place_order', methods=['GET', 'POST'])
def place_order():
    if request.method == 'POST':
        pickup_location = request.form['pickup_location']
        pickup_floors = int(request.form['pickup_floors'])
        dropoff_location = request.form['dropoff_location']
        dropoff_floors = int(request.form['dropoff_floors'])
        pickup_date = request.form['pickup_date']
        pickup_time = request.form['pickup_time']
        items_count = int(request.form['items_count'])
        item_type = request.form['item_type']
        distance = calculate_distance(pickup_location, dropoff_location)
        total_price = calculate_price(distance, items_count, item_type, pickup_floors, dropoff_floors)

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO bookings (customer_username, pickup_location, pickup_floors, dropoff_location, dropoff_floors, pickup_date, pickup_time, items_count, item_type, distance, total_price, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
            (session['username'], pickup_location, pickup_floors, dropoff_location, dropoff_floors, pickup_date, pickup_time, items_count, item_type, distance, total_price, 'Pending'))
        booking_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('order_summary', booking_id=booking_id))
    return render_template('new_booking.html')

# ----------------- Order Summary -----------------
@app.route('/order_summary/<int:booking_id>')
def order_summary(booking_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id = %s', (booking_id,))
    booking = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('order_summary.html', booking=booking)

# ----------------- PDF Invoice -----------------
@app.route('/generate_invoice/<int:booking_id>')
def generate_invoice(booking_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id = %s', (booking_id,))
    booking = cursor.fetchone()
    cursor.close()
    conn.close()

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 750, "MoVan & Man - Invoice")
    p.setFont("Helvetica", 12)
    p.drawString(100, 720, f"Booking ID: {booking[0]}")
    p.drawString(100, 700, f"Pickup Location: {booking[2]}")
    p.drawString(100, 680, f"Dropoff Location: {booking[3]}")
    p.drawString(100, 660, f"Total Price: £{booking[10]}")

    p.showPage()
    p.save()

    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=invoice_{booking_id}.pdf'
    return response

# ----------------- Price Calculation -----------------
def calculate_price(distance, items_count, item_type, pickup_floors, dropoff_floors):
    base_price = 50 if distance < 30 else (100 if distance < 100 else 320)
    item_charge = items_count * (5 if item_type == 'small' else 10)
    floor_charge = 10 * (pickup_floors + dropoff_floors)
    return base_price + item_charge + floor_charge

# ----------------- Hash Password -----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ----------------- Run the App -----------------
if __name__ == '__main__':
    app.run(debug=True)
