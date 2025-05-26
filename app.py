import pandas as pd
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "secret_key_for_session" 

donor_data = pd.DataFrame(columns=["Name", "Blood Type", "Location", "Contact"])
credentials_file = "user_credentials.csv"
donor_file = "donor_data.csv"


def load_credentials():
    global valid_credentials
    valid_credentials = {}
    if os.path.exists(credentials_file):
        df = pd.read_csv(credentials_file)
        for _, row in df.iterrows():
            valid_credentials[row["Username"]] = row["Password"]

def save_credentials():
    df = pd.DataFrame(valid_credentials.items(), columns=["Username", "Password"])
    df.to_csv(credentials_file, index=False)

def add_donor(name, blood_type, location, contact):
    global donor_data
    if name and blood_type and location and contact:
        new_donor = pd.DataFrame([{"Name": name, "Blood Type": blood_type, "Location": location, "Contact": contact}])
        donor_data = pd.concat([donor_data, new_donor], ignore_index=True)
        save_donor_data()
        return True
    else:
        return False

def save_donor_data():
    donor_data.to_csv(donor_file, index=False)

def load_donor_data():
    global donor_data
    if os.path.exists(donor_file):
        donor_data = pd.read_csv(donor_file)

def display_donors():
    global donor_data
    return donor_data.to_dict(orient="records")

def validate_login(username, password):
    return username in valid_credentials and valid_credentials[username] == password

def create_user(username, password, confirm_password):
    global valid_credentials
    if password == confirm_password:
        if username not in valid_credentials:
            valid_credentials[username] = password
            save_credentials()
            return True
    return False


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/test')
def test():
    load_donor_data()
    search_query = request.args.get('search', '').strip().lower()
    if search_query:
        filtered_donors = [
            donor for donor in display_donors() if
            search_query in donor['Name'].lower() or
            search_query in donor['Blood Type'].lower() or
            search_query in donor['Location'].lower()
        ]
    else:
        filtered_donors = display_donors()

    return render_template('donor_data.html', donors=filtered_donors, search_query=search_query)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_login(username, password):
            return redirect(url_for('dashboard'))
    else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if create_user(username, password, confirm_password):
            flash(f"User {username} created successfully!", 'success')
            return redirect(url_for('login'))
        else:
            flash('Error creating account. Passwords may not match or username exists.', 'danger')
    return render_template('create_account.html')


@app.route('/donor_data', methods=['GET', 'POST'])
def donor_data():
    load_donor_data()
    search_query = request.args.get('search', '').strip().lower()
    if search_query:
        filtered_donors = [
            donor for donor in display_donors() if
            search_query in donor['Name'].lower() or
            search_query in donor['Blood Type'].lower() or
            search_query in donor['Location'].lower()
        ]
    else:
        filtered_donors = display_donors()

    return render_template('donor_data.html', donors=filtered_donors, search_query=search_query)


@app.route('/edit_donor/<int:index>', methods=['GET', 'POST'])
def edit_donor(index):
    load_donor_data()
    if request.method == 'POST':
        name = request.form['name']
        blood_type = request.form['blood_type']
        location = request.form['location']
        contact = request.form['contact']
        if name and blood_type and location and contact:
            donor_data.loc[index] = [name, blood_type, location, contact]
            save_donor_data()
            flash('Donor updated successfully!', 'success')
            return redirect(url_for('donor_data'))
        else:
            flash('Please fill in all fields.', 'danger')
    donor = donor_data.iloc[index].to_dict()
    return render_template('edit_donor.html', donor=donor, index=index)


@app.route('/delete_donor/<int:index>', methods=['POST'])
def delete_donor(index):
    load_donor_data()
    donor_data.drop(index, inplace=True)  
    donor_data.reset_index(drop=True, inplace=True) 
    save_donor_data()
    flash('Donor deleted successfully!', 'success')
    return redirect(url_for('donor_data'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    load_donor_data()
    if request.method == 'POST':
        name = request.form['name']
        blood_type = request.form['blood_type']
        location = request.form['location']
        contact = request.form['contact']
        if add_donor(name, blood_type, location, contact):
            flash('Donor added successfully!', 'success')
        else:
            flash('Please fill in all fields.', 'danger')

    donors = display_donors()
    return render_template('dashboard.html', donors=donors)


if __name__ == '__main__':
    load_credentials()
    app.run(host='0.0.0.0', port=5000, debug=True)

