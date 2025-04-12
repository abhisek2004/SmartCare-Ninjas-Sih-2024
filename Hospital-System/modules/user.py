from flask import request, session, redirect, flash, render_template, Blueprint, jsonify
from flask_bcrypt import Bcrypt
from modules.db import users_collection, appointment_collection, hospital_data_collection, doctors_collection, feedback_collection
from datetime import datetime, timedelta
from modules.login_required import login_required

user_blueprint = Blueprint('user_blueprint', __name__)
bcrypt = Bcrypt()


@user_blueprint.route('/user_login', methods=['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user by username
        user = users_collection.find_one({'username': username})

        if user:
            # Compare the entered password with the stored hashed password
            if bcrypt.check_password_hash(user['password'], password):
                session['username'] = username
                session['role'] = 'user'
                print(f'user session details:{session}')
                return redirect('/user_app')
            else:
                flash('Incorrect Password', 'error')
                return redirect('/user_login')

        else:
            flash('User not found', 'error')
            return redirect('/user_login')

    return render_template('user_login_register.html')


@user_blueprint.route('/user_app', methods=['GET', 'POST'])
@login_required('user')
def user_app():
    user_info = users_collection.find_one(
        {'username': session.get('username')})
    appointment = appointment_collection.find(
        {'username': session.get('username')})
    return render_template('user_app.html', user=user_info, appointments=appointment)


@user_blueprint.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        print("HEllo from user regiostration .........................")
        name = request.form['name']
        number = request.form['phone']
        email = request.form['email']
        user_name = request.form['username'].strip()

        existing_user = users_collection.find_one({'username': user_name})
        existing_email = users_collection.find_one({'email': email})

        if existing_user:
            return 'Username already exists. Please choose a different username.'

        if existing_email:
            return 'Email already exists. Please use a different email address.'
        pa = request.form['password']
        password = bcrypt.generate_password_hash(pa).decode('utf-8')
        user_data = {
            'name': name,
            'username': user_name,
            'email': email,
            'number': number,
            'password': password
        }
        users_collection.insert_one(user_data)
        return redirect('/user_login')
    return render_template('user_login_register.html')


@user_blueprint.route('/appointment', methods=['POST', 'GET'])
@login_required('user')
def appointment():
    if request.method == 'POST':
        # Extract form data
        name = request.form['name']
        user_name = session.get('username')
        number = request.form['number']
        email = request.form['email']
        address = request.form['Address']
        appointment_date = request.form['dat']
        time_slot = request.form['timeSlot']
        speciality = request.form['specialization']
        disease_description = request.form['diseaseDescription']
        hospital_name = request.form['hospital']
        doctorname = request.form['doctor']

        # Fetch doctor names based on selected hospital and specialization
        doctor_names = doctors_collection.find(
            {'hospital_name': hospital_name, 'specialization': speciality})
        doctor_names_list = [doctor['name'] for doctor in doctor_names]

        # Check if the selected time slot is available
        is_slot_full = check_and_allocate_time_slot(
            appointment_date, time_slot, hospital_name, speciality)
        print("Is slot full", is_slot_full)

        doctor_count = len(doctor_names_list)
        print("Doctor count:", doctor_count)
        print("Speciality:", speciality)

        if not doctor_count:
            flash(
                f'Doctor for the selected field is not available in {hospital_name}. Sorry for the inconvenience', 'error')
            return redirect('/appointment')

        if is_slot_full:
            flash(
                'The selected time slot is full. Please choose another time or date.', 'error')
            return redirect('/appointment')

        queue_number = calculate_queue_number(
            appointment_date, time_slot, hospital_name, speciality)
        print("Queue number:", queue_number)

        # Store the appointment in the database
        appointment_data = {
            'name': name,
            'username': user_name,
            'number': number,
            'email': email,
            'address': address,
            'appointment_date': appointment_date,
            'time_slot': time_slot,
            'speciality': speciality,
            'disease_description': disease_description,
            'hospital_name': hospital_name,
            'queue_number': queue_number,
            'appointed_doc': doctorname
        }
        appointment_collection.insert_one(appointment_data)

        # After saving, redirect to the confirmation page
        return redirect('/confirmation')

    # If GET request, render the appointment form

    hospitals = hospital_data_collection.find()
    hospital_names = [hospital['hospital_name'] for hospital in hospitals]

    today = datetime.today().strftime('%Y-%m-%d')
    max_date = (datetime.today() + timedelta(days=15)).strftime('%Y-%m-%d')

    return render_template('appointment.html', hospitals=hospital_names, today=today, max_date=max_date)


def add_days(date, days):
    return (date + timedelta(days=days)).strftime('%Y-%m-%d')

# Route to book an appointment

# New route to handle AJAX request for fetching doctors


@user_blueprint.route('/get_doctors/<hospital>/<speciality>', methods=['GET'])
@login_required('user')
def get_doctors(hospital, speciality):
    # Log the incoming values
    print(
        f"Fetching doctors for hospital: {hospital}, specialization: {speciality}")

    # Fetch doctors based on the hospital and specialization
    doctor_names = doctors_collection.find(
        {'hospital_name': hospital, 'specialization': speciality})

    # Log the result from the query
    doctor_names_list = [doctor['name'] for doctor in doctor_names]
    print(f"Found doctors: {doctor_names_list}")

    # Return the list of doctors in JSON format
    if doctor_names_list:
        return jsonify({'doctors': doctor_names_list})
    else:
        # Log if no doctors are found
        print("No doctors found for the given hospital and specialization")
        return jsonify({'doctors': []})

# This is the queueing system for the appiontments:


def check_and_allocate_time_slot(appointment_date, time_slot, hospital_name, speciality):
    # Check the number of appointments in the given time slot
    print('check_and_allocate_time_slot is called')
    doctor_count = doctors_collection.count_documents(
        {'hospital_name': hospital_name, 'specialization': speciality})
    print(doctor_count)

    # Convert to datetime object
    print("Date:", appointment_date)
    print(
        f"Checking for date: {appointment_date}, time slot: {time_slot}, hospital: {hospital_name}")
    count = appointment_collection.count_documents({
        'appointment_date': appointment_date,
        'time_slot': time_slot,
        'hospital_name': hospital_name,
        'speciality': speciality
    })
    print("appointment count on that day:", count)
    # Return True if the slot is full
    return count >= 3 * doctor_count


def calculate_queue_number(appointment_date, time_slot, hospital_name, speciality):
    # Count how many appointments have already been booked for the same slot

    count = appointment_collection.count_documents({
        'appointment_date': appointment_date,
        'time_slot': time_slot,
        'hospital_name': hospital_name,
        'speciality': speciality
    })

    return count + 1


@user_blueprint.route('/get_specializations', methods=['GET'])
def get_specializations():
    # Get hospital name from query parameter
    hospital_name = request.args.get('hospital_name')

    # Find hospital data in MongoDB
    hospital_data = hospital_data_collection.find_one(
        {"hospital_name": hospital_name})
    if hospital_data:
        specializations = hospital_data.get('specialization', [])
        return jsonify({"specializations": specializations})
    else:
        return jsonify({"error": "Hospital not found"}), 404
