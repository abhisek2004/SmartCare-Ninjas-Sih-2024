from flask import request,session,redirect,Blueprint,flash,render_template
from flask_bcrypt import Bcrypt
from modules.db import doctors_collection,appointment_collection,hospital_data_collection,patients_collection,feedback_collection
from modules.login_required import login_required

doctor_blueprint = Blueprint('doctor_blueprint',__name__)
bcrypt = Bcrypt()
@doctor_blueprint.route('/doctor_login', methods=['POST', 'GET'])
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
                session['role'] = 'doctor'
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


@doctor_blueprint.route('/doctor_app', methods=["POST", "GET"])
@login_required('doctor')
def doctor_app():
    appointments = appointment_collection.find({'hospital_name': session.get(
        'hospital_name'), 'speciality': session.get('specialization')})
    doc_detail = doctors_collection.find_one(
        {'username': session.get('username')})
    appointment_count = appointment_collection.count_documents({'hospital_name': session.get('hospital_name')})
    return render_template('doctor_dash.html', appointments=appointments, doctor=doc_detail,total_appointments=appointment_count)


@doctor_blueprint.route('/bed_status', methods=['GET', 'POST'])
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
        occupied_icu_beds = total_icu_beds_data.get(
            'total_occupied_icu_beds', 0)
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
        occupied_ventilators = total_ventilators_data.get(
            'total_occupied_ventilators', 0)
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
        occupied_icu_beds = total_icu_beds_data.get(
            'total_occupied_icu_beds', 0)
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

    return render_template('bed_status.html',
                           hospitals=hospital_names,
                           no_hospital=no_of_hospital,
                           doctor=total_doctor,
                           patient=active_patient,
                           total_general_beds=total_beds,
                           available_beds=available_beds,
                           total_icu_beds=total_icu_beds,
                           available_icu_beds=available_icu_beds,
                           total_ventilators=total_ventilators,
                           available_ventilators=available_ventilators)

@doctor_blueprint.route('/doctor_feedback',methods = ['GET','POST'])
@login_required('doctor')
def feedback():
    if request.method == 'POST':
       name = request.form['uname'] 
       email = request.form['email']
       phone = request.form['phone']
       service_satisfaction = request.form['satisfy']
       issue = request.form['msg']
       feedback_data = {
            'name':name,
            'email':email,
            'phone':phone,
            'service':service_satisfaction,
            'issue':issue
        }

       print(feedback_collection.insert_one(feedback_data))
    return render_template('feedback.html')

    
@doctor_blueprint.route('/video_call',methods=['GET'])
def video():
    return render_template('emergency_scheduling.html')