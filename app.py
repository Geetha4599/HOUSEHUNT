from flask import Flask, render_template, request, redirect, flash, session, url_for
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import os

# MongoDB connection
client = MongoClient("mongodb+srv://admin:Secret%409@cluster0.8ejfhrg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["househunt"]
users_collection = db["users"]
properties_collection = db["properties"]

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from flask import Flask
app=Flask(__name__)
@app.route('/')
def home():
    query = {}
    location = request.args.get('location')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    if location:
        query['location'] = {'$regex': location, '$options': 'i'}

    try:
        price_filter = {}
        if min_price:
            price_filter['$gte'] = int(min_price)
        if max_price:
            price_filter['$lte'] = int(max_price)
        if price_filter:
            query['price'] = price_filter
    except ValueError:
        flash("Please enter valid price values.", "error")

    properties = list(properties_collection.find(query))
    return render_template('properties.html', properties=properties)
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        image = request.files['image']

        try:
            raw_price = request.form['price']
            clean_price = int(raw_price.replace('₹', '').replace(',', '').strip())
        except ValueError:
            flash("Invalid price. Please enter a number.", "error")
            return redirect(url_for('upload'))

        filename = None
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))

        property_data = {
            'title': title,
            'description': description,
            'price': clean_price,
            'location': location,
            'image': filename,
            'posted_by': session['user_email']
        }

        properties_collection.insert_one(property_data)
        flash('Property uploaded successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('upload.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})

        if not email or not password:
            flash('Please fill in all fields.', 'error')
        elif user and user['password'] == password:
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash(f"Welcome, {user['name']}!", 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if not name or not email or not password:
            flash('All fields are required.', 'error')
        elif users_collection.find_one({'email': email}):
            flash('Email already registered.', 'error')
        else:
            users_collection.insert_one({
                'name': name,
                'email': email,
                'password': password
            })
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
