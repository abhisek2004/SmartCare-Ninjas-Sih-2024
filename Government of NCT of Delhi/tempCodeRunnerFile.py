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
        # total_no_of_appointments=hospital_data_collection.count_documents({"hospital_name":hospital_name})
        # print(total_no_of_appointments)
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
            'hospital_name': hospital_name
        }
        appointment_collection.insert_one(appointment_data)

        # After saving or processing, redirect or render a success page
        return redirect('/confirmation')