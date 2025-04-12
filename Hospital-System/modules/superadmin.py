from flask import request,session,redirect,flash,render_template,Blueprint
from modules.db import superadmin_collection,hospital_data_collection,doctors_collection,patients_collection,admin_collection,my_email,code,feedback_collection
from datetime import datetime
from modules.login_required import login_required
from flask_bcrypt import Bcrypt
import smtplib


bcrypt = Bcrypt()
superadmin_blueprint = Blueprint('superadmin_blueprint',__name__)
@superadmin_blueprint.route("/superadmin_login", methods=['GET', 'POST'])
def superadmin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(username)
        print(superadmin_collection.find_one({"username": username, "password": password}))
        # Check if the username and password match an entry in the admin_collection
        if superadmin_collection.find_one({"username": username, "password": password}):
            session['username'] = username
            session['role'] = 'superadmin'
            print(session)
            return redirect('/superadmin')
        else:
            flash('Access Denied', 'error')
            return redirect('/superadmin_login')

    return render_template("Super_Admin_login.html")

@superadmin_blueprint.route('/superadmin/', methods=['GET', 'POST'])
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



@superadmin_blueprint.route('/superadmin/addHospital', methods=['GET', 'POST'])
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


@superadmin_blueprint.route('/superadmin/checkHospitalStatus', methods=['GET', 'POST'])
@login_required('superadmin')
def check_hospital():
    if request.method == 'POST':
        hospital_name = request.form.get('hname')

        if not hospital_name:
            return "Hospital name is missing", 400  # Bad Request

        data = hospital_data_collection.find_one(
            {'hospital_name': hospital_name})

        if data:
            no_doc = doctors_collection.count_documents(
                {"hospital_name": hospital_name})
            return render_template('superadmin_hospital_status.html', data=data, no_doc=no_doc)
        else:
            return "No hospital found"
    hospitals = hospital_data_collection.find()
    hospital_names = [hospital['hospital_name'] for hospital in hospitals]
    return render_template('super_admin_check_hospital.html', hospitals=hospital_names)

@superadmin_blueprint.route('/superadmin/feedback', methods=['GET', 'POST'])
@login_required('superadmin')
def feedback():
    return render_template('Admin_feedback.html',feedback=feedback)