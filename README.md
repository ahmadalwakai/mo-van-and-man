
# mo-van-and-man


# Mo Van and Man

A web application to manage delivery services, customer orders, and real-time chat functionality. The project includes user registration, login, order placement, and chat features with cash and card payment options.

## Features
- User registration and login
- Real-time chat with image uploads
- Order placement with pickup and dropoff locations
- Cash and card payment methods
- Email notifications for account confirmation and invoices
- Distance-based pricing calculations

## Project Structure
```
mo-van-and-man/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   └── utils/
│       ├── helpers.py
│       └── send_order_invoice.py
├── migrations/                # Database migration files
├── static/
│   └── uploads/               # Uploaded images
├── templates/                 # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   └── place_order.html
├── manage.py                  # Script to manage database migrations
├── config.py                  # Configuration settings
├── requirements.txt           # Python package dependencies
└── README.md                  # Project documentation
```

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/mo-van-and-man.git
   cd mo-van-and-man
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   export SECRET_KEY='your_secret_key'
   export MAIL_USERNAME='your_email@example.com'
   export MAIL_PASSWORD='your_email_password'
   ```
4. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
5. Run the application:
   ```bash
   flask run
   ```

## Technologies Used
- Flask
- SQLAlchemy
- Flask-Migrate
- Flask-Mail
- Flask-SocketIO
- Geopy
- FPDF

## License
This project is licensed under the MIT License.
>>>>>>> ccd1865 (First commit)
