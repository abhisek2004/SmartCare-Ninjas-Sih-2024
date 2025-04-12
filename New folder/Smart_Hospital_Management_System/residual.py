from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(data):
    doc = SimpleDocTemplate("appointment.pdf", pagesize=letter)

    # Define styles
    styles = getSampleStyleSheet()
    header_style = styles["Heading1"]
    table_style = TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, 'black'),
        ('BOX', (0, 0), (-1, -1), 0.25, 'black'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
    ])

    # Define header and footer functions
    def header(canvas, doc):
        canvas.saveState()
        # Add AIIMS logo or text here
        canvas.drawString(inch, 10 * inch, "AIIMS, BHUBANESWAR, ODISHA")
        canvas.restoreState()

    def footer(canvas, doc):
        canvas.saveState()
        page_num = canvas.getPageNumber()
        canvas.drawString(inch, 0.5 * inch, f"Page {page_num}")
        canvas.restoreState()

    # Create elements
    header_elements = [Paragraph("Appointment Details", header_style)]
    table_data = [
        ["Appointment No.", "Appointment Date", "Patient Name", "Mobile No."],
        [data["appointment_no"], data["appointment_date"], data["patient_name"], data["mobile_no"]]
    ]
    table_data2 = [
        ["Appointment No.", "Appointment Date", "Patient Name", "Mobile No."],
        [data["appointment_no"], data["appointment_date"], data["patient_name"], data["mobile_no"]]
    ]
    table = Table(table_data, style=table_style)
    table2 = Table(table_data2, style=table_style)
    # Build the document
    doc.build(header_elements + [table] +[table2], onFirstPage=header, onLaterPages=footer)

# Static data dictionary
data = {
    "appointment_no": "A123456",
    "appointment_date": "2024-09-05",
    "patient_name": "John Doe",
    "mobile_no": "1234567890"
}

# Generate the PDF
generate_pdf(data)
