from pymongo import MongoClient
from pymongo.server_api import ServerApi

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