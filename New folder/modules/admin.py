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