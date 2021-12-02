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
	return render_template('flights.html', name1="guest")

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

#Holds all the code for the staff to input into flights (Required for staff to be logged in)
@app.route('/staff', methods=['GET', 'POST'])
def staff():
	Airline = session['test'][1]
	cursor = conn.cursor()
	query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, status FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND AirlineName = %s AND DATEDIFF(DepartureDate, CURRENT_DATE) < 0'
	
	query_airport = 'SELECT * FROM airport'
	#query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, status FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND AirlineName = %s'
	cursor.execute(query, (Airline))
	airline_flights = cursor.fetchall()

	cursor.execute(query_airport)

	airports = cursor.fetchall()
	
	cursor.close()

	return render_template('staff.html', flights = airline_flights, Airports = airports, Airline = session['test'][1])

#Inserts the Flight into the data base
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

#Shows all the planes the airline has and the confirmation button (Opens airplane.html)
@app.route('/add_airplane_confirmation', methods=['GET', 'POST'])
def add_airplane_confirmation():
	Airline = session['test'][1]
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
		return redirect(url_for('staff'))

#Adds the plane to the database (redirects to '/staff')
@app.route('/add_airplane', methods=['PUT', 'POST'])
def add_airplane():
	Airline = session['test'][1]
	AirplaneID = request.form["AirplaneID"]
	NumSeats = request.form["NumSeats"]
	
	cursor = conn.cursor()
	query = 'INSERT INTO airplane VALUES (%s, %s, %s)' 
	cursor.execute(query, ( AirplaneID, Airline, NumSeats))
	conn.commit()
	cursor.close()
	return redirect(url_for('staff'))

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
		return redirect(url_for('staff'))
	else:
		cursor.close()
		print("didnt work")
		error = 'Invalid login or username'
		return redirect(url_for('staff'))
	
#Staff_info gets the info that the staff should be able to see
@app.route('/staff_info', methods=['GET', 'POST'])
def staff_info():
	
	Airline = session['test'][1]
	cursor = conn.cursor()
	query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, status FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND AirlineName = %s AND DATEDIFF(DepartureDate, CURRENT_DATE) < 0'
	
	cursor.execute(query, (Airline))
	airline_flights = cursor.fetchall()

	frequent_flyer_query = 'SELECT CustomerName FROM customer NATURAL JOIN ticket WHERE DATEDIFF(PurchaseDate, CURRENT_DATE) < 365 AND AirlineName = %s ORDER BY SoldPrice DESC'
	
	cursor.execute(frequent_flyer_query, (Airline))
	

	frequent_flyer = cursor.fetchall()

	frequent_flyer = frequent_flyer[0]['CustomerName']

	cursor.close()

	return render_template('staff_info.html', flights = airline_flights, flyer = frequent_flyer, Airline = Airline)

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

	return render_template('staff_view_review.html', flights = comments, Avg = avg)


#Define route for loginfork // this is where we pick is a user or staff log in
@app.route('/loginfork')
def loginfork():
	return render_template('loginfork.html')

#Define route for login
@app.route('/login')
def login():

	session['test'] = ['test_username', "China Eastern", 1]       #FOR TESTING GOTTA DELETE

	return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s and password = %s'
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
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO user VALUES(%s, %s)'
		cursor.execute(ins, (username, password))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/home')
def home():
    
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, (username))
    data1 = cursor.fetchall() 
    for each in data1:
        print(each['blog_post'])
    cursor.close()
    return render_template('home.html', username=username, posts=data1)



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