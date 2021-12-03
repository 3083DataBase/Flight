#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
					   port=3306,
                       user='root',
                       password='',
                       db='project_sys',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


#Define a route to hello function
@app.route('/', methods=['GET', 'POST'])
def hello():
	session['email'] = [None, 'Guest', 0, None]    # Will hold the email and name of the season
	#cursor = conn.cursor();

	#after this Kevin needs to change for search
	#query = 'SELECT * FROM flight WHERE DepartureDate > CURRENT_DATE or (DepartureDate = CURRENT_DATE and DepartureTime > CURRENT_TIMESTAMP)'
	#cursor.execute(query) #Runs the query
	#flight_data = cursor.fetchall() #Gets the data from ran SQL query

	#Tests
	#for each in flight_data:   #prints out all the flights we have THIS IS A TEST
	#	print(each['FlightNumber'],each['DepartureDate'], each['DepartureTime'])


	#cursor.close()
	return render_template('flights.html', name1="guest")

#Searches for the flights of the inputs
@app.route('/search_flights', methods=['GET', 'POST'])
def search_flights():
	checkbox = request.form["checkbox"]
	departing = request.form["Departing"]
	departing_date = request.form["Departure Date"]
	arriving = request.form["Arriving"]
	arriving_date = None

	arriving_data = ()

	cursor = conn.cursor()
	if(checkbox == "RoundTrip"):
		arriving_date = request.form["Arriving Date"]
		query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate = %s'
		query2 = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = a.AirportID AND ArrivalAirportID = d.AirportID AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate = %s'
		cursor.execute(query, (departing, departing, arriving, arriving, departing_date)) #Runs the query
		depart_data = cursor.fetchall() #Gets the data from ran SQL query
		cursor.execute(query2, (arriving, arriving, departing, departing, arriving_date)) #Runs the query
		arriving_data = cursor.fetchall()

	else:    #Is the one way search
		query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate = %s'
		cursor.execute(query, (departing, departing, arriving, arriving, departing_date)) #Runs the query
		depart_data = cursor.fetchall() #Gets the data from ran SQL query
		for each in depart_data:   #prints out all the flights we have THIS IS A TEST
			print(each)

	cursor.close()
	return render_template('flights.html', depart_flights=depart_data, arrival_flights=arriving_data)

#Searches for a flight to see the status
@app.route('/flight_status', methods=['GET', 'POST'])
def flight_status():
	return render_template('flight_status.html')

@app.route('/get_flight', methods=['GET', 'POST'])
def get_flight():
	FlightNumber = request.form["FlightNumber"]
	Date = request.form["Date"]
	Airline = request.form["AirlineName"]

	cursor = conn.cursor()
	query = 'Select FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, Status FROM `flight` WHERE FlightNumber = %s AND (DepartureDate = %s or ArrivalDate = %s) AND AirlineName = %s'
	cursor.execute(query, (FlightNumber, Date, Date, Airline))
	flight = cursor.fetchall()

	cursor.close()
	return render_template('flight_status.html', flight = flight)

#Holds all the code for the staff to input into flights
@app.route('/staff', methods=['GET', 'POST'])
def staff():
	session['email'][2] = "China Eastern"
	cursor = conn.cursor()
	query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, status FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND AirlineName = %s AND DATEDIFF(DepartureDate, CURRENT_DATE) > 0'
	#query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, status FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND AirlineName = %s'
	cursor.execute(query, (session['email'][2]))
	airline_flights = cursor.fetchall()
	cursor.close()
	return render_template('staff.html', flights = airline_flights, Airline = session['email'][2])

@app.route('/staffinput', methods=['GET', 'POST'])
def staffinput():
	FlightNumber = request.form["Flight Number"]
	Date = request.form["Departing Date"]
	DepartureTime = request.form["Departing Time"]
	ArrivalDate = request.form["Arrival Date"]
	ArrivalTime = request.form["Arrival Time"]
	BasePrice = request.form["Base Price"]
	Status = request.form["Status"]
	AirplaneID = request.form["Airplane ID"]
	DepartingAirport = request.form["Departing Airport ID"]
	ArrivingAirport = request.form["Arriving Airport ID"]

	cursor = conn.cursor()
	query = 'INSERT INTO flight VALUES (%s, %s, %s, "China Eastern", %s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, BasePrice, Status, AirplaneID, DepartingAirport, ArrivingAirport))
	depart_data = cursor.fetchall()

	for each in depart_data:   #prints out all the flights we have THIS IS A TEST
			print(each)
	cursor.close()

	return redirect(url_for('staff'))

#Update the status of the flight
@app.route('/staff_update_status', methods=['GET', 'POST'])
def staff_update_status():
	FlightNumber = request.form["FlightNumber"]
	Date = request.form["DepartureDate"]
	Time = request.form["DepartureTime"]
	print(FlightNumber)
	print(Date)
	print(Time)
	return render_template('status_update.html', FNumber = FlightNumber, date = Date, time = Time)

@app.route('/update_status', methods=['PUT', 'POST'])
def update_status():
	FlightNumber = request.form["FlightNumber"]
	Date = request.form["DepartureDate"]
	Time = request.form["DepartureTime"]
	Status = request.form["Status"]

	print(FlightNumber)
	print(Date)
	print(Time)
	print(Status)

	cursor = conn.cursor()
	query = 'UPDATE flight SET Status = %s WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
	cursor.execute(query, (Status, FlightNumber, Date, Time))
	conn.commit()
	cursor.close()
	return redirect(url_for('staff'))

#Define route for loginfork // this is where we pick is a user or staff log in
@app.route('/loginfork')
def loginfork():
	return render_template('loginfork.html')

#Define route for login
@app.route('/userlogin', methods=['GET', 'POST'])
def userLogin():
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid Credential'
		else:
			return redirect(url_for('customerhome'))
	return render_template('userlogin.html', error = error)



#Authenticates the login
@app.route('/userLoginAuth', methods=['GET', 'POST'])
def userLoginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE CustomerEmail = %s AND password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#double check for password error

		# TODO
		# cursor = conn.cursor()
		# query = 'SELECT password FROM customer WHERE CustomerEmail = %s'
		# cursor.execute(query, (username))
		# pw = cursor.fetchone()
		# print("printint", pw["password"])
		# if pw["password"].hexdigest() != password:
		# 	cursor.close()
		# 	error = 'Invalid password'
		# 	return render_template('userlogin.html', error = error)


		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('customerhome'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('userlogin.html', error=error)


#Define route for staff login
@app.route('/stafflogin', methods=['GET', 'POST'])
def staffLogin():
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid Credential'
		else:
			return redirect(url_for('staff'))
	return render_template('stafflogin.html', error = error)

#Authenticates the staff login
@app.route('/staffLoginAuth', methods=['GET', 'POST'])
def staffLoginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM airlinestaff WHERE StaffUsername = %s and password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('staff'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('stafflogin.html', error=error)



# #Define route for register
# @app.route('/register')
# def register():
# 	return render_template('register.html')
@app.route('/registerfork')
def registerfork():
	return render_template('registerfork.html')

#Define route for reg
@app.route('/userRegister', methods=['GET', 'POST'])
def userRegister():
	return render_template('userRegister.html')


#Authenticates the register
@app.route('/userRegisterAuth', methods=['GET', 'POST'])
def userRegisterAuth():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	customername = request.form['fullname']
	BuildingNo = request.form['BuildingNo']
	street = request.form['street']
	city = request.form['city']

	state = request.form['state']
	phoneNo = request.form['phoneNo']
	passportNo = request.form['passportNo']
	passportExp = request.form['passportExp']
	passportCntry = request.form['passportCntry']
	dob = request.form['dob']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE CustomerEmail = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('userRegister.html', error = error)
	else:
		ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (email, password, customername, BuildingNo, street, city, state, phoneNo, passportNo, passportExp, passportCntry, dob))
		# TODO
		# cursor.execute(ins, (email, hashlib.md5(password.encode('utf8')), customername, BuildingNo, street, city, state, phoneNo, passportNo, passportExp, passportCntry, dob))
		conn.commit()
		cursor.close()
		return render_template('userLogin.html')

#Define route for register
@app.route('/staffRegister', methods=['GET', 'POST'])
def staffRegister():
	return render_template('staffRegister.html')

#Authenticates the register
@app.route('/staffRegisterAuth', methods=['GET', 'POST'])
def staffRegisterAuth():
	#grabs information from the forms
	staffUsername = request.form['staffUsername']
	password = request.form['password']
	firstname = request.form['firstName']
	lastName = request.form['lastName']
	dob = request.form['dob']
	airlineName = request.form['airlineName']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM airlinestaff WHERE StaffUsername = %s'
	cursor.execute(query, (staffUsername))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('staffRegister.html', error = error)
	else:
		ins = 'INSERT INTO airlinestaff VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (staffUsername, password, firstname, lastName, dob, airlineName))
		conn.commit()
		cursor.close()
		return render_template('staffLogin.html')



@app.route('/home')
def home():
    print("hihi")
    # username = session['username']
    # cursor = conn.cursor();
    # query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    # cursor.execute(query, (username))
    # data1 = cursor.fetchall() 
    # for each in data1:
    #     print(each['blog_post'])
    # cursor.close()
    # return render_template('home.html', username=username, posts=data1)
    return render_template('home.html')                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         



####################### CUSTOMERHOME
@app.route('/customerhome')
def customerhome():
	#username = session['username']
	cursor = conn.cursor();

	# duplicate of Kevin's flights code
	# need to update to limit to purchased flights
	query = 'SELECT * FROM flight WHERE DepartureDate > CURRENT_DATE or (DepartureDate = CURRENT_DATE and DepartureTime > CURRENT_TIMESTAMP)'
	cursor.execute(query) #Runs the query
	flight_data = cursor.fetchall() #Gets the data from ran SQL query

	#Tests
	for each in flight_data:   #prints out all the flights
		print(each['FlightNumber'],each['DepartureDate'], each['DepartureTime'])

	cursor.close()

	return render_template('CustomerHome.html', flights=flight_data)

####################### CUSTOMERREVIEW
@app.route('/customerreview')
def customerreview():
	return render_template('CustomerReview.html')

####################### CUSTOMERREVIEW
@app.route('/customersearchflights')
def customersearchflights():
	return render_template('CustomerSearchFlights.html')
	

		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	cursor = conn.cursor();
	blog = request.form['blog']
	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	cursor.execute(query, (blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 3306, debug = True)