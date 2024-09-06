from bson import ObjectId
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
import smtplib
from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, make_response, session, send_file, after_this_request
import os
import secrets
from pymongo import MongoClient
import jwt
from functools import wraps
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import qrcode
import io
from log_out import logout_bp

# test pull
app = Flask(__name__)
app.register_blueprint(logout_bp)
# test push
# app.config['SECRET_KEY']=secrets.token_hex()\
app.secret_key = secrets.token_hex()

my_email = "nicdelhi2024@gmail.com"
code = "zuff vkvx pamt kdor"
bcrypt = Bcrypt(app)
uri = "mongodb+srv://manasranjanpradhan2004:root@hms.m7j9t.mongodb.net/?retryWrites=true&w=majority&appName=HMS"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client['HMS']
patients_collection = db['patients']
doctors_collection = db['doctors']
users_collection = db['users']
admin_collection = db['admin']
appointment_collection = db['appointment']
contact_collection = db['contact']
superadmin_collection = db['Superadmin']
hospital_data_collection = db['hospital_data']
hospital_discharge_collection = db['discharged']
inventory_collection = db['inventory']
stock_collection = db['stock']

today_date = datetime.today().strftime('%Y-%m-%d')
# Query to find documents where the date is less than today
query = {'appointment_date': {'$lt': today_date}}

# Delete the matching documents
result = appointment_collection.delete_many(query)

print(f"Deleted {result.deleted_count} appointments.")



# def token_required(expected_role):
#     def decorator(f):
#         @wraps(f)
#         def decorated(*args,**kwargs):
#             if expected_role=='user':
#                 token=request.cookies.get('access_token_user')
#             else:
#                 token=request.cookies.get('access_token_admin')
#             if not token:
#                 return redirect('/user_login')

#             try:
#                 data=jwt.decode(token,app.config['SECRET_KEY'],algorithms=["HS256"])
#                 current_user=data['user_username']
#                 role=data.get('role')
#                 print(role)

#                 if role!=expected_role:
#                     return redirect(f'/{expected_role}_login')
#             except jwt.ExpiredSignatureError:
#                 return 'Token has expired',401

#             except jwt.InvalidTokenError:
#                 return redirect(f'/{expected_role}_login')

#             return f(current_user,*args,**kwargs)
#         return decorated
#     return decorator
def login_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print(f"Session data: {session}")
            print(f"Checking if username in session: {'username' in session}")
            print(f"Checking if role matches: {session.get('role')} == {role}")
            if 'username' not in session or session.get('role') != role:
                return redirect(f'/{role}_login')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/', methods=['GET', 'POST'])
def landing():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        number = request.form['number']
        comment = request.form['comment']
        contact_data = {
            'name': name,
            'email': email,
            'number': number,
            'comment': comment
        }
        contact_collection.insert_one(contact_data)
    return render_template('index.html')


@app.route('/user_login', methods=['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user by username
        user = users_collection.find_one({'username': username})

        if user:
            # Compare the entered password with the stored hashed password
            if bcrypt.check_password_hash(user['password'], password):
                # token=jwt.encode({
                #     'user_username':username,
                #     'role':'user',
                #     'exp':datetime.utcnow()+timedelta(hours=1)
                # },app.config['SECRET_KEY'],algorithm="HS256")
                # response=make_response(redirect('/appointment'))
                # response.set_cookie('access_token_user',token,httponly=True)
                # response.set_cookie('user_username',username,httponly=True)

                # return response
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

    return render_template('user_login.html')


@app.route('/user_app', methods=['GET', 'POST'])
@login_required('user')
def user_app():
    user_info = users_collection.find_one(
        {'username': session.get('username')})
    appointment = appointment_collection.find(
        {'username': session.get('username')})
    return render_template('user_app.html', user=user_info, appointments=appointment)


@app.route('/user_register', methods=['GET', 'POST'])
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
    return render_template('user register.html')


@app.route('/all_doctor')
def all_doc():
    return render_template('doctor.html')

def add_days(date, days):
    return (date + timedelta(days=days)).strftime('%Y-%m-%d')

# Route to book an appointment
@app.route('/appointment', methods=['POST', 'GET'])
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
        speciality = request.form['diseaseInput']
        disease_description = request.form['diseaseDescription']
        hospital_name = request.form['hospital']
        doctorname = request.form['doctor']

        # Fetch doctor names based on selected hospital and specialization
        doctor_names = doctors_collection.find({'hospital_name': hospital_name, 'specialization': speciality})
        doctor_names_list = [doctor['name'] for doctor in doctor_names]

        # Check if the selected time slot is available
        is_slot_full = check_and_allocate_time_slot(appointment_date, time_slot, hospital_name, speciality)
        print(is_slot_full)
        
        doctor_count = len(doctor_names_list)
        print(doctor_count)
        print(speciality)
        
        if not doctor_count:
            flash(f'Doctor for the selected field is not available in {hospital_name}. Sorry for the inconvenience', 'error')
            return redirect('/appointment')
        
        if is_slot_full:
            flash('The selected time slot is full. Please choose another time or date.', 'error')
            return redirect('/appointment')
        
        queue_number = calculate_queue_number(appointment_date, time_slot, hospital_name, speciality)
        print(queue_number)
        
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


# New route to handle AJAX request for fetching doctors
@app.route('/get-doctors/<hospital>/<speciality>', methods=['GET'])
@login_required('user')
def get_doctors(hospital, speciality):
    # Log the incoming values
    print(f"Fetching doctors for hospital: {hospital}, specialization: {speciality}")

    # Fetch doctors based on the hospital and specialization
    doctor_names = doctors_collection.find({'hospital_name': hospital, 'specialization': speciality})

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
    print(appointment_date)
    print(f"Checking for date: {appointment_date}, time slot: {time_slot}, hospital: {hospital_name}")
    count = appointment_collection.count_documents({
        'appointment_date': appointment_date,
        'time_slot': time_slot,
        'hospital_name': hospital_name,
        'speciality': speciality
    })
    print(count)
    # Return True if the slot is full
    return count >= 3*int(doctor_count/3)


def calculate_queue_number(appointment_date, time_slot, hospital_name, speciality):
    # Count how many appointments have already been booked for the same slot

    count = appointment_collection.count_documents({
        'appointment_date': appointment_date,
        'time_slot': time_slot,
        'hospital_name': hospital_name,
        'speciality': speciality
    })

    return count+1


@app.route('/confirmation', methods=['POST', 'GET'])
def conform():
    return render_template('conformation.html')


@app.route('/admin/add_patient', methods=['GET', 'POST'])
# @token_required('admin')
@login_required('admin')
def add_patient():
    if request.method == 'POST':
        name = request.form['Name']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        aadhaar = request.form['aadhaar']
        bed_type = request.form['bedtype']
        bed_no = request.form['bedno']

        session['bed_type'] = bed_type
        session['patient_name'] = name
        hospital_name_patient = session.get('hospital_name')
        if bed_type == 'general':
            data = {
                'name': name,
                'dob': dob,
                'gender': gender,
                'address': address,
                'phone': phone,
                'email': email,
                "aadhaar": aadhaar,
                "bed_type": bed_type,
                "bed no": "G"+bed_no,
                "hospital_name": hospital_name_patient
            }
        elif bed_type == 'icu':
            data = {
                'name': name,
                'dob': dob,
                'gender': gender,
                'address': address,
                'phone': phone,
                'email': email,
                "aadhaar": aadhaar,
                "bed_type": bed_type,
                "bed no": "I"+bed_no,
                "hospital_name": hospital_name_patient
            }

        else:
            data = {
                'name': name,
                'dob': dob,
                'gender': gender,
                'address': address,
                'phone': phone,
                'email': email,
                "aadhaar": aadhaar,
                "bed_type": bed_type,
                "bed no": "V"+bed_no,
                "hospital_name": hospital_name_patient
            }

        print(hospital_name_patient)

        patients_collection.insert_one(data)

        hospital_data_collection.update_one(
            {'hospital_name': hospital_name_patient},
            # Increment the occupied beds count by 1
            {'$inc': {f'occupied_{bed_type}': 1}}
        )
        return redirect(url_for('confirmation'))
    return render_template('add patient.html')


@app.route('/admin/patient_details', methods=['GET', 'POST'])
@login_required('admin')
def patient_details():
    patients = patients_collection.find(
        {'hospital_name': session.get('hospital_name')})
    return render_template('manage_patient.html', patients=patients)


@app.route('/admin/confirmation')
@login_required('admin')
def confirmation():
    return render_template('success_admin.html')


@app.route('/admin/manage_appointment', methods=['GET', 'POST'])
@login_required('admin')
def manage():
    hospital_name = session.get('hospital_name')
    appointments = appointment_collection.find(
        {"hospital_name": hospital_name})
    return render_template('manage_appointment.html', appointments=appointments)


@app.route('/admin_login', methods=["GET", "POST"])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        pa = request.form['password']
        password = bcrypt.generate_password_hash(pa).decode('utf-8')
        # print('this is executed')

        admin = admin_collection.find_one({'hospital_mail': username})
        if admin:
            # Compare the entered password with the stored hashed password
            if bcrypt.check_password_hash(admin['hospital_password'], pa):
                # print('this is executed')
                # token=jwt.encode({
                #     'user_username':username,
                #     'role':'admin',
                #     'exp':datetime.utcnow()+timedelta(hours=1)
                # },app.config['SECRET_KEY'],algorithm="HS256")

                # response=make_response(redirect('/admin'))
                # response.set_cookie('access_token',token,httponly=True)
                # response.set_cookie('user_username',username,httponly=True)
                session['username'] = username
                session['role'] = 'admin'
                admin_email = session['username']
                hospital_data = admin_collection.find_one(
                    {"hospital_mail": admin_email})
                hospital_name_doctor = hospital_data.get("hospital_name")
                session['hospital_name'] = hospital_name_doctor
                print(f'session details:{session}')
                # return response
                return redirect('/admin')

            else:
                flash('Wrong Password', 'error')
                return redirect('/admin_login')

        else:
            flash('User not found', 'error')
            return redirect('/admin_login')
    return render_template("login_admin.html")


@app.route('/admin/', methods=['GET', 'POST'])
# @token_required('admin')
@login_required('admin')
def admin():
    hospital_name = session.get('hospital_name')
    print(hospital_name)
    total_appointment = appointment_collection.count_documents(
        {"hospital_name": hospital_name})
    data = hospital_data_collection.find_one({'hospital_name': hospital_name})
    if data:
        g_beds = data['number_of_general_beds']
        vacent_general = g_beds-data['occupied_general']
        icu_beds = data['number_of_icu_beds']
        vacent_icu = icu_beds-data['occupied_icu']
        v_beds = data['number_of_ventilators']
        vacent_ventilator = v_beds-data['occupied_ventilator']
        total_patient = patients_collection.count_documents(
            {'hospital_name': hospital_name})
        total_doc = doctors_collection.count_documents(
            {"hospital_name": hospital_name})
        nurses = data['total_number_of_nurses']
        staff = data['administrative_staff_count']

        return render_template('admin_dashboard.html', count=total_appointment, general_total=g_beds, icu_total=icu_beds, vantilator_total=v_beds, patient=total_patient, doc=total_doc,
                               vacent_general=vacent_general, vacent_icu=vacent_icu, vacent_ventilator=vacent_ventilator, hospital_name=hospital_name, nurses=nurses, staff=staff)
    else:
        return redirect('/admin/add_detail')


@app.route("/admin/contact-us")
@login_required('admin')
def admin_contact_us():
    contacts = contact_collection.find()
    return render_template("manage_appointment.html", contacts=contacts)


@app.route('/admin/add_detail', methods=['GET', 'POST'])
@login_required('admin')
def add_details():
    if request.method == 'POST':
        name = request.form['hospitalName']
        ID = request.form['hospitalID']
        address1 = request.form['addressLine1']
        city = request.form['city']
        state = request.form['stateProvince']
        postal_code = request.form['postalCode']
        contact_number = request.form['contactNumber']
        emergency = request.form['emergencyContactNumber']
        email = request.form['emailAddress']
        website = request.form['websiteURL']
        no_beds = int(request.form['numberOfBeds'])
        occupied_beds = int(request.form['Beds_occupied'])
        no_icu = int(request.form['numberOfICUBeds'])
        occupied_icu = int(request.form['icu_occupied'])
        no_ventilator = int(request.form['numberOfVentilators'])
        occupied_ventilator = int(request.form['ventilator_occupied'])
        emergency_dept = request.form['emergencyDepartment']
        spetialisation = request.form['specialization']
        operating_hour = request.form['hospitalOperatingHours']
        visiting_hour = request.form['visitingHours']
        pharmacy_onsite = request.form['pharmacyOnSite']
        no_nurse = int(request.form['totalNumberOfNurses'])
        no_admin_staff = int(request.form['administrativeStaffCount'])
        ambulance = request.form['ambulanceServices']
        bload_bank = request.form['bloodBank']
        diagonis_services = request.form['diagnosticServices']

        data = {
            "hospital_name": name,
            "hospital_id": ID,
            "address_line1": address1,
            "city": city,
            "state": state,
            "postal_code": postal_code,
            "contact_number": contact_number,
            "emergency_contact_number": emergency,
            "email_address": email,
            "website_url": website,
            "number_of_general_beds": no_beds,
            "occupied_general": occupied_beds,
            "number_of_icu_beds": no_icu,
            "occupied_icu": occupied_icu,
            "number_of_ventilators": no_ventilator,
            "occupied_ventilator": occupied_ventilator,
            "emergency_department": emergency_dept,
            "specialization": spetialisation,
            "hospital_operating_hours": operating_hour,
            "visiting_hours": visiting_hour,
            "pharmacy_on_site": pharmacy_onsite,
            "total_number_of_nurses": no_nurse,
            "administrative_staff_count": no_admin_staff,
            "ambulance_services": ambulance,
            "blood_bank": bload_bank,
            "diagnostic_services": diagonis_services}

    # Insert the data into the hospital collection
        hospital_data_collection.insert_one(data)
        return redirect('/admin')
    return render_template('hospital_details.html',)


@app.route('/add_doc', methods=['POST', 'GET'])
# @token_required('admin')
@login_required('admin')
def doctor_register():
    if request.method == 'POST':
        name = request.form['doctor_name']
        specialization = request.form['specialization']
        qualification = request.form['qualification']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
        phone = request.form['phone']
        aadhar = request.form['aadhaar']
        # Doctor and hospital relation
        session['doctor_name'] = name
        admin_email = session['username']
        hospital_data = admin_collection.find_one(
            {"hospital_mail": admin_email})
        hospital_name_doctor = hospital_data.get("hospital_name")
        session['hospital_name'] = hospital_name_doctor

        # print(hospital_name_patient)
        doctor_data = {
            'name': name,
            'specialization': specialization,
            'qualification': qualification,
            'email': email,
            'username': username,
            'password': hash_password,
            'phone': phone,
            'aadhar': aadhar,
            "hospital_name": hospital_name_doctor
        }
        if doctors_collection.find_one({'username': username}) or doctors_collection.find_one({'email': email}):
            return redirect('/add_doc')
        else:
            doctors_collection.insert_one(doctor_data)
            return redirect('/admin')
        # return render_template('add doc.html')
    return render_template('add doc.html')


@app.route('/doctor_login', methods=['POST', 'GET'])
def doc_login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Fetch the doctor's details from the database by username
        doctor = doctors_collection.find_one({'username': username})
        # print(username,password)
        if doctor:
            # stored_hash = doctor['password']  # The stored hashed password

            # Check if the provided password matches the hashed passwor
            if bcrypt.check_password_hash(doctor['password'], password):
                # Password matches, grant access
                # Store doctor ID in session
                doctor_data = doctors_collection.find_one(
                    {'username': username})

                session['username'] = username
                session['hospital_name'] = doctor_data.get('hospital_name')
                session['specialization'] = doctor_data.get('specialization')
                session['role'] = 'doc'
                return redirect('/doctor_app')  # Redirect to the doctor app

            else:
                # Password does not match
                # flash('Invalid username or password', 'error')
                flash('Wrong Password', 'error')
                return redirect('/doctor_login')
        else:
            # Username not found
            flash('Username Not Found', 'error')
            return redirect('/user_login')

    # Render the login page if GET request
    # Replace with your login template
    return render_template('doctor login.html')


@app.route('/stock_detail')
def detail():
    return render_template('inv_stock_product.html')


@app.route('/doctor_app', methods=["POST", "GET"])
@login_required('doc')
def doctor_app():
    appointments = appointment_collection.find({'hospital_name': session.get(
        'hospital_name'), 'speciality': session.get('specialization')})
    doc_detail = doctors_collection.find_one(
        {'username': session.get('username')})
    return render_template('doctor_dash.html', appointments=appointments, doctor=doc_detail)


@app.route('/superadmin/', methods=['GET', 'POST'])
@login_required('superadmin')
def superadmin():
    no_of_hospital = len(hospital_data_collection.distinct("hospital_name"))
    total_doctor = len(doctors_collection.distinct("username"))
    active_patient = len(patients_collection.distinct("name"))

    total_beds_data = hospital_data_collection.aggregate([
        {
            "$group": {
                "_id": None,
                "total_beds": {"$sum": "$number_of_general_beds"},
                "total_occupied_beds": {"$sum": "$occupied_general"}
            }
        }
    ]).next()

    total_beds = total_beds_data.get('total_beds', 0)
    occupied_beds = total_beds_data.get('total_occupied_beds', 0)
    available_beds = total_beds - occupied_beds

    total_icu_beds_data = hospital_data_collection.aggregate([
        {
            "$group": {
                "_id": None,
                "total_icu_beds": {"$sum": "$number_of_icu_beds"},
                "total_occupied_icu_beds": {"$sum": "$occupied_icu"}
            }
        }
    ]).next()
    total_nurse_data = hospital_data_collection.aggregate([
        {
            "$group": {
                "_id": None,
                "total_nurse": {"$sum": "$total_number_of_nurses"},
            }
        }
    ]).next()
    total_admin_staff = hospital_data_collection.aggregate([
        {
            "$group": {
                "_id": None,
                "total_adminstaff": {"$sum": "$administrative_staff_count"},
            }
        }
    ]).next()

    total_icu_beds = total_icu_beds_data.get('total_icu_beds', 0)
    occupied_icu_beds = total_icu_beds_data.get('total_occupied_icu_beds', 0)
    total_nurse = total_nurse_data.get('total_nurse')
    total_adminstaff = total_admin_staff.get('total_adminstaff')
    available_icu_beds = total_icu_beds - occupied_icu_beds

    total_ventilators_data = hospital_data_collection.aggregate([
        {
            "$group": {
                "_id": None,
                "total_ventilators": {"$sum": "$number_of_ventilators"},
                "total_occupied_ventilators": {"$sum": "$occupied_ventilator"}
            }
        }
    ]).next()

    total_ventilators = total_ventilators_data.get('total_ventilators', 0)
    occupied_ventilators = total_ventilators_data.get(
        'total_occupied_ventilators', 0)
    available_ventilators = total_ventilators - occupied_ventilators

    total_nurses = hospital_data_collection.aggregate([
        {
            "$group": {
                "_id": None,
                "total_nurses": {"$sum": "$total_number_of_nurses"}
            }
        }
    ]).next()
    total_nurses = total_nurses.get('total_nurses')

    total_staff = hospital_data_collection.aggregate([
        {
            "$group": {
                "_id": None,
                "total_staff": {"$sum": "$administrative_staff_count"}
            }
        }
    ]).next()
    total_staff = total_staff.get('total_staff')
    return render_template('super_admin_dash.html',
                           no_hospital=no_of_hospital,
                           doctor=total_doctor,
                           patient=active_patient,
                           total_beds=total_beds,
                           available_beds=available_beds,
                           total_icu_beds=total_icu_beds,
                           available_icu_beds=available_icu_beds,
                           total_ventilators=total_ventilators,
                           available_ventilators=available_ventilators,
                           total_adminstaff=total_adminstaff, total_nurse=total_nurse)


@app.route('/bed_status', methods=['GET', 'POST'])
def status():
    # Get list of hospitals for dropdown menu
    hospitals = hospital_data_collection.find()
    hospital_names = [hospital['hospital_name'] for hospital in hospitals]

    # Common data to be calculated
    no_of_hospital = len(hospital_data_collection.distinct("hospital_name"))
    total_doctor = len(doctors_collection.distinct("username"))
    active_patient = len(patients_collection.distinct("name"))

    if request.method == 'POST':
        hs_name = request.form.get('hs_name')
        query = {}

        if hs_name:
            query = {"hospital_name": hs_name}

        # General Beds
        total_beds_data = hospital_data_collection.aggregate([
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "total_beds": {"$sum": "$number_of_general_beds"},
                    "total_occupied_beds": {"$sum": "$occupied_general"}
                }
            }
        ])
        total_beds_data = next(total_beds_data, {})
        total_beds = total_beds_data.get('total_beds', 0)
        occupied_beds = total_beds_data.get('total_occupied_beds', 0)
        available_beds = total_beds - occupied_beds

        # ICU Beds
        total_icu_beds_data = hospital_data_collection.aggregate([
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "total_icu_beds": {"$sum": "$number_of_icu_beds"},
                    "total_occupied_icu_beds": {"$sum": "$occupied_icu"}
                }
            }
        ])
        total_icu_beds_data = next(total_icu_beds_data, {})
        total_icu_beds = total_icu_beds_data.get('total_icu_beds', 0)
        occupied_icu_beds = total_icu_beds_data.get('total_occupied_icu_beds', 0)
        available_icu_beds = total_icu_beds - occupied_icu_beds

        # Ventilators
        total_ventilators_data = hospital_data_collection.aggregate([
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "total_ventilators": {"$sum": "$number_of_ventilators"},
                    "total_occupied_ventilators": {"$sum": "$occupied_ventilator"}
                }
            }
        ])
        total_ventilators_data = next(total_ventilators_data, {})
        total_ventilators = total_ventilators_data.get('total_ventilators', 0)
        occupied_ventilators = total_ventilators_data.get('total_occupied_ventilators', 0)
        available_ventilators = total_ventilators - occupied_ventilators

    else:
        # Show overall status if no hospital is selected (GET request)
        total_beds_data = hospital_data_collection.aggregate([
            {
                "$group": {
                    "_id": None,
                    "total_beds": {"$sum": "$number_of_general_beds"},
                    "total_occupied_beds": {"$sum": "$occupied_general"}
                }
            }
        ]).next()

        total_beds = total_beds_data.get('total_beds', 0)
        occupied_beds = total_beds_data.get('total_occupied_beds', 0)
        available_beds = total_beds - occupied_beds

        total_icu_beds_data = hospital_data_collection.aggregate([
            {
                "$group": {
                    "_id": None,
                    "total_icu_beds": {"$sum": "$number_of_icu_beds"},
                    "total_occupied_icu_beds": {"$sum": "$occupied_icu"}
                }
            }
        ]).next()

        total_icu_beds = total_icu_beds_data.get('total_icu_beds', 0)
        occupied_icu_beds = total_icu_beds_data.get('total_occupied_icu_beds', 0)
        available_icu_beds = total_icu_beds - occupied_icu_beds

        total_ventilators_data = hospital_data_collection.aggregate([
            {
                "$group": {
                    "_id": None,
                    "total_ventilators": {"$sum": "$number_of_ventilators"},
                    "total_occupied_ventilators": {"$sum": "$occupied_ventilator"}
                }
            }
        ]).next()

        total_ventilators = total_ventilators_data.get('total_ventilators', 0)
        occupied_ventilators = total_ventilators_data.get('total_occupied_ventilators', 0)
        available_ventilators = total_ventilators - occupied_ventilators

    return render_template('bed_status.html',
                           hospitals = hospital_names,
                           no_hospital=no_of_hospital, 
                           doctor=total_doctor, 
                           patient=active_patient, 
                           total_general_beds=total_beds, 
                           available_beds=available_beds, 
                           total_icu_beds=total_icu_beds, 
                           available_icu_beds=available_icu_beds, 
                           total_ventilators=total_ventilators,
                           available_ventilators=available_ventilators)


# @app.route('/select_hs', methods=['GET', 'POST'])
# @login_required('user')
# def select():
#     if request.method == 'POST':
#         hospital_name = request.form['hname']
#         print(hospital_name)
#         if not hospital_name:
#             return "Hospital name is missing", 400  # Bad Request

#         data = hospital_data_collection.find_one(
#             {'hospital_name': hospital_name})

#         print(data)
#         if data:
#             total_general_beds = data.get('number_of_general_beds', 0)
#             occupied_general_beds = data.get('occupied_general', 0)
#             total_icu_beds = data.get('number_of_icu_beds', 0)
#             occupied_icu_beds = data.get('occupied_icu', 0)
#             total_ventilators = data.get('number_of_ventilators', 0)
#             occupied_ventilators = data.get('occupied_ventilator', 0)

#             # Calculate available beds
#             available_beds = total_general_beds - occupied_general_beds
#             available_icu_beds = total_icu_beds - occupied_icu_beds
#             available_ventilator = total_ventilators - occupied_ventilators
#             return render_template('bed_status.html', available_beds=available_beds, available_icu_beds=available_icu_beds, available_ventilators=available_ventilator, total_general_beds=total_general_beds, total_icu_beds=total_icu_beds, total_ventilators=total_ventilators)
#         else:
#             return "No hospital found"
#     hospitals = hospital_data_collection.find()
#     hospital_names = [hospital['hospital_name'] for hospital in hospitals]
#     return render_template('select_hs_for_beds.html', hospitals=hospital_names)


@app.route("/superadmin_login", methods=['GET', 'POST'])
def superadmin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match an entry in the admin_collection
        if superadmin_collection.find_one({"username": username, "password": password}):
            session['username'] = username
            session['role'] = 'superadmin'
            return redirect('/superadmin')
        else:
            flash('Access Denied', 'error')
            return redirect('/superadmin_login')

    return render_template("Super_Admin_login.html")


@app.route('/superadmin/addHospital', methods=['GET', 'POST'])
@login_required('superadmin')
def add_hospital():
    if request.method == 'POST':
        hospital_name = request.form['hospitalName']
        hospital_mail = request.form['hospitalmail'].strip()
        pa = request.form['hospitalpass']
        password = bcrypt.generate_password_hash(pa).decode('utf-8')

        existing_hospital = admin_collection.find_one(
            {'hospital_name': hospital_name})
        existing_hospital_email = admin_collection.find_one(
            {'hospital_mail': hospital_mail})

        if existing_hospital:
            return 'Username already exists. Please choose a different username.'

        if existing_hospital_email:
            return 'Email already exists. Please use a different email address.'
        # Store the hospital data in the hospital collection
        hospitalData = {
            "hospital_name": hospital_name,
            "hospital_mail": hospital_mail,
            "hospital_password": password
        }
        admin_collection.insert_one(hospitalData)

        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            time = datetime.now()
            connection.login(user=my_email, password=code)
            connection.sendmail(from_addr=my_email,
                                to_addrs=hospital_mail,
                                msg=f"""
Dear,
Your Hospital Account (Email ID {hospital_mail}) Password is:{pa}.

(Generated at {time})

********************************
This is an auto-generated email. Do not reply to this email.""")
    return render_template('super_add_hospital.html')


@app.route('/superadmin/checkHospitalStatus', methods=['GET', 'POST'])
@login_required('superadmin')
def check_hospital():
    if request.method == 'POST':
        hospital_name = request.form.get('hname')

        if not hospital_name:
            return "Hospital name is missing", 400  # Bad Request

        data = hospital_data_collection.find_one(
            {'hospital_name': hospital_name})

        if data:
            no_doc= doctors_collection.count_documents({"hospital_name":hospital_name})
            return render_template('superadmin_hospital_status.html', data=data,no_doc = no_doc)
        else:
            return "No hospital found"
    hospitals = hospital_data_collection.find()
    hospital_names = [hospital['hospital_name'] for hospital in hospitals]
    return render_template('super_admin_check_hospital.html', hospitals=hospital_names)


@app.route('/admin/discharge', methods=['POST', 'GET'])
@login_required('admin')
def submit_discharge():
    if request.method == 'POST':
        # Extracting form data
        patient_id = request.form.get('patient_id')
        patient_name = request.form.get('patient_name')
        admission_date = request.form.get('admission_date')
        discharge_date = request.form.get('discharge_date')
        diagnosis = request.form.get('diagnosis')
        treatment = request.form.get('treatment')
        doctor_name = request.form.get('doctor_name')
        discharge_summary = request.form.get('discharge_summary')
        follow_up_instructions = request.form.get('follow_up_instructions')
        medications = request.form.get('medications')
        contact_info = request.form.get('contact_info')
        gender = request.form.get('gender')
        address = request.form.get('address')
        bed_type = request.form.get('bedtype')

        hospital_name_patient = session.get('hospital_name')
        data_discharge = {
            'patient_id': patient_id,
            'patient_name': patient_name,
            'admission_date': admission_date,
            'discharge_date': discharge_date,
            'diagnosis': diagnosis,
            'treatment': treatment,
            'doctor_name': doctor_name,
            'discharge_summary': discharge_summary,
            'follow_up_instructions': follow_up_instructions,
            'medications': medications,
            'contact_info': contact_info,
            'gender': gender,
            'address': address
        }
        hospital_discharge_collection.insert_one(data_discharge)
        hospital_data_collection.update_one(
            {'hospital_name': hospital_name_patient},
            # Increment the occupied beds count by 1
            {'$inc': {f'occupied_{bed_type}': -1}}
        )
        # Generate PDF with the provided details
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        # Patient details inside the pdf
        elements = []
        elements.append(Paragraph("Patient ID Card", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(
            Paragraph(f"Full Name: {patient_name}", styles['Normal']))
        elements.append(Paragraph(f"Admission Date: {admission_date}", styles['Normal']))
        elements.append(Paragraph(f"Gender: {gender}", styles['Normal']))
        elements.append(Paragraph(f"Address: {address}", styles['Normal']))
        elements.append(Paragraph(f"Phone Number: {contact_info}", styles['Normal']))
        elements.append(Paragraph(f"Diagnosis: {diagnosis}", styles['Normal']))
        elements.append(Paragraph(f"Discharge Summary: {discharge_summary}", styles['Normal']))

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(
            f"Name: {patient_name}\Admission Date: {admission_date}\nPhone: {contact_info}\nDischarge Summary: {diagnosis}")
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        qr_buffer = io.BytesIO()
        img.save(qr_buffer, 'PNG')
        qr_buffer.seek(0)

        # Add QR code to PDF
        elements.append(Spacer(1, 12))
        elements.append(Image(qr_buffer, width=100, height=100))

        doc.build(elements)

        pdf_buffer.seek(0)
        # @after_this_request
        # def redirect_to_admin(reponse=302):
        #     return redirect('/admin')
        return send_file(pdf_buffer, as_attachment=True, download_name='patient_id_card.pdf', mimetype='application/pdf')
        # return redirect('/admin')
    return render_template('Patient_discharge.html')
# where is the change


@app.route('/admin/inv_admin', methods=['GET', 'POST'])
@login_required('admin')
def inv_details():
    return render_template('inv_admin.html')


@app.route('/admin/inv_med_order', methods=['GET', 'POST'])
@login_required('admin')
def inv_med():
    if request.method == 'POST':
        medicine_name = request.form.get('medicine-name')
        medicine_composition = request.form.get('medicine-composition')
        medicine_quantity = request.form.get('medicine-quantity')
        order_comment = request.form.get('order-comment')
        hospital_name = session.get('hospital_name')
        # Create a document to insert into MongoDB
        order_data = {
            "medicine_name": medicine_name,
            "medicine_composition": medicine_composition,
            "medicine_quantity": int(medicine_quantity),  # Convert to integer
            "order_comment": order_comment,
            "hospital_name": hospital_name
        }

        # Insert the document into the inventory collection
        inventory_collection.insert_one(order_data)

    # return "Order submitted successfully!"
    return render_template('inv_med_order.html')


@app.route('/admin/inv_order_status', methods=['GET', 'POST'])
@login_required('admin')
def order_status():
    # data=
    datas = inventory_collection.find(
        {'hospital_name': session.get('hospital_name')})

    return render_template('inv_order_status.html', datas=datas)


@app.route('/admin/inv_stock_product', methods=['GET', 'POST'])
@login_required('admin')
def stock_details():
    return render_template('inv_stock_product.html')

# show

if __name__ == '__main__':
    app.run(port=8000, debug=True)
