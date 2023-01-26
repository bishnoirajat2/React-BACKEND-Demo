from flask import Flask, request, redirect, session, jsonify
from flask_mysqldb import MySQL
from flask_session import Session
# from flask_cors import CORS
import MySQLdb.cursors
import redis
# from flask_api_cache import ApiCache
import jwt
from datetime import datetime, timedelta
from functools import wraps
app = Flask(__name__)

# app.options('*', CORS())
# Change this to your secret key (can be anything, it's for extra protection)
app.config['SECRET_KEY'] = 'ZmNbu4OcCPzeC6Fi'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'pythonlogin'
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)
# CORS(app)
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers['Token']
        print(type(token),token)
        payload = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])
        print(payload)

        # except:
        return func(payload['user'], *args, **kwargs)
    return decorated
# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - the following will be our login page, which will use both GET and POST requests
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    print(str(request.json['username']))
    print("reached")
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.json and 'password' in request.json:
        # Create variables for easy access
        username = request.json['username']
        password = request.json['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = SHA2(%s,256)', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        print("123")
        # If account exists in accounts table in our database
        if account:
            # Create session data, we can access this data in other routes
            print("456")
            print([i for i in session])
            session['loggedin'] = True
            print(session.get("loggedin"))
            session['id'] = account['id']
            session['username'] = account['username']
            session.modified = True
            token = jwt.encode({
                'user': session['id'],
                'expiration': str(datetime.utcnow()+timedelta(seconds=120))}, app.config['SECRET_KEY'])
            return jsonify({'token': token, 'status': True})
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return jsonify(msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return jsonify({'status': True})

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home/', methods=['GET','POST'])
@token_required
def home(token):
    print(token)
    app.logger.info("home...")
    print('reached home1')
    print(session.get('loggedin'))
    print([i for i in session])
    # Check if user is loggedin
    # if session.get('loggedin'):
    print('reached home2')
    # User is loggedin show them the home page
    cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor2.execute('SELECT * FROM employees')
    information = list(cursor2)
    # print(information)
    for i in information:
        i['dob'] = str(i['dob'])
        # print(i['dob'])
    return jsonify({"data": information, "status": True, "token": token})


@app.route('/pythonlogin/add/', methods=['GET','POST'])
def add():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    print("C1")
    # print(request.json, request.method, 'employee id' in request.json, 'employee name' in request.json and 'email' in request.json)
    if request.method == 'POST' and 'fn' in request.json and 'ln' in request.json and 'dob' in request.json and 'skl' in request.json and 'act' in request.json and 'email' in request.json and 'age' in request.json:
        print("C2")
        # Create variables for easy access
        f_name = request.json['fn']
        l_name = request.json['ln']
        dob = request.json['dob']
        skl = request.json['skl']
        act = bool(request.json['act'])
        age = request.json['age']
        email = request.json['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO employees (f_name, l_name, dob, email, skill_id, active, age) VALUES (%s, %s, %s, %s, %s, %s, %s)', (f_name, l_name, dob, email, skl, act, age,))
        cursor.execute('SELECT MAX(e_id) FROM employees')
        x = list(cursor)
        mysql.connection.commit()
        # If account exists show error and validation checks
        print("C3")
        msg = 'You have been successfully added!'
        return jsonify({"status": True, "e_id": x[0]['MAX(e_id)']})
    elif request.method == 'POST':
        print("C4")
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
        return jsonify({"status": False})

@app.route('/pythonlogin/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    msg = ''
    print("edit1")
    if request.method == 'POST' and 'fn' in request.json and 'ln' in request.json and 'dob' in request.json and 'skl' in request.json and 'act' in request.json and 'email' in request.json and 'age' in request.json:
        # Create variables for easy access
        print('edit2')
        eid = id
        f_name = request.json['fn']
        l_name = request.json['ln']
        dob = datetime.strptime(request.json['dob'], '%Y-%m-%d').date()
        skl = request.json['skl']
        print(request.json['act'])

        act = request.json['act']
        print('act', act)
        age = request.json['age']
        email = request.json['email']
        print(dob, type(dob))
        print('eid',eid)
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('UPDATE employees SET e_id = %s, e_name = %s, age = %s, email = %s WHERE e_id = %s', (eid, name, age, email, eid))
        cursor.execute('select * from employees WHERE e_id = %s', (eid,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            print("START")
            cursor.execute('UPDATE employees SET f_name = %s, l_name = %s, dob = %s, email = %s, skill_id = %s, active = %s, age = %s WHERE e_id = %s', (f_name, l_name, dob, email, skl, act, age, eid,))
            # account2 = cursor.fetchone()
            mysql.connection.commit()
            print("FINISH")
            msg = 'Details Updated Sucessfully!'
            return jsonify({"status": True})

    # Show registration form with message (if any)
    return jsonify({"status": False})

@app.route('/pythonlogin/delete/<id>',  methods=['GET', 'POST'])
def delete(id):
    # Remove session data, this will log the user out
   print(id, "delete reached")
   cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   cursor.execute('DELETE FROM employees WHERE e_id = %s', (id,))
   mysql.connection.commit()
   print("DELETED")
   # Redirect to login page
   return jsonify({"status": True})