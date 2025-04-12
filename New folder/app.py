from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, redirect
from modules.log_out import logout_bp
from modules.admin import admin_blueprint
from modules.superadmin import superadmin_blueprint
from modules.doctor import doctor_blueprint
from modules.db import contact_collection, feedback_collection
from modules.user import user_blueprint

app = Flask(__name__)
app.register_blueprint(logout_bp)
app.register_blueprint(admin_blueprint)
app.register_blueprint(doctor_blueprint)
app.register_blueprint(superadmin_blueprint)
app.register_blueprint(user_blueprint)
bcrypt = Bcrypt()
app.secret_key = "anything_secret_is_good"


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/contact', methods=['GET', 'POST'])
def landing():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        number = request.form['phone']
        city = request.form['city']
        nearest_hospial = request.form['nearest_hospital']
        subject = request.form['subject']
        message = request.form['message']
        contact_data = {
            'name': name,
            'email': email,
            'number': number,
            'city': city,
            'nearest_hospital': nearest_hospial,
            'message': message,
            'subject': subject
        }
        contact_collection.insert_one(contact_data)
    return render_template('contact.html')


@app.route('/all_doctor')
def all_doc():
    return render_template('doctor.html')


@app.route('/confirmation', methods=['POST', 'GET'])
def confirmation():
    return render_template('conformation.html')


@app.route('/stock_detail')
def detail():
    return render_template('inv_stock_product.html')


@app.route('/home_feedback', methods=['POST'])
def feedback():
    name = request.form['name']
    email = request.form['email']
    city = request.form['city']
    nearest_hospital = request.form['nearest_hospital']
    message = request.form['message']

    data = {
        'name': name,
        'email': email,
        'city': city,
        'nearest_hospital': nearest_hospital,
        'message': message
    }
    feedback_collection.insert_one(data)
    return redirect('/')


@app.route('/blog', methods=['GET', 'POST'])
def blog_single():
    return render_template('blog-single.html')


# a customized error handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(port=8000, debug=True)
