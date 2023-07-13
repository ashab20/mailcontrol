from flask import Flask, render_template, request, redirect, session
import mysql.connector
import imaplib
import email
from email.header import decode_header
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ashabu',
    'database': 'pymail'
}
def get_email_data():
    IMAP_SERVER = 'imap.gmail.com'
    IMAP_PORT = 993
    IMAP_USERNAME = os.getenv('IMAP_USERNAME')
    IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')

    imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    imap.login(IMAP_USERNAME, IMAP_PASSWORD)
    imap.select('INBOX')

    _, message_ids = imap.search(None, 'ALL')
    message_ids = message_ids[0].split()

    email_data = []
    for message_id in message_ids:
        _, message_data = imap.fetch(message_id, '(RFC822)')
        raw_email = message_data[0][1]
        email_message = email.message_from_bytes(raw_email)
        subject = decode_header(email_message['Subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode('utf-8')
        
        sender = email_message['From']
        date = email_message['Date']

        email_data.append({'subject': subject, 'sender': sender, 'date': date})
        print(subject)

    imap.logout()
    return email_data

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Hash the password (bcrypt or any other secure hashing algorithm)
        # Save the hashed password and other user details to the MySQL database

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Authenticate with MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()

        if user:
            session['email'] = email
            session['password'] = password

            return redirect('/mails')
        else:
            return "Invalid credentials"

    return render_template('login.html')

@app.route('/mails')
def mails():
    if 'email' in session and 'password' in session:
        email_data = get_email_data()
        return render_template('mails.html', email_data=email_data)
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
