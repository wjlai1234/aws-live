from ast import dump
from subprocess import check_output
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
    ["Dashboard", "ion-ios-home-outline", "/"],
    ["Employee", "ion-ios-person-outline", "employee"],
    ["Leave Tracker", "ion-ios-calendar-outline", "leave"],
    ["Payroll", "ion-cash", "payroll"],
    ["Attendances", "ion-checkmark", "attendances"],
    ["About Us","ion-ios-chatboxes-outline","about"]
]
count = 0
cur.execute("""SELECT e.id, e.first_name, e.last_name ,a.* FROM employee e LEFT JOIN attendance a ON (e.id = a.employee_id)""")
attendance = cur.fetchall()
employee_data = []
for employee in attendance:
    username = employee[2] + employee[1]
    employee_data.append(username)
    if employee[8] == "valid":
        count += 1

attendance_rate = count/len(attendance) * 100


@app.route("/", methods=['GET', 'POST'])
@cross_origin()
def home():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    count = 0
    cur = db_conn.cursor()
    cur.execute(
        """SELECT e.id, e.first_name, e.last_name ,a.* FROM employee e LEFT JOIN attendance a ON (e.id = a.employee_id)""")
    attendance = cur.fetchall()
    employee_data = []
    for employee in attendance:
        username = employee[2] + employee[1]
        employee_data.append(username)
        if employee[8] == "valid":
            count += 1
    attendance_rate = count/len(attendance) * 100

    total = 0.0
    cur = db_conn.cursor()
    cur.execute("""SELECT  CASE WHEN a.total_payment IS NULL THEN 0 ELSE a.total_payment END FROM employee e LEFT JOIN payroll a ON (e.id = a.emp_id)""")

    payroll = cur.fetchall()
    payroll_data = []
    for data in payroll:
        print(data[0])
        total += data[0]
        payroll_data.append(data[0])

    cur = db_conn.cursor()
    cur.execute(
        """SELECT e.id, e.first_name, e.last_name ,p.* FROM employee e LEFT JOIN leave_app p ON (e.id = p.emp_id)""")
    leave = cur.fetchall()
    leave_count = 0
    for employee in leave:
        if employee[6] == "approve":
            leave_count += 1

    leave_rate = leave_count/len(leave) * 100
    title = 'Employee System Management'
    return render_template('base.html', user=user, len_user=len(user), leave_rate=str(round(leave_rate, 2)), payroll_data=payroll_data, total=total, employee_data=employee_data, attendance_rate=str(round(attendance_rate, 2)), len=len(user), active="/",  sidebar_items=sidebar_items,  len_sidebar=len(sidebar_items), title=title, attendance=attendance)


@app.route("/employee", methods=['GET', 'POST'])
def employee():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

    )
    cur = db_conn.cursor()
    cur.execute("""SELECT * FROM employee""")
    user = cur.fetchall()
    id = len(user) + 1
    return render_template('Employee.html', employee_data=employee_data, len=len(user), active="employee", user=user, id=id, sidebar_items=sidebar_items, len_sidebar=len(sidebar_items))


@app.route("/leave", methods=['GET'])
def leave():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    cur = db_conn.cursor()
    cur.execute(
        """SELECT e.id, e.first_name, e.last_name ,p.* FROM employee e LEFT JOIN leave_app p ON (e.id = p.emp_id)""")
    leave = cur.fetchall()
    return render_template('Leave.html', active="leave", len=len(leave), leave=leave, employee_data=employee_data, sidebar_items=sidebar_items, len_sidebar=len(sidebar_items))


@app.route("/payroll", methods=['GET'])
def payroll():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    cur = db_conn.cursor()
    cur.execute(
        """SELECT e.id, e.first_name, e.last_name ,a.* FROM employee e LEFT JOIN payroll a ON (e.id = a.emp_id)""")
    payroll = cur.fetchall()
    return render_template('Payroll.html', active="payroll", len=len(payroll), payroll=payroll, employee_data=employee_data, sidebar_items=sidebar_items, len_sidebar=len(sidebar_items))


@app.route("/attendances", methods=['GET'])
def attendances():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    cur = db_conn.cursor()
    cur.execute("""SELECT * FROM employee""")
    user = cur.fetchall()
    cur = db_conn.cursor()
    cur.execute(
        """SELECT e.id, e.first_name, e.last_name ,a.* FROM employee e LEFT JOIN attendance a ON (e.id = a.employee_id)""")
    attendance = cur.fetchall()
    print(attendance)
    return render_template('Attendance.html', employee_data=employee_data, attendance=attendance, len_attendance=len(attendance), active="attendances", len=len(user), user=user, sidebar_items=sidebar_items, len_sidebar=len(sidebar_items))


@app.route("/addemp", methods=['POST'])
def AddEmp():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    position = request.form['position']
    start_date = request.form['start_date']
    salary = request.form['salary']
    email = request.form['email']
    location = request.form['location']
    drive = request.form['drive']
    emp_image_file = request.files['emp_image_file']
    emp_profile_picture_file = request.files['profile_picture']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s) ON DUPLICATE KEY UPDATE first_name=%s, last_name=%s, position=%s, start_date=%s, salary=%s, email=%s, location=%s, drive=%s"
    cursor = db_conn.cursor()

    # if emp_image_file.filename == "":
    #     return "Please select a file"

    try:
        cursor.execute( insert_sql, (emp_id, first_name, last_name, position, start_date, salary,
                       email, location, drive, first_name, last_name, position, start_date, salary, email, location, drive))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        emp_profile_piture_file_name_in_s3 = "emp-id-" + str(emp_id) + "_profile_image_file.png"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(
                Key=emp_image_file_name_in_s3, Body=emp_image_file)
            s3.Bucket(custombucket).put_object(
                Key=emp_profile_piture_file_name_in_s3, Body=emp_profile_picture_file)
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
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

    return redirect('employee')


@app.route("/addattendance", methods=['POST'])
def AddAttendance():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    emp_id = request.form['emp_id']
    print(emp_id)
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    check_in_data = check_in.split(":")
    check_out_data = check_out.split(":")
    a_hours = int(check_in_data[0])
    b_hours = int(check_out_data[0])
    a_mins = int(check_in_data[1])
    b_mins = int(check_out_data[1])

    if b_hours < a_hours:
        return "please enter correct check out hours!"
    ttl_a = a_hours + (a_mins/60)
    ttl_b = b_hours + (b_mins/60)
    ttl = ttl_b - ttl_a

    total_hours = float(f'{ttl:.2f}')

    overtime = 0
    status = "invalid"
    if (total_hours >= 8):
        overtime = total_hours - 8.00
        status = "valid"

    cur = db_conn.cursor()
    cur.execute(
        "SELECT e.salary, p.total_hours FROM employee e LEFT JOIN attendance p ON (e.id = p.employee_id)  WHERE e.id = %s", (emp_id))
    total_work = cur.fetchall()
    print(total_work[0][0])
    payment = total_work[0][0] * total_work[0][1]
    total_payment = float(f'{payment:.2f}')

    insert_sqla = "INSERT INTO payroll VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE total_hours=%s, total_payment=%s"
    insert_sqlb = "INSERT INTO attendance VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE status=%s, check_in=%s, check_out=%s, total_hours=%s, over_time=%s"
    cursor = db_conn.cursor()
    try:
        cursor.execute(
            insert_sqla, (emp_id, total_hours, total_payment, total_hours, total_payment))
        cursor.execute(insert_sqlb, (emp_id, check_in, check_out, total_hours,
                       overtime, status, status, check_in, check_out, total_hours, overtime))
        db_conn.commit()
    finally:
        cursor.close()
    return redirect('attendances')


@app.route("/addleave", methods=['POST'])
def AddLeave():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    emp_id = request.form['emp_id']
    date = request.form['date']
    reason = request.form['reason']
    status = request.form['status']

    insert_sql = "INSERT INTO leave_app VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE date=%s, reason=%s, status=%s"
    cursor = db_conn.cursor()
    try:
        cursor.execute(insert_sql, (emp_id, date, reason,
                       status, date, reason, status))
        db_conn.commit()
    finally:
        cursor.close()
    return redirect('leave')

@app.route('/about', methods=['GET'])
def about():
    return render_template('About.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
