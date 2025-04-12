from datetime import datetime, timedelta
from modules.db import users_collection, appointment_collection, hospital_data_collection, doctors_collection, feedback_collection
from flask import request, session, redirect, flash, render_template, Blueprint, jsonify
from pymongo.server_api import ServerApi
from flask import Blueprint, jsonify,request,session,redirect,render_template,url_for,flash,send_file

from reportlab.lib.pagesizes import A4 # type: ignore
from reportlab.lib.styles import getSampleStyleSheet # type: ignore
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image # type: ignore
import qrcode #type:ignore
import io
from flask_bcrypt import Bcrypt
from modules.login_required import login_required
from modules.db import contact_collection,admin_collection,doctors_collection,appointment_collection,hospital_data_collection,hospital_discharge_collection,inventory_collection,patients_collection,superadmin_collection,stock_collection,feedback_collection
from flask import Flask, render_template, request, send_file, session
from pymongo import MongoClient
import io
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas


admin_blueprint = Blueprint('admin_blueprint',__name__)
bcrypt = Bcrypt()

@admin_blueprint.route('/admin/', methods=['GET', 'POST'])
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

@admin_blueprint.route('/add_patient',methods=['GET','POST'])
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


@admin_blueprint.route('/admin/patient_details', methods=['GET', 'POST'])
@login_required('admin')
def patient_details():
    patients = patients_collection.find(
        {'hospital_name': session.get('hospital_name')})
    return render_template('manage_patient.html', patients=patients)


@admin_blueprint.route("/admin/contact-us")
@login_required('admin')
def admin_contact_us():
    contacts = contact_collection.find()
    return render_template("manage_appointment.html", contacts=contacts)


@admin_blueprint.route('/admin/confirmation')
@login_required('admin')
def confirmation():
    return render_template('success_admin.html')


@admin_blueprint.route('/admin/manage_appointment', methods=['GET', 'POST'])
@login_required('admin')
def manage():
    hospital_name = session.get('hospital_name')
    appointments = appointment_collection.find(
        {"hospital_name": hospital_name})
    return render_template('manage_appointment.html', appointments=appointments)


@admin_blueprint.route('/admin_login', methods=["GET", "POST"])
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


@admin_blueprint.route('/admin/', methods=['GET', 'POST'])
# @token_required('admin')
@login_required('admin')
def login_by_admin():
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


# @admin.route("/admin/contact-us")
# @login_required('admin')
# def admin_contact_us():
#     contacts = contact_collection.find()
#     return render_template("manage_appointment.html", contacts=contacts)


@admin_blueprint.route('/admin/add_detail', methods=['GET', 'POST'])
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
        spetialisation = request.form.getlist('specialization[]')
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


@admin_blueprint.route('/add_doc', methods=['POST', 'GET'])
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


@admin_blueprint.route('/admin/inv_admin', methods=['GET', 'POST'])
@login_required('admin')
def inv_details():
    return render_template('inv_admin.html')


@admin_blueprint.route('/admin/inv_med_order', methods=['GET', 'POST'])
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

@admin_blueprint.route('/admin/inv_order_status', methods=['GET', 'POST'])
@login_required('admin')
def order_status():
    # data=
    datas = inventory_collection.find(
        {'hospital_name': session.get('hospital_name')})

    return render_template('inv_order_status.html', datas=datas)


@admin_blueprint.route('/admin/inv_stock_product', methods=['GET', 'POST'])
@login_required('admin')
def stock_details():
    return render_template('inv_stock_product.html')


@admin_blueprint.route('/admin/discharge', methods=['POST', 'GET'])
def submit_discharge():
    if request.method == 'POST':
        # Extract form data
        patient_data = {
            'Patient ID': request.form.get('patient_id'),
            'Patient Name': request.form.get('patient_name'),
            'Admission Date': request.form.get('admission_date'),
            'Discharge Date': request.form.get('discharge_date'),
            'Diagnosis': request.form.get('diagnosis'),
            'Treatment': request.form.get('treatment'),
            'Doctor Name': request.form.get('doctor_name'),
            'Discharge Summary': request.form.get('discharge_summary'),
            'Follow-Up Instructions': request.form.get('follow_up_instructions'),
            'Medications': request.form.get('medications'),
            'Contact Info': request.form.get('contact_info'),
            'Gender': request.form.get('gender'),
            'Address': request.form.get('address'),
            'Bed Type': request.form.get('bedtype')
        }

        hospital_name_patient = session.get('hospital_name', 'City Hospital')

        # Save in MongoDB
        hospital_discharge_collection.insert_one(patient_data)
        hospital_data_collection.update_one(
            {'hospital_name': hospital_name_patient},
            {'$inc': {f'occupied_{patient_data["Bed Type"]}': -1}}
        )

        # Generate PDF
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        elements = []

        # Add Background Image (Optional: Replace with your hospital logo or theme)
        # Provide a valid path if using a real background image
        background_image_path = "hospital_bg.jpg"

        # Title Section
        elements.append(
            Paragraph(f"<b>{hospital_name_patient}</b>", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(
            Paragraph(" <b>Patient Discharge Summary</b>", styles['Heading2']))
        elements.append(Spacer(1, 12))

        # Patient Details Table
        table_data = [[Paragraph(f"<b>{key}</b>", styles['Normal']), Paragraph(str(value), styles['Normal'])]
                      for key, value in patient_data.items()]

        table = Table(table_data, colWidths=[180, 300])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))

        # Important Health & Recovery Tips
        elements.append(
            Paragraph("<b> Health & Wellness Tips for Recovery:</b>", styles['Heading3']))
        health_tips = [
            " Drink Plenty of Water – Stay hydrated to help your body recover faster.",
            " Take a Bath Daily – Maintain good hygiene to prevent infections. ",
            " Eat an Apple Every Day – 'An apple a day keeps the doctor away!' ",
            " Consume a Balanced Diet – Include proteins, vitamins, and minerals.",
            " Avoid Junk Food – Say NO to excessive sugar, salt, and oily foods. ",
            " Take Your Medicines on Time – Follow the prescribed dosage carefully.",
            " Get Enough Rest & Sleep – Allow your body to heal and regain energy. ",
            " Avoid Smoking & Alcohol – These slow down recovery and harm your health. ",
            " Do Light Exercise – Gentle movements help in faster recovery. ",
            " Keep Your Surroundings Clean – Prevent infections and maintain hygiene.",
            " Regularly Change Wound Dressings – If applicable, as per doctor’s advice.",
            " Follow Your Doctor’s Instructions – Always stick to medical advice.",
            " Keep Emergency Contacts Handy – Save the hospital and doctor’s numbers.",
            " Wash Hands Frequently – Avoid germs and stay safe. ",
            " Monitor Your Symptoms – Report any unusual pain, fever, or discomfort. ",
            " Attend All Follow-Up Appointments – Ensure complete recovery. ",
            " Stay Positive & Stress-Free – Mental health is just as important. ",
        ]

        for tip in health_tips:
            elements.append(Paragraph(tip, styles['Normal']))

        elements.append(Spacer(1, 12))

        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = "\n".join(
            [f"{key}: {value}" for key, value in patient_data.items()])
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        qr_buffer = io.BytesIO()
        img.save(qr_buffer, 'PNG')
        
        qr_buffer.seek(0)

        # Add QR Code to PDF
        elements.append(
            Paragraph("<b> Scan QR for Full Details:</b>", styles['Heading3']))
        elements.append(Spacer(1, 6))
        elements.append(Image(qr_buffer, width=100, height=100))

        elements.append(Spacer(1, 12))

        # Footer Section
        elements.append(Paragraph(
            "Thank you for choosing our hospital. Wishing you a speedy recovery! ", styles['Italic']))
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(" Hospital Address: 123, Main Street, City XYZ", styles['Normal']))
        elements.append(
            Paragraph(" Emergency Helpline: +91-9999999999", styles['Normal']))

        doc.build(elements)

        pdf_buffer.seek(0)

        return send_file(pdf_buffer, as_attachment=True, download_name='Patient_Discharge_Summary.pdf', mimetype='application/pdf')

    return render_template('Patient_discharge.html')

@admin_blueprint.route('/admin_feedback',methods=['POST','GET'])
def admin_feedback():
    hospital_name = feedback_collection.find({})
    feedbacks = feedback_collection.find()
    return render_template('feedback.html')

@admin_blueprint.route('/admin_appointment',methods=['POST','GET'])
def appointment():
    return render_template('add appointment.html')

@admin_blueprint.route('/admin_settings',methods=['POST','GET'])
def admin_settings():
    hospital_name = session.get('hospital_name')
    print(hospital_name)
    data = hospital_data_collection.find_one({'hospital_name':hospital_name})

    if request.method == 'POST':
        name = request.form.get('hospital_name')
        ID = data['hospital_id']  # Assuming 'data' is a dictionary
        address = request.form.get('address')
        contact_number = request.form.get('contact_number')
        emergency_contact_number = request.form.get('emergency_contact_number')
        email = request.form.get('email')
        website = request.form.get('website')
        no_beds = int(request.form.get('no_beds', 0))  # Default to 0 if missing
        general_beds_occupied = int(request.form.get('general_beds_occupied', 0))
        icu_beds = request.form.get('icu_beds')
        icu_beds_occupied = request.form.get('icu_beds_occupied')
        ventilators = request.form.get('ventilators')
        ventilators_occupied = request.form.get('ventilators_occupied')
        emergency_department = request.form.get('emergency_department')
        specialization = request.form.get('specialization')
        operating_hours = request.form.get('operating_hours')
        visiting_hours = request.form.get('visiting_hours')
        pharmacy_on_site = request.form.get('pharmacy_on_site')
        total_doctor = request.form.get('total_doctor')
        total_nurses = request.form.get('total_nurses')
        administrative_staff = request.form.get('administrative_staff')
        total_inventory_distributors = request.form.get('total_inventory_distributors')
        ambulance_services = request.form.get('ambulance_services')
        blood_bank = request.form.get('blood_bank')
        diagnostic_services = request.form.get('diagnostic_services')
        print(name, ID, address, contact_number, emergency_contact_number, email, website, no_beds, general_beds_occupied, icu_beds, icu_beds_occupied, ventilators, ventilators_occupied, emergency_department, specialization, operating_hours, visiting_hours, pharmacy_on_site, total_doctor, total_nurses, administrative_staff, total_inventory_distributors, ambulance_services, blood_bank, diagnostic_services)
        hospital_data_collection.update_one(
            {'hospital_name': hospital_name},
            {'$set': {'hospital_name': name,
                      'hospital_id': ID,
                      'address': address,
                      'contact_number': contact_number,
                      'emergency_contact_number': emergency_contact_number,
                      'email': email,
                      'website': website,
                      'number_of_beds': no_beds,
                      'general_beds_occupied': general_beds_occupied,
                      'icu_beds': icu_beds,
                      'icu_beds_occupied': icu_beds_occupied,
                      'ventilators': ventilators,
                      'ventilators_occupied': ventilators_occupied,
                      'emergency_department': emergency_department,
                      'specialization': specialization,
                      'operating_hours': operating_hours,
                      'visiting_hours': visiting_hours,
                      'pharmacy_on_site': pharmacy_on_site,
                      'total_doctor': total_doctor,
                      'total_nurses': total_nurses,
                      'administrative_staff': administrative_staff,
                      'total_inventory_distributors': total_inventory_distributors,
                      'ambulance_services': ambulance_services,
                      'blood_bank': blood_bank,
                      'diagnostic_services': diagnostic_services
                      }
             }
        )
    return render_template('superadmin_hospital_status.html',data=data)


@admin_blueprint.route('/update_hospital', methods=['POST'])
def update_hospital():
    try:
        hospital_id = request.form['hospitalID']  # Assuming this is the unique identifier
        updated_data = {
            "hospital_name": request.form['hospital_name'],
            "address": request.form['address'],
            "contact_number": request.form['contact_number'],
            "emergency_contact_number": request.form['emergency_contact_number'],
            "email_address": request.form['email'],
            "website_url": request.form['website'],
            "number_of_general_beds": int(request.form['no_beds']),
            "occupied_general": int(request.form['general_beds_occupied']),
            "number_of_icu_beds": int(request.form['icu_beds']),
            "occupied_icu": int(request.form['icu_beds_occupied']),
            "number_of_ventilators": int(request.form['ventilators']),
            "occupied_ventilator": int(request.form['ventilators_occupied']),
            "emergency_department": request.form['emergency_department'],
            "specialization": request.form['specialization'],
            "hospital_operating_hours": request.form['operating_hours'],
            "visiting_hours": request.form['visiting_hours'],
            "pharmacy_on_site": request.form['pharmacy_on_site'],
            "total_doctors": int(request.form['total_doctors']),
            "total_number_of_nurses": int(request.form['total_nurses']),
            "administrative_staff_count": int(request.form['administrative_staff']),
            "inventory_distributors": int(request.form['total_inventory_distributors']),
            "ambulance_services": request.form['ambulance_services'],
            "blood_bank": request.form['blood_bank'],
            "diagnostic_services": request.form['diagnostic_services'],
        }

        # Updating the database
        hospital_data_collection.update_one({"hospital_id": hospital_id}, {"$set": updated_data})
        return redirect(url_for('hospital_details', hospital_id=hospital_id))

    except KeyError as e:
        return f"KeyError: Missing field {e}", 400
    except Exception as e:
        return f"Error: {e}", 500@admin_blueprint.route('/update_hospital_data', methods=['POST'])
def update_hospital_data():
    try:
        data = request.get_json()

        # Extract hospital ID or unique identifier (e.g., hospital_id)
        hospital_id = data.get('hospital_id')
        if not hospital_id:
            return jsonify({"error": "Hospital ID is required"}), 400

        # Remove the hospital_id from data before updating
        data.pop('hospital_id', None)

        # Update MongoDB
        result = hospital_data_collection.update_one(
            {"hospital_id": hospital_id},
            {"$set": data}
        )

        if result.modified_count > 0:
            return jsonify({"success": "Hospital data updated successfully!"})
        else:
            return jsonify({"error": "No data was updated. Please check the input values."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    from pymongo import MongoClient


my_email = "nicdelhi2024@gmail.com"
code = "zuff vkvx pamt kdor"
uri = "mongodb+srv://manasranjanpradhan2004:root@hms.m7j9t.mongodb.net/?retryWrites=true&w=majority&appName=HMS"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

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
feedback_collection = db['feedback']
admin_feedback_collection = db['admin_feedback']



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



from flask import session, redirect,Blueprint,flash

logout_bp=Blueprint('logout_bp',__name__)

@logout_bp.route('/user_logout')
def user_logout():
    session.clear()
    flash('You have logged out', 'success')
    return redirect('/')


@logout_bp.route('/admin_logout')
def admin_logout():
    session.clear()
    flash('You have logged out', 'success')
    return redirect('/')


@logout_bp.route('/superadmin_logout')
def sueperadmin_logout():
    session.clear()
    # flash('You have logged out', 'success')
    return redirect('/superadmin')

@logout_bp.route('/doctor_logout')
def doctor_logout():
    session.clear()
    flash('You have logged out', 'success')
    return redirect('/')



from flask import session,redirect
from functools import wraps


def login_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session or session.get('role') != role:
                return redirect(f'/{role}_login')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


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
    return render_template('Admin_feedback.html', feedback=feedback)


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
