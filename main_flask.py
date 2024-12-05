from flask import Flask, render_template, request, flash, redirect, url_for
import web_data
import secrets  # Import secrets module for generating a secure key

app = Flask(__name__)

# Set a secret key for sessions and flash messages
app.secret_key = secrets.token_hex(16)  # Generate a random 32-character key

data = web_data
data.web.create_db()
#data.user.add(0, "admin", "admin")
data.user.update("admin", 1, "newpass")
#data.user_details.add(1, 'John', 'Doe', 'john.doe@example.com', '1234567890')
data.user_details.update(1, email='john.newemail@example.com')

@app.route('/')
def home():
    return render_template('index.html', title='Home')

@app.route('/about')
def about():
    return render_template('index.html', title='About')

@app.route('/login')
def login():
    return render_template('index.html', title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate form inputs
        if not all([first_name, last_name, email, username, password, confirm_password]):
            flash("All fields are required.", "error")
            return redirect(url_for('register'))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('register'))

        # Add logic to save user to the database
        data.user.add(1, username, password)
        user_id = data.user.get_by_username(username)[0]
        data.user_details.add(user_id, first_name, last_name, email)
        # Example: Save data (replace with your database interaction logic)
        print(f"First Name: {first_name}, Last Name: {last_name}, Email: {email}, "
              f"Username: {username}, Password: {password}")

        # Redirect or show a success message
        flash("Registration successful!", "success")
        return redirect(url_for('home'))

    # Render the registration form for GET request
    return render_template('index.html', title='Register')

if __name__ == '__main__':
    app.run(debug=False)
