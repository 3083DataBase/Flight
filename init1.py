#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

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
	session['user'] = [None, 'Guest', 0]    #Creates a session, will hold [staffusername / customer email, name of the customer or just Guest if not logged in / airline, 0 for customers, 1 for flight staff]
	#cursor = conn.cursor();

	#after this Kevin needs to change for search
	#query = 'SELECT * FROM flight WHERE DepartureDate > CURRENT_DATE or (DepartureDate = CURRENT_DATE and DepartureTime > CURRENT_TIMESTAMP)'
	#cursor.execute(query) #Runs the query
	#flight_data = cursor.fetchall() #Gets the data from ran SQL query

	#Tests
	#for each in flight_data:   #prints out all the flights we have THIS IS A TEST
	#	print(each['FlightNumber'],each['DepartureDate'], each['DepartureTime'])


	#cursor.close()
	return render_template('flights.html', name1=session['user'][1])

#Searches for the flights of the inputs (Works for guests or for people logged in)
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

#Redirects to flight_status.html (Goes from staff to flight_status)
@app.route('/flight_status', methods=['GET', 'POST'])
def flight_status():
	return render_template('flight_status.html',  name1=session['user'][1])

#Gets the Flight from the data base
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

#Holds all the code for the staff to input into flights (Required for staff to be logged in)
@app.route('/staff', methods=['GET', 'POST'])
def staff():

	#if(session['user'][2] != 1):
	#	return redirect(url_for('staffLogin'))
		
	Airline = session['user'][1]
	print(Airline)
	cursor = conn.cursor()
	query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, status FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND AirlineName = %s AND DATEDIFF(DepartureDate, CURRENT_DATE) < 30 AND DATEDIFF(DepartureDate, CURRENT_DATE) > 0'
	
	query_airport = 'SELECT * FROM airport'
	cursor.execute(query, (Airline))
	airline_flights = cursor.fetchall()

	cursor.execute(query_airport)

	airports = cursor.fetchall()
	
	cursor.close()

	return render_template('staff.html', flights = airline_flights, Airline = Airline)

@app.route('/add_flight', methods=['GET', 'POST'])
def add_flight():
	return render_template('staff_add_flight.html')

#Inserts the Flight into the data base
@app.route('/staffinput', methods=['GET', 'POST'])
def staffinput():
	FlightNumber = request.form["Flight Number"]
	DepartureDate = request.form["Departing Date"]
	DepartureTime = request.form["Departing Time"]
	ArrivalDate = request.form["Arrival Date"]
	ArrivalTime = request.form["Arrival Time"]
	BasePrice = request.form["Base Price"]
	Status = request.form["Status"]
	AirplaneID = request.form["Airplane ID"]
	DepartingAirport = request.form["Departing Airport ID"]
	ArrivingAirport = request.form["Arriving Airport ID"]

	Airline = session['user'][1]

	cursor = conn.cursor()
	query = 'INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (FlightNumber, DepartureDate, DepartureTime, Airline, ArrivalDate, ArrivalTime, BasePrice, Status, AirplaneID, DepartingAirport, ArrivingAirport))
	depart_data = cursor.fetchall()

	conn.commit()
	cursor.close()

	return redirect(url_for('staff'))

#Transfers the data to status_update.html (opens status_update.html)
@app.route('/staff_update_status', methods=['GET', 'POST'])
def staff_update_status():
	FlightNumber = request.form["FlightNumber"]
	Date = request.form["DepartureDate"]
	Time = request.form["DepartureTime"]

	return render_template('status_update.html', FNumber = FlightNumber, date = Date, time = Time)

#Updates the Status of the plane (redirects to '/staff')
@app.route('/update_status', methods=['PUT', 'POST'])
def update_status():
	FlightNumber = request.form["FlightNumber"]
	Date = request.form["DepartureDate"]
	Time = request.form["DepartureTime"]
	Status = request.form["Status"]

	cursor = conn.cursor()
	query = 'UPDATE flight SET Status = %s WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
	cursor.execute(query, (Status, FlightNumber, Date, Time))
	conn.commit()
	cursor.close()
	return redirect(url_for('staff'))

@app.route('/add_airplane_page', methods=['GET', 'POST'])
def add_airplane_page():
	return render_template('staff_add_airplane.html')


#Shows all the planes the airline has and the confirmation button (Opens airplane.html)
@app.route('/add_airplane_confirmation', methods=['GET', 'POST'])
def add_airplane_confirmation():
	Airline = session['user'][1]
	AirplaneID = request.form["AirplaneID"]
	NumSeats = request.form["NumSeats"]

	cursor = conn.cursor()
	query_check = 'SELECT AirplaneID FROM airplane WHERE AirlineName = %s AND AirplaneID = %s'
	cursor.execute(query_check, (Airline, AirplaneID))
	check = cursor.fetchall()

	if(check == ()):
		query = 'SELECT AirplaneID, NumSeats FROM airplane WHERE AirlineName = %s'
		cursor.execute(query, Airline)
		airplanes = cursor.fetchall()
		cursor.close()
		return render_template('airplane.html', airplanes = airplanes, Airline = Airline, AirplaneID = AirplaneID, NumSeats = NumSeats)
	else:
		cursor.close()
		return redirect(url_for('add_airplane'))

#Adds the plane to the database (redirects to '/staff')
@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
	Airline = session['user'][1]
	AirplaneID = request.form["AirplaneID"]
	NumSeats = request.form["NumSeats"]
	
	cursor = conn.cursor()

	query = 'INSERT INTO airplane VALUES (%s, %s, %s)' 
	cursor.execute(query, ( AirplaneID, Airline, NumSeats))
	conn.commit()

	cursor.close()
	return redirect(url_for('add_airplane_page'))

@app.route('/add_airport_page', methods=['GET', 'POST'])
def add_airport_page():
	cursor = conn.cursor()

	query_airport = 'SELECT * FROM airport'
	cursor.execute(query_airport)
	airports = cursor.fetchall()
	
	cursor.close()
	return render_template('staff_add_airport.html', Airports = airports)

@app.route('/add_airport', methods=['PUT', 'POST'])
def add_airport():
	AirportID = request.form["AirportID"]
	AirportName	= request.form["AirportName"]
	City = request.form["City"]
	
	print(AirportID)
	cursor = conn.cursor()
	query_check = 'SELECT AirportID FROM airport WHERE AirportID = %s'
	cursor.execute(query_check, AirportID)
	check = cursor.fetchall()

	print(check)

	if(check == ()):
		print()
		query = 'INSERT INTO airport VALUES (%s, %s, %s)'
		cursor.execute(query, (AirportID, AirportName, City))
		conn.commit()
		cursor.close()
		return redirect(url_for('add_airport_page'))
	else:
		cursor.close()
		print("didnt work")
		error = 'Invalid login or username'
		return redirect(url_for('add_airport_page'))
	
#Staff_info gets the info that the staff should be able to see
@app.route('/staff_info', methods=['GET', 'POST'])
def staff_info():

	#if(session['user'][2] != 1):
	#	return redirect(url_for('staffLogin'))

	print("In Staff Info")
	print(session['user'])
	
	Airline = session['user'][1]
	cursor = conn.cursor()

	query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, status FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND AirlineName = %s AND DATEDIFF(DepartureDate, CURRENT_DATE) < 0'
	
	cursor.execute(query, (Airline))
	airline_flights = cursor.fetchall()

	frequent_flyer_query = 'SELECT CustomerName FROM customer NATURAL JOIN ticket WHERE DATEDIFF(CURRENT_DATE,PurchaseDate) < 365 AND AirlineName = %s ORDER BY SoldPrice DESC'
	
	cursor.execute(frequent_flyer_query, (Airline))
	frequent_flyer = cursor.fetchall()
	frequent_flyer = frequent_flyer[0]['CustomerName']

	customer_query = 'SELECT CustomerName, CustomerEmail FROM customer NATURAL JOIN ticket WHERE AirlineName = %s'
	
	cursor.execute(customer_query, (Airline))
	customers = cursor.fetchall()

	query = 'SELECT SUM(SoldPrice) FROM ticket WHERE AirlineName = %s AND DATEDIFF(CURRENT_DATE,PurchaseDate) < 30'
	cursor.execute(query, Airline)
	total_month = cursor.fetchall()
	total_month = total_month[0]['SUM(SoldPrice)']

	query = 'SELECT SUM(SoldPrice) FROM ticket WHERE AirlineName = %s AND DATEDIFF(CURRENT_DATE,PurchaseDate) < 365'
	cursor.execute(query, Airline)
	total_year = cursor.fetchall()
	total_year= total_year[0]['SUM(SoldPrice)']

	query = 'SELECT b.City FROM ticket NATURAL JOIN (flight, airport as a, airport as b) WHERE DepartAirportID = a.AirportID AND ArrivalAirportID = b.AirportID AND AirlineName = %s AND DATEDIFF(CURRENT_DATE,DepartureDate) < 365 GROUP BY b.City ORDER BY COUNT(*) DESC'
	cursor.execute(query, Airline)
	popular_year = cursor.fetchall()
	popular_year = popular_year[0]['City']

	query = 'SELECT b.City FROM ticket NATURAL JOIN (flight, airport as a, airport as b) WHERE DepartAirportID = a.AirportID AND ArrivalAirportID = b.AirportID AND AirlineName = %s AND DATEDIFF(CURRENT_DATE,DepartureDate) < 90 GROUP BY b.City ORDER BY COUNT(*) DESC'
	cursor.execute(query, Airline)
	popular_month = cursor.fetchall()
	if(popular_month != ()):
		popular_month = popular_month[0]['City']
	else:
		popular_month = None
	cursor.close()


	return render_template('staff_info.html', flights = airline_flights, flyer = frequent_flyer, customers = customers, Airline = Airline, Year = total_year, Month = total_month, pop_year = popular_year, pop_month = popular_month)
	
@app.route('/reviews', methods=['GET', 'POST'])
def reviews():

	FlightNumber = request.form["FlightNumber"]
	Date = request.form["DepartureDate"]
	Time = request.form["DepartureTime"]

	cursor = conn.cursor()
	query = 'SELECT Comment FROM views WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
	cursor.execute(query, (FlightNumber, Date, Time))
	comments = cursor.fetchall()

	average_query = 'SELECT AVG(Rate) FROM views WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
	cursor.execute(average_query, (FlightNumber, Date, Time))
	avg = cursor.fetchall()

	avg = avg[0]['AVG(Rate)']

	cursor.close()

	return render_template('staff_view_review.html', comments = comments, Avg = avg)

@app.route('/customer_flights', methods=['GET', 'POST'])
def customer_flights():

	Email = request.form["CustomerEmail"]
	Airline = session['user'][1]

	print(Airline)
	print(Email)

	cursor = conn.cursor()
	query = 'SELECT TicketID, FlightNumber, DepartureDate, SoldPrice FROM ticket NATURAL JOIN flight WHERE AirlineName = %s AND CustomerEmail = %s'
	cursor.execute(query, (Airline, Email))
	customer_flights = cursor.fetchall()
	cursor.close()

	print(customer_flights)

	return render_template('staff_customer_view.html', flights = customer_flights)

@app.route('/reports', methods=['GET', 'POST'])
def reports():
	Airline = session['user'][1]

	cursor = conn.cursor()
	year_query = 'SELECT COUNT(TicketID) FROM ticket WHERE AirlineName = %s AND YEAR(PurchaseDate) = (YEAR(CURRENT_DATE) - 1)'
	cursor.execute(year_query, Airline)
	year_tickets = cursor.fetchall()

	month_query = 'SELECT COUNT(TicketID) FROM ticket WHERE AirlineName = %s AND MONTH(PurchaseDate) = (MONTH(CURRENT_DATE) - 1)'
	cursor.execute(month_query, Airline)
	month_tickets = cursor.fetchall()

	year_tickets = year_tickets[0]['COUNT(TicketID)']
	month_tickets = month_tickets[0]['COUNT(TicketID)']

	cursor.close()
	return render_template('reports.html', year = year_tickets, month = month_tickets)

@app.route('/reports_inrange', methods=['GET', 'POST'])
def reports_inrange():
	Airline = session['user'][1]
	start = request.form["StartingDate"]
	end = request.form["EndingDate"]

	cursor = conn.cursor()

	year_query = 'SELECT COUNT(TicketID) FROM ticket WHERE AirlineName = %s AND YEAR(PurchaseDate) = (YEAR(CURRENT_DATE) - 1)'
	cursor.execute(year_query, Airline)
	year_tickets = cursor.fetchall()

	month_query = 'SELECT COUNT(TicketID) FROM ticket WHERE AirlineName = %s AND MONTH(PurchaseDate) = (MONTH(CURRENT_DATE) - 1)'
	cursor.execute(month_query, Airline)
	month_tickets = cursor.fetchall()

	year_tickets = year_tickets[0]['COUNT(TicketID)']
	month_tickets = month_tickets[0]['COUNT(TicketID)']

	query = 'SELECT COUNT(TicketID) FROM ticket WHERE AirlineName = %s AND PurchaseDate > %s AND PurchaseDate < %s'
	cursor.execute(query, (Airline, start, end))
	tickets = cursor.fetchall()
	tickets = tickets[0]['COUNT(TicketID)']

	return render_template('reports.html',year = year_tickets, month = month_tickets, tickets = tickets)

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
	email = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT CustomerEmail, CustomerName FROM customer WHERE CustomerEmail = %s AND password = md5(%s)'
	cursor.execute(query, (email, password))


	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row

	cursor.close()
	error = None
	if(data):
		#double check for password error

		#creates a session for the the user
		#session is a built in
		print("DATA: ", data)
		print("ERROR: ", [data['CustomerEmail'], data['CustomerName']])
		print("PRE: ", session)
		session.pop('user')
		print("POP: ", session)

		session['user'] = [data['CustomerEmail'], data['CustomerName'], 1]
		print("POST: ", session)
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
	query = 'SELECT StaffUsername, AirlineName FROM airlinestaff WHERE StaffUsername = %s and password = md5(%s)'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchall()
	# print(data)
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		print(session)
		session.pop('user')
		session['user'] = [data[0]['StaffUsername'], data[0]['AirlineName'], 1]
		print(session)
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
		ins = 'INSERT INTO customer VALUES(%s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		# cursor.execute(ins, (email, password, customername, BuildingNo, street, city, state, phoneNo, passportNo, passportExp, passportCntry, dob))
		cursor.execute(ins, (email, password, customername, BuildingNo, street, city, state, phoneNo, passportNo, passportExp, passportCntry, dob))
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
		ins = 'INSERT INTO airlinestaff VALUES(%s, md5(%s), %s, %s, %s, %s)'
		cursor.execute(ins, (staffUsername, password, firstname, lastName, dob, airlineName))
		conn.commit()
		cursor.close()
		return render_template('staffLogin.html')




# NOT USED
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

	# need to update to limit to purchased flights
	query = 'SELECT * FROM flight WHERE DepartureDate > CURRENT_DATE or (DepartureDate = CURRENT_DATE and DepartureTime > CURRENT_TIMESTAMP)'
	cursor.execute(query) #Runs the query
	flight_data = cursor.fetchall() #Gets the data from ran SQL query

	#Tests
	for each in flight_data:   #prints out all the flights
		print(each['FlightNumber'],each['DepartureDate'], each['DepartureTime'])

	cursor.close()

	return render_template('CustomerHome.html', flights=flight_data)

####################### CUSTOMERPASTFLIGHT
@app.route('/customerpastflightsview', methods=['GET', 'POST'])
def customerpastflightsview():
	#username = session['username']
	cursor = conn.cursor();

	# need to update to limit to purchased flights
	# need to take from purchase table instead of flights table
	query_past = 'SELECT * FROM flight WHERE DepartureDate < CURRENT_DATE or (DepartureDate = CURRENT_DATE and ArrivalTime < CURRENT_TIMESTAMP)'
	cursor.execute(query_past) #Runs the query
	past_flight_data = cursor.fetchall()

	#Tests
	for each in past_flight_data:   #prints out all the flights
		print(each['FlightNumber'],each['DepartureDate'], each['DepartureTime'])

	cursor.close()

	return render_template('CustomerPastFlight.html', flights=past_flight_data)

####################### CUSTOMERREVIEW
@app.route('/customerreview', methods=['GET', 'POST'])
def customerreview():
	#CustomerEmail = request.form["CustomerEmail"]
	CustomerEmail = request.form.get("CustomerEmail")
	#FlightNumber = request.form["FlightNumber"]
	FlightNumber = request.form.get("FlightNumber")
	#DepartureDate = request.form["DepartureDate"]
	DepartureDate = request.form.get("DepartureDate")
	#DepartureTime = request.form["DepartureTime"]
	DepartureTime = request.form.get("DepartureTime")

	cursor = conn.cursor();
	#rate = request.form['rating']
	rate = request.form.get('rating')
	#comment = request.form['comment']
	comment = request.form.get('comment')
	query = 'UPDATE views SET Rate = %s, Comment = %s WHERE CustomerEmail = %s AND FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
	cursor.execute(query, (rate, comment))
	conn.commit()
	cursor.close()
	
	return render_template('CustomerReview.html')

####################### CUSTOMERREVIEW
@app.route('/customersearchflights', methods=['GET', 'POST'])
def customersearchflights():
	#checkbox = request.form["checkbox"]
	checkbox = request.form.get("checkbox")
	#departing = request.form["Departing"]
	departing = request.form.get("Departing")
	#departing_date = request.form["Departure Date"]
	departing_date = request.form.get("Departure Date")
	#arriving = request.form["Arriving"]
	arriving = request.form.get("Arriving")

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
	return render_template('CustomerSearchFlights.html', depart_flights=depart_data, arrival_flights=arriving_data)






	

#NOT USED
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['user']
	cursor = conn.cursor();
	blog = request.form['blog']
	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	cursor.execute(query, (blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('user')
	session['user'] = [None, 'Guest', 0]
	return redirect('/loginfork')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 3306, debug = True)