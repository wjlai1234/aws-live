from flask import Flask, render_template, redirect, request
from pymysql import connections
import os
import boto3
from config import *
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_HEADERS'] = 'Access-Control-Allow-Origin'

# Access-Control-Allow-Origin
bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'
cur = db_conn.cursor() 
cur.execute("""SELECT * FROM employee""")
user = cur.fetchall()
sidebar_items = [
        ["Dashboard","ion-ios-home-outline","/"],
        ["Employee","ion-ios-person-outline","employee"],
        ["Leave Tracker","ion-ios-calendar-outline","leave"],
        ["Payroll","ion-cash","payroll"],
        ["Attendances","ion-checkmark","attendances"],
        ["Message","ion-ios-chatboxes-outline","message"]
        ]

@app.route("/", methods=['GET', 'POST'])
@cross_origin()
def home():
    title = 'Employee System Management'
    return render_template('base.html', len = len(user), active="/",  sidebar_items=sidebar_items,  len_sidebar=len(sidebar_items), title=title)

@app.route("/employee", methods=['GET', 'POST'])
def employee():
    id = len(user) + 1
    return render_template('Employee.html',len = len(user), active="employee", user = user, id=id, sidebar_items=sidebar_items, len_sidebar=len(sidebar_items))

@app.route("/leave", methods=['GET'])
def leave():
    return render_template('Leave.html',active="leave", sidebar_items=sidebar_items, len_sidebar=len(sidebar_items))

@app.route("/payroll", methods=['GET'])
def payroll():
    return render_template('Payroll.html',active="payroll", sidebar_items=sidebar_items, len_sidebar=len(sidebar_items))

@app.route("/attendances", methods=['GET'])
def attendances():
    return render_template('Attendance.html',active="attendances", sidebar_items=sidebar_items, len_sidebar=len(sidebar_items))


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    position = request.form['position']
    start_date = request.form['start_date']
    salary = request.form['salary']
    email = request.form['email']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, position, start_date, salary, email, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    id = len(user) + 1
    return render_template('Employee.html',len = len(user), active="employee", user = user, id=id, sidebar_items=sidebar_items, len_sidebar=len(sidebar_items))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
