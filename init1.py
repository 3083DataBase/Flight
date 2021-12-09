#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import random

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
	session['user'] = [None, 'Guest', -1]    #Creates a session, will hold [staffusername / customer email, name of the customer or just Guest if not logged in / airline, 0 for customers, 1 for flight staff]
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
	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	Airline = session['user'][1]
	return render_template('staff.html', Airline = Airline)

@app.route('/view_flights', methods=['GET', 'POST'])
def view_flights():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	Airline = session['user'][1]
	cursor = conn.cursor()

	#finds the flights in 30 days
	query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, status FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND AirlineName = %s AND DATEDIFF(DepartureDate, CURRENT_DATE) < 30 AND DATEDIFF(DepartureDate, CURRENT_DATE) > 0 ORDER BY DepartureDate, DepartureTime'
	cursor.execute(query, Airline)
	airline_flights = cursor.fetchall()
	
	cursor.close()
	return render_template('staff_view_flights.html', flights = airline_flights, Airline = Airline)

@app.route('/staff_search_flights', methods=['GET', 'POST'])
def staff_search_flights():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	Airline = session['user'][1]
	checkbox = request.form["checkbox"]

	print(checkbox)
	cursor = conn.cursor()
	if(checkbox == "DateSearch"):
		start = request.form["Inital Date"] 
		end = request.form["Ending Date"]

		print(start)
		print(end)

		query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, status FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND DepartureDate > %s and DepartureDate < %s AND AirlineName = %s ORDER BY DepartureDate, DepartureTime'
		cursor.execute(query, (start, end, Airline)) #Runs the query
		date = cursor.fetchall() #Gets the data from ran SQL query
		print(date)
		cursor.close()
		return render_template('staff_view_flights.html', flights=date, Airline = Airline)
	else:    #Is the one way search
		depart = request.form["Departing"] 
		arrival = request.form["Arriving"]

		if depart == arrival:
			return redirect(url_for('view_flights'))

		query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName , status FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND AirlineName = %s ORDER BY DepartureDate, DepartureTime'
		cursor.execute(query, (depart, depart, arrival, arrival, Airline)) #Runs the query
		dest = cursor.fetchall() #Gets the data from ran SQL query
		cursor.close()
		return render_template('staff_view_flights.html', flights=dest, Airline = Airline)

@app.route('/staff_view_customer', methods=['GET', 'POST'])
def staff_view_customer():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	FlightNumber = request.form["FlightNumber"]
	Date = request.form["DepartureDate"]
	Time = request.form["DepartureTime"]

	Airline = session['user'][1]

	cursor = conn.cursor()
	query = 'SELECT CustomerName FROM customer NATURAL JOIN ticket WHERE FlightNumber = %s AND AirlineName = %s'
	cursor.execute(query, (FlightNumber, Airline))
	customers = cursor.fetchall()
	cursor.close()

	return render_template('staff_view_customers.html', customers = customers, Airline = Airline)

# Loads staff_add_flight.html from staff.html
@app.route('/add_flight', methods=['GET', 'POST'])
def add_flight():
	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	Airline = session['user'][1]

	return render_template('staff_add_flight.html',Airline = Airline)

#Inserts the Flight into the data base
@app.route('/staffinput', methods=['GET', 'POST'])
def staffinput():
	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	error = None

	FlightNumber = request.form["Flight Number"]
	Airline = session['user'][1]
	AirplaneID = request.form["Airplane ID"]
	DepartingAirport = request.form["Departing Airport ID"]
	ArrivingAirport = request.form["Arriving Airport ID"]

	cursor = conn.cursor()
	query = 'SELECT FlightNumber FROM flight WHERE FlightNumber = %s AND AirlineName = %s'
	cursor.execute(query, (FlightNumber, Airline))
	flights = cursor.fetchall()
	#print(flights)

	query = 'SELECT AirplaneID FROM airplane WHERE AirplaneID = %s AND AirlineName = %s'
	cursor.execute(query, (AirplaneID, Airline))
	airplane = cursor.fetchall()
	#print(airplane)

	query = 'SELECT AirportID FROM airport WHERE AirportID = %s'
	cursor.execute(query, DepartingAirport)
	dep_airport = cursor.fetchall()
	#print(dep_airport)

	query = 'SELECT AirportID FROM airport WHERE AirportID = %s'
	cursor.execute(query, ArrivingAirport)
	ari_airport = cursor.fetchall()
	print(ari_airport)

	# Checks if the Flight Number Exists already
	if flights != ():
		cursor.close()
		error = "Flight Number already exists"
		return render_template('staff_add_flight.html', error = error, Airline = Airline)
	
	# Checks if the Airplane ID exists
	if airplane == ():
		cursor.close()
		error = "Airplane does not exist"
		return render_template('staff_add_flight.html', error = error, Airline = Airline)

	# Checks if the departing Airport Exists
	if dep_airport == ():
		cursor.close()
		error = "Departing Airport does not exist"
		return render_template('staff_add_flight.html', error = error, Airline = Airline)

	# Checks if the Arriving Airport Exists
	if ari_airport == ():
		cursor.close()
		error = "Arriving Airport does not exist"
		return render_template('staff_add_flight.html', error = error, Airline = Airline)

	# Checks if the departing and arriving airports the same
	if DepartingAirport == ArrivingAirport:
		cursor.close()
		error = "Departing and Arriving airports cant be the same"
		return render_template('staff_add_flight.html', error = error, Airline = Airline)

	DepartureDate = request.form["Departing Date"]
	DepartureTime = request.form["Departing Time"]
	ArrivalDate = request.form["Arrival Date"]
	ArrivalTime = request.form["Arrival Time"]
	BasePrice = request.form["Base Price"]
	Status = request.form["Status"]


	query = 'INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (FlightNumber, DepartureDate, DepartureTime, Airline, ArrivalDate, ArrivalTime, BasePrice, Status, AirplaneID, DepartingAirport, ArrivingAirport))
	depart_data = cursor.fetchall()

	conn.commit()
	cursor.close()

	return redirect(url_for('add_flight'))

#Transfers the data to status_update.html (opens status_update.html)
@app.route('/staff_update_status', methods=['GET', 'POST'])
def staff_update_status():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	FlightNumber = request.form["FlightNumber"]
	Date = request.form["DepartureDate"]
	Time = request.form["DepartureTime"]

	Airline = session['user'][1]

	return render_template('status_update.html', FNumber = FlightNumber, date = Date, time = Time, Airline = Airline)

#Updates the Status of the plane (redirects to '/staff')
@app.route('/update_status', methods=['PUT', 'POST'])
def update_status():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	FlightNumber = request.form["FlightNumber"]
	Date = request.form["DepartureDate"]
	Time = request.form["DepartureTime"]
	Status = request.form["Status"]

	cursor = conn.cursor()
	query = 'UPDATE flight SET Status = %s WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
	cursor.execute(query, (Status, FlightNumber, Date, Time))
	conn.commit()
	cursor.close()
	return redirect(url_for('view_flights'))

@app.route('/add_airplane_page', methods=['GET', 'POST'])
def add_airplane_page():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	Airline = session['user'][1]
	cursor = conn.cursor()
	query = 'SELECT AirplaneID, NumSeats FROM airplane WHERE AirlineName = %s'
	cursor.execute(query, Airline)
	airplanes = cursor.fetchall()
	return render_template('staff_add_airplane.html', airplanes = airplanes, Airline = Airline)


#Shows all the planes the airline has and the confirmation button (Opens airplane.html)
@app.route('/add_airplane_confirmation', methods=['GET', 'POST'])
def add_airplane_confirmation():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

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
		return redirect(url_for('add_airplane_page'))

#Adds the plane to the database (redirects to '/staff')
@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	Airline = session['user'][1]
	AirplaneID = request.form["AirplaneID"]
	NumSeats = request.form["NumSeats"]
	
	cursor = conn.cursor()

	query = 'INSERT INTO airplane VALUES (%s, %s, %s)' 
	cursor.execute(query, ( AirplaneID, Airline, NumSeats))
	conn.commit()

	cursor.close()
	return redirect(url_for('add_airplane_page'))

# Finds all the Airports
@app.route('/add_airport_page', methods=['GET', 'POST'])
def add_airport_page():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	Airline = session['user'][1]

	cursor = conn.cursor()

	query_airport = 'SELECT * FROM airport'
	cursor.execute(query_airport)
	airports = cursor.fetchall()
	cursor.close()
	return render_template('staff_add_airport.html', Airports = airports, Airline = Airline)

# Checks and inserts airports that meet criteria
@app.route('/add_airport', methods=['PUT', 'POST'])
def add_airport():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	AirportID = request.form["AirportID"]
	AirportName	= request.form["AirportName"]
	City = request.form["City"]
	
	print(AirportID)
	cursor = conn.cursor()
	query_check = 'SELECT AirportID FROM airport WHERE AirportID = %s or AirportName = %s'
	cursor.execute(query_check, (AirportID, AirportName))
	check = cursor.fetchall()

	if(check == ()):
		query = 'INSERT INTO airport VALUES (%s, %s, %s)'
		cursor.execute(query, (AirportID, AirportName, City))
		conn.commit()
		cursor.close()
		return redirect(url_for('add_airport_page'))
	else:
		cursor.close()
		error = 'Invalid login or username'
		return redirect(url_for('add_airport_page'))

# Loads staff_review_page.html from staff.html
@app.route('/view_review', methods=['GET', 'POST'])
def view_review():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	Airline = session['user'][1]
	cursor = conn.cursor()

	query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, status FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND AirlineName = %s AND ArrivalDate < CURRENT_DATE ORDER BY ArrivalDate'
	
	cursor.execute(query, (Airline))
	airline_flights = cursor.fetchall()
	cursor.close()
	return render_template('staff_review_page.html', flights = airline_flights, Airline = Airline)

#Staff_info gets the info that the staff should be able to see (NOT GONNA BE USED)
#@app.route('/staff_info', methods=['GET', 'POST'])
#def staff_info():

	#if(session['user'][2] != 1):
	#	return redirect(url_for('staffLogin'))

	#print("In Staff Info")
	#print(session['user'])
	
	#Airline = session['user'][1]
	#cursor = conn.cursor()

	#query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, status FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND AirlineName = %s AND DATEDIFF(DepartureDate, CURRENT_DATE) < 0'
	
	#cursor.execute(query, (Airline))
	#airline_flights = cursor.fetchall()

	#frequent_flyer_query = 'SELECT CustomerName FROM customer NATURAL JOIN ticket WHERE DATEDIFF(CURRENT_DATE,PurchaseDate) < 365 AND AirlineName = %s ORDER BY SoldPrice DESC'
	
	#cursor.execute(frequent_flyer_query, (Airline))
	#frequent_flyer = cursor.fetchall()
	#frequent_flyer = frequent_flyer[0]['CustomerName']

	#customer_query = 'SELECT CustomerName, CustomerEmail FROM customer NATURAL JOIN ticket WHERE AirlineName = %s'
	
	#cursor.execute(customer_query, (Airline))
	#customers = cursor.fetchall()

	#query = 'SELECT SUM(SoldPrice) FROM ticket WHERE AirlineName = %s AND DATEDIFF(CURRENT_DATE,PurchaseDate) < 30'
	#cursor.execute(query, Airline)
	#total_month = cursor.fetchall()
	#total_month = total_month[0]['SUM(SoldPrice)']

	#query = 'SELECT SUM(SoldPrice) FROM ticket WHERE AirlineName = %s AND DATEDIFF(CURRENT_DATE,PurchaseDate) < 365'
	#cursor.execute(query, Airline)
	#total_year = cursor.fetchall()
	#total_year= total_year[0]['SUM(SoldPrice)']

	#query = 'SELECT b.City FROM ticket NATURAL JOIN (flight, airport as a, airport as b) WHERE DepartAirportID = a.AirportID AND ArrivalAirportID = b.AirportID AND AirlineName = %s AND DATEDIFF(CURRENT_DATE,DepartureDate) < 365 GROUP BY b.City ORDER BY COUNT(*) DESC'
	#cursor.execute(query, Airline)
	#popular_year = cursor.fetchall()
	#popular_year = popular_year[0]['City']

	#query = 'SELECT b.City FROM ticket NATURAL JOIN (flight, airport as a, airport as b) WHERE DepartAirportID = a.AirportID AND ArrivalAirportID = b.AirportID AND AirlineName = %s AND DATEDIFF(CURRENT_DATE,DepartureDate) < 90 GROUP BY b.City ORDER BY COUNT(*) DESC'
	#cursor.execute(query, Airline)
	#popular_month = cursor.fetchall()
	#if(popular_month != ()):
	#	popular_month = popular_month[0]['City']
	#else:
	#	popular_month = None
	#cursor.close()


	#return render_template('staff_info.html', flights = airline_flights, flyer = frequent_flyer, customers = customers, Airline = Airline, Year = total_year, Month = total_month, pop_year = popular_year, pop_month = popular_month)
	
# Gets all the reviews for a flight and shows it
@app.route('/reviews', methods=['GET', 'POST'])
def reviews():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	FlightNumber = request.form["FlightNumber"]
	Date = request.form["DepartureDate"]
	Time = request.form["DepartureTime"]

	Airline = session['user'][1]

	cursor = conn.cursor()
	query = 'SELECT Comment FROM views WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
	cursor.execute(query, (FlightNumber, Date, Time))
	comments = cursor.fetchall()

	average_query = 'SELECT AVG(Rate) FROM views WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
	cursor.execute(average_query, (FlightNumber, Date, Time))
	avg = cursor.fetchall()

	avg = avg[0]['AVG(Rate)']

	cursor.close()

	return render_template('staff_view_review.html', comments = comments, Avg = avg, Airline = Airline )

# Find the most frequent flyer and lists all customers from the airline
@app.route('/customer_view', methods=['GET', 'POST'])
def customer_view():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	Airline = session['user'][1]
	cursor = conn.cursor()

	frequent_flyer_query = 'SELECT CustomerName FROM customer NATURAL JOIN ticket WHERE DATEDIFF(CURRENT_DATE,PurchaseDate) < 365 AND AirlineName = %s ORDER BY SoldPrice DESC'
	
	cursor.execute(frequent_flyer_query, (Airline))
	frequent_flyer = cursor.fetchall()
	frequent_flyer = frequent_flyer[0]['CustomerName']

	customer_query = 'SELECT CustomerName, CustomerEmail FROM customer NATURAL JOIN ticket WHERE AirlineName = %s'
	
	cursor.execute(customer_query, (Airline))
	customers = cursor.fetchall()

	cursor.close()
	return render_template('staff_frequent_flyer.html', flyer = frequent_flyer, customers = customers, Airline = Airline)

# Gets the customers flights in that airline
@app.route('/customer_flights', methods=['GET', 'POST'])
def customer_flights():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

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

	return render_template('staff_customer_view.html', flights = customer_flights, Airline = Airline)

# Finds the amount of tickets sold last month and last year
@app.route('/reports', methods=['GET', 'POST'])
def reports():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	Airline = session['user'][1]

	cursor = conn.cursor()
	year_query = 'SELECT COUNT(TicketID) FROM ticket WHERE AirlineName = %s AND YEAR(PurchaseDate) = (YEAR(CURRENT_DATE) - 1)'
	cursor.execute(year_query, Airline)
	year_tickets = cursor.fetchall()

	month_query = 'SELECT COUNT(TicketID) FROM ticket WHERE AirlineName = %s AND MONTH(PurchaseDate) = (MONTH(CURRENT_DATE) - 1)'
	cursor.execute(month_query, Airline)
	month_tickets = cursor.fetchall()

	query = 'SELECT MONTH(PurchaseDate) Month, COUNT(TicketID) count FROM `ticket` WHERE YEAR(PurchaseDate) = YEAR(CURRENT_DATE) - 1 GROUP BY MONTH(PurchaseDate) AND AirlineName = %s'
	cursor.execute(query, Airline)
	chart = cursor.fetchall()

	blank_chart = []
	for i in range(1,13):
		blank_chart.append({'Month': i, 'count': 0})

	for month in chart:
		blank_chart[month['Month'] - 1]['count'] = month['count']

	year_tickets = year_tickets[0]['COUNT(TicketID)']
	month_tickets = month_tickets[0]['COUNT(TicketID)']

	cursor.close()
	return render_template('reports.html', year = year_tickets, month = month_tickets, Airline = Airline, table = blank_chart)

#finds the amount of tickets sold in the range dipicted
@app.route('/reports_inrange', methods=['GET', 'POST'])
def reports_inrange():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

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

	query = 'SELECT MONTH(PurchaseDate) Month, COUNT(TicketID) count FROM `ticket` WHERE YEAR(PurchaseDate) = YEAR(CURRENT_DATE) - 1 GROUP BY MONTH(PurchaseDate) AND AirlineName = %s'
	cursor.execute(query, Airline)
	chart = cursor.fetchall()

	blank_chart = []
	for i in range(1,13):
		blank_chart.append({'Month': i, 'count': 0})

	for month in chart:
		blank_chart[month['Month'] - 1]['count'] = month['count']

	return render_template('reports.html',year = year_tickets, month = month_tickets, tickets = tickets, Airline = Airline, table = blank_chart)

# Finds the revenue made in the last 30 days and last year
@app.route('/revenue', methods=['GET', 'POST'])
def revenue():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))

	Airline = session['user'][1]
	cursor = conn.cursor()

	query = 'SELECT SUM(SoldPrice) FROM ticket WHERE AirlineName = %s AND DATEDIFF(CURRENT_DATE,PurchaseDate) < 30'
	cursor.execute(query, Airline)
	total_month = cursor.fetchall()
	total_month = total_month[0]['SUM(SoldPrice)']

	query = 'SELECT SUM(SoldPrice) FROM ticket WHERE AirlineName = %s AND DATEDIFF(CURRENT_DATE,PurchaseDate) < 365'
	cursor.execute(query, Airline)
	total_year = cursor.fetchall()
	total_year= total_year[0]['SUM(SoldPrice)']
	cursor.close()

	return render_template('staff_revenue.html', Year = total_year, Month = total_month, Airline = Airline)

# Finds the most popular desination in the last 3 months and year
@app.route('/destination', methods=['GET', 'POST'])
def destination():

	###Security Check
	if(session['user'][2] != 1):
		return redirect(url_for('staffLogin'))
		
	Airline = session['user'][1]
	cursor = conn.cursor()

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

	return render_template('staff_destinations.html', pop_year = popular_year, pop_month = popular_month, Airline = Airline)

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



####################### CustomerHome
@app.route('/customerhome')
def customerhome():
	username = session['user'][1]
	useremail = session['user'][0]

	cursor = conn.cursor();

	# limit flights display to user's purchased flights
	query = 'SELECT FlightNumber, DepartureDate, DepartureTime, AirlineName, Status FROM `flight`, `purchase` WHERE CustomerEmail = %s AND DepartureDate > CURRENT_DATE or (DepartureDate = CURRENT_DATE and DepartureTime > CURRENT_TIMESTAMP);'
	cursor.execute(query, (useremail,)) #Runs the query
	flight_data = cursor.fetchall() #Gets the data from ran SQL query

	#Tests
	for each in flight_data:   #prints out all the flights
		print(each['FlightNumber'],each['DepartureDate'], each['DepartureTime'])

	cursor.close()

	return render_template('CustomerHome.html', flights=flight_data, username = username)

####################### CustomerPastFlightsView
@app.route('/customerpastflightsview', methods=['GET', 'POST'])
def customerpastflightsview():
	useremail = session['user'][0]
	cursor = conn.cursor();

	# need to update to limit to purchased flights
	# need to take from purchase table instead of flights table
	query_past = 'SELECT FlightNumber, DepartureDate, DepartureTime, AirlineName, Status FROM `flight`, `purchase` WHERE CustomerEmail = %s AND DepartureDate < CURRENT_DATE or (DepartureDate = CURRENT_DATE and ArrivalTime < CURRENT_TIMESTAMP);'
	cursor.execute(query_past, (useremail,)) #Runs the query
	past_flight_data = cursor.fetchall()

	#Tests
	for each in past_flight_data:   #prints out all the flights
		print(each['FlightNumber'],each['DepartureDate'], each['DepartureTime'])

	cursor.close()

	return render_template('CustomerPastFlight.html', flights=past_flight_data)

####################### CustomerReview
@app.route('/customerreview', methods=['GET', 'POST'])
def customerreview():
	#CustomerEmail = request.form["CustomerEmail"]
	CustomerEmail = session['user'][0]
	#FlightNumber = request.form["FlightNumber"]
	FlightNumber = request.form["FlightNumber"]
	#DepartureDate = request.form["DepartureDate"]
	DepartureDate = request.form["DepartureDate"]
	#DepartureTime = request.form["DepartureTime"]
	DepartureTime = request.form["DepartureTime"]
	rate = request.form.get('rating')
	comment = request.form.get('comment')

	print(CustomerEmail)
	print(FlightNumber)
	print(DepartureDate)
	print(DepartureTime)


	if(rate == None and comment == None):
		print("in none")
		return render_template('CustomerReview.html', FlightNumber = FlightNumber, DepartureDate = DepartureDate, DepartureTime = DepartureTime)

	cursor = conn.cursor();
	#rate = request.form['rating']
	rate = request.form.get('rating')

	print(rate)
	#comment = request.form['comment']
	comment = request.form.get('comment')
	print(comment)
	query = 'UPDATE views SET Rate = %s, Comment = %s WHERE CustomerEmail = %s AND FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
	cursor.execute(query, (rate, comment, CustomerEmail, FlightNumber, DepartureDate, DepartureTime))
	conn.commit()
	cursor.close()
	
	return render_template('CustomerReview.html')

####################### CustomerSearchFlights
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
		query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName FROM (`flight` NATURAL JOIN `airplane`), `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate = %s AND NumSeats > 0'
		query2 = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName FROM (`flight` NATURAL JOIN `airplane`), `airport` AS d, `airport` AS a WHERE DepartAirportID = a.AirportID AND ArrivalAirportID = d.AirportID AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate = %s AND NumSeats > 0'
		cursor.execute(query, (departing, departing, arriving, arriving, departing_date)) #Runs the query
		depart_data = cursor.fetchall() #Gets the data from ran SQL query
		cursor.execute(query2, (arriving, arriving, departing, departing, arriving_date)) #Runs the query
		arriving_data = cursor.fetchall()

	else:    #Is the one way search
		query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName FROM (`flight` NATURAL JOIN `airplane`), `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate = %s AND NumSeats > 0'
		cursor.execute(query, (departing, departing, arriving, arriving, departing_date)) #Runs the query
		depart_data = cursor.fetchall() #Gets the data from ran SQL query
		for each in depart_data:   #prints out all the flights we have THIS IS A TEST
			print(each)

	cursor.close()
	return render_template('CustomerSearchFlights.html', depart_flights=depart_data, arrival_flights=arriving_data)


####################### CustomerSearchFlights -- One Way
@app.route('/customersearchflightsoneway', methods=['GET', 'POST'])
def customersearchflightsoneway():
	departing = request.form.get("Departing")
	departing_date = request.form.get("Departure Date")
	arriving = request.form.get("Arriving")

	if(departing == None and departing_date == None and arriving == None):
		return render_template('CustomerSearchFlightsOneWay.html')

	cursor = conn.cursor()

	#Checks if it should be 
	query = 'SELECT FlightNumber, d.AirportName, a.AirportName, NumSeats, BasePrice FROM `flight` AS f, `airplane` AS air , `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND f.AirplaneID = air.AirplaneID AND f.AirlineName = air.AirlineName AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate > CURRENT_DATE'
	cursor.execute(query, (departing, departing, arriving, arriving))
	check = cursor.fetchall()

	seats = []

	for each in check:
		#query = 'SELECT COUNT(TicketID) FROM ticket WHERE FlightNumber = %s'
		#cursor.execute(query, each['FlightNumber'])
		#data = cursor.fetchall()
		#seats.append(data['COUNT(TicketID'])
		print(each)

	query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, BasePrice FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate > CURRENT_DATE ORDER BY DepartureDate ASC, DepartureTime ASC'
	cursor.execute(query, (departing, departing, arriving, arriving))
	check = cursor.fetchall()
	#query = 'SELECT flight.FlightNumber, COUNT(TicketID) FROM flight, airport AS d, airport AS a, ticket WHERE ticket.FlightNumber = flight.FlightNumber AND DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate > CURRENT_DATE'
	#cursor.execute(query, (departing, departing, arriving, arriving))
	#depart_data = cursor.fetchall()

	#for each in depart_data:
	#	print(each)

	

	# one way search
	#queryOneWay = 'SELECT f.FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, plane.AirlineName, a.AirportName, d.AirportName, NumSeats, SoldPrice FROM `flight` AS f, `airplane` AS plane, `ticket`, `airport` AS d, `airport` AS a WHERE DepartAirportID = a.AirportID AND ArrivalAirportID = d.AirportID AND f.`AirplaneID` = plane.`AirplaneID` AND f.`AirlineName` = plane.`AirlineName`AND f.`FlightNumber` = `ticket`.`FlightNumber` AND f.`AirlineName` = `ticket`.`AirlineName`AND plane.`AirlineName` =`ticket`.`AirlineName` AND NumSeats > 0 AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate = %s;'

	#queryOneWay = 'SELECT f.FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, f.AirlineName, d.AirportName, a.AirportName, SoldPrice FROM `flight` AS f, `airplane` AS p, `ticket` as t, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND f.AirplaneID = p.AirplaneID AND p.AirlineName = t.AirlineName AND NumSeats > 0 AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate = %s ORDER BY DepartureDate ASC, DepartureTime ASC;'
	#queryOneWay = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, SoldPrice FROM `flight`, `ticket` as t, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND p.AirlineName = t.AirlineName AND NumSeats > 0 AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate = %s ORDER BY DepartureDate ASC, DepartureTime ASC;'
	#cursor.execute(queryOneWay, (departing, departing, arriving, arriving, departing_date))
	#depart_data = cursor.fetchall()
	#for each in depart_data:
	#	print(each)

	cursor.close()
	return render_template('CustomerSearchFlightsOneWay.html', depart_flights=check)


####################### CustomerSearchFlights -- Two Way
@app.route('/customersearchflightstwoway', methods=['GET', 'POST'])
def customersearchflightstwoway():
	departing = request.form.get("Departing")
	departing_date = request.form.get("Departure Date")
	arriving = request.form.get("Arriving")
	arriving_date = request.form.get("Arriving Date")

	if(departing == None and departing_date == None and arriving == None and arriving_date == None):
		return render_template('CustomerSearchFlightsTwoWay.html')

	cursor = conn.cursor()

	print(departing)
	print(departing_date)
	print(arriving)
	print(arriving_date)

	query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, BasePrice FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = d.AirportID AND ArrivalAirportID = a.AirportID AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate > CURRENT_DATE ORDER BY DepartureDate ASC, DepartureTime ASC'
	cursor.execute(query, (departing, departing, arriving, arriving))
	departing_flight = cursor.fetchall()

	query = 'SELECT FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, AirlineName, d.AirportName, a.AirportName, BasePrice FROM `flight`, `airport` AS d, `airport` AS a WHERE DepartAirportID = a.AirportID AND ArrivalAirportID = d.AirportID AND (d.AirportName = %s or d.City = %s) AND (a.AirportName = %s or a.City = %s) AND DepartureDate > CURRENT_DATE ORDER BY DepartureDate ASC, DepartureTime ASC'
	cursor.execute(query, (departing, departing, arriving, arriving))
	arriving_flight = cursor.fetchall()

	cursor.close()
	return render_template('CustomerSearchFlightsTwoWay.html', depart_flights = departing_flight, arrival_flights = arriving_flight)

@app.route('/ticketprice', methods=['GET', 'POST'])
def ticketprice():
	print("in Ticketprice")
	FlightNumber = request.form["FlightNumber"]
	Airline = request.form["AirlineName"]
	BasePrice = request.form["BasePrice"]
	
	cursor = conn.cursor()

	query = 'SELECT COUNT(TicketID) as tickets FROM ticket WHERE FlightNumber = %s AND AirlineName = %s'
	cursor.execute(query, (FlightNumber, Airline))
	seats = cursor.fetchall()
	seats_taken = seats[0]['tickets']

	print(seats_taken)

	query = 'SELECT NumSeats FROM flight NATURAL JOIN airplane WHERE FlightNumber = %s AND AirlineName = %s'
	cursor.execute(query, (FlightNumber, Airline))
	seats = cursor.fetchall()
	seats = seats[0]['NumSeats']

	print("Total seats: " + str(seats))
	print(seats * .75)

	if seats_taken > int(seats * .75):
		BasePrice = float(BasePrice) * 1.25

	return render_template('TicketPrice.html', FlightNumber = FlightNumber, Airline = Airline, Price = BasePrice)

@app.route('/ticketprice2', methods=['GET', 'POST'])
def ticketprice2():
	print("in Ticketprice2")

	depart_flight = request.form["departflight"]
	Arr_flight = request.form["arrflight"]
	
	cursor = conn.cursor()

	print(depart_flight.split(","))
	print(Arr_flight)

	query = 'SELECT COUNT(TicketID) as tickets FROM ticket WHERE FlightNumber = %s AND AirlineName = %s'
	cursor.execute(query, (dep_FlightNumber, dep_Airline))
	seats = cursor.fetchall()
	seats_taken = seats[0]['tickets']

	print(seats_taken)

	query = 'SELECT NumSeats FROM flight NATURAL JOIN airplane WHERE FlightNumber = %s AND AirlineName = %s'
	cursor.execute(query, (dep_FlightNumber, dep_Airline))
	seats = cursor.fetchall()
	seats = seats[0]['NumSeats']

	print("Total seats: " + str(seats))
	print(seats * .75)

	if seats_taken > int(seats * .75):
		dep_BasePrice = float(dep_BasePrice) * 1.25

	return render_template('TicketPrice.html')

@app.route('/customerinputcard', methods=['GET', 'POST'])
def customerinputcard():
	print("in customerinputcard")
	FlightNumber = request.form["FlightNumber"]
	Airline = request.form["Airline"]
	Price = request.form["Price"]

	return render_template('CustomerPaymentInput.html', FlightNumber = FlightNumber, Airline = Airline, Price = Price)


####################### CustomerPurchase
@app.route('/customerpurchase', methods=['GET', 'POST'])
def customerpurchase():
	CustomerEmail = session['user'][0]
	CardType = request.form["CardType"]
	CardNumber = request.form["CardNumber"]
	NameOfCard = request.form["NameOfCard"]
	ExpirationDate = request.form["ExpirationDate"]
	FlightNumber = request.form["FlightNumber"]
	Airline = request.form["Airline"]
	Price = request.form["Price"]

	cursor = conn.cursor()

	query = 'SELECT CURRENT_DATE as date WHERE CURRENT_DATE < %s;'
	cursor.execute(query, ExpirationDate) # need this format or else, will crash
	check = cursor.fetchall()

	if(check == ()):
		return redirect(url_for('customerinputcard'))

	# update ticket to have customerEmail
	# take ticketID from ticket and insert into purchase
	# insert basic data into views
	'''
	SQL to get all tickets from 'tickets'
	randnum = pythonRandNumGenerator
	existTickets = query.getall
	for i in existTickets
	if randnum == i.ticketID
    	randnum = randPythonFunc
    else
    	insertQuery = INSERT INTO.........
	'''
	
	#randomNum = random.randrange(1, 100000000) # max num is 99999999
	
	#allTickets = 'SELECT * FROM `ticket`'
	queryAllTicketID = 'SELECT TicketID FROM `ticket` ORDER BY TicketID ASC;'
	cursor.execute(queryAllTicketID)
	allTicketID_data = cursor.fetchall()

	'''
	isSame = False

	# change to While loop?
	# logic wrong
	for id in allTicketID_data:

		if(randomNum == id[0]): # id[0] is the TicketID
			isSame = True
		
		# if randomNum already exists as ticketNum, 
		if(isSame == True):
			randomNum = random.randrange(1, 100000000)
	'''
	

	# if we abandon the randomNum idea and have the tickets be assigned in consecutive nums
	counter = 0
	for id in allTicketID_data:
		counter += 1
	
	lastTicketID = allTicketID_data[counter - 1]['TicketID'] #gets the ticketID of the last ticket
	newTicketID = int(lastTicketID) + 1
	
	#print("Insert into")
	#queryInsertPurchase = 'INSERT INTO purchase VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, CURRENT_TIME)'
	#cursor.execute(queryInsertPurchase, (newTicketID, FlightNumber, Airline, CustomerEmail, Price))

	queryInsertPurchase = 'INSERT INTO ticket VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, CURRENT_TIME)'
	cursor.execute(queryInsertPurchase, (newTicketID, FlightNumber, Airline, CustomerEmail, Price))

	# inserting Purchase
	queryInsertPurchase = 'INSERT INTO purchase VALUES (%s, %s, %s, %s, %s, %s)'
	cursor.execute(queryInsertPurchase, (newTicketID, CustomerEmail, CardType, CardNumber, NameOfCard, ExpirationDate))


	# inserting Ticket
	#queryCurrDate = 'SELECT CURRENT_DATE();'
	#cursor.execute(queryCurrDate)
	#currDate_data = cursor.fetchall()

	#queryCurrTime = 'SELECT CURRENT_TIME();'
	#cursor.execute(queryCurrTime)
	#currTime_data = cursor.fetchall()
		

	# inserting Views, set up for Review -- NEED TO TEST
	# finding departure date and time
	queryDepartureDate = 'SELECT DepartureDate FROM `flight` WHERE FlightNumber = %s AND AirlineName = %s;'
	cursor.execute(queryDepartureDate, (FlightNumber, Airline))
	departing_date = cursor.fetchall()
	departing_date = departing_date[0]['DepartureDate']
	
	queryDepartureTime = 'SELECT DepartureTime FROM `flight` WHERE FlightNumber = %s And AirlineName = %s;'
	cursor.execute(queryDepartureTime,(FlightNumber, Airline))
	departing_time = cursor.fetchall()
	departing_time = departing_time[0]['DepartureTime']

	queryInsertViews = 'INSERT INTO views VALUES (%s, %s, %s, %s, NULL, NULL)'
	cursor.execute(queryInsertViews, (CustomerEmail, FlightNumber, departing_date, departing_time))

	conn.commit()
	cursor.close()

	return redirect(url_for('customersearchflightsoneway'))


####################### CustomerPurchaseResult
@app.route('/customerpurchaseresult', methods=['GET', 'POST'])
def customerpurchaseresult():
	return render_template('CustomerPurchaseResult.html')

####################
@app.route('/customertrackspending', methods=['GET', 'POST'])
def customertrackspending():
	cursor = conn.cursor();
	user = session['user'][0]
	# print(user)
	query = 'SELECT SUM(SoldPrice) FROM ticket NATURAL JOIN customer WHERE CustomerEmail = %s AND YEAR(PurchaseDate) = YEAR(now());'
	cursor.execute(query, user)
	total_spent = cursor.fetchall()
	# print("HERE: ", total_spent[0])
	# print(total_spent[0]['SUM(SoldPrice)'])
	if total_spent[0]['SUM(SoldPrice)'] == None:
		total_spent = 0
	else:
		total_spent = total_spent[0]['SUM(SoldPrice)']

	query2 = 'SELECT MONTH(PurchaseDate), SUM(SoldPrice) FROM ticket NATURAL JOIN customer WHERE PurchaseDate > DATE_SUB(now(), INTERVAL 6 MONTH) AND CustomerEmail = %s GROUP BY MONTH(PurchaseDate)'
	cursor.execute(query2, user)
	money_spent = cursor.fetchall()
	s_date = request.form.get("startDate") 
	e_date = request.form.get("endDate")

	conn.commit()
	cursor.close()

	return render_template('customertrackspending.html', total_spent = total_spent, six_months = money_spent)



@app.route('/customer_tracking_range', methods=['GET', 'POST'])
def customer_tracking_range():
	user = session['user'][0]
	s_date = request.form.get("startDate") 
	e_date = request.form.get("endDate")

	cursor = conn.cursor()

	# print(user)
	query = 'SELECT SUM(SoldPrice) FROM ticket NATURAL JOIN customer WHERE CustomerEmail = %s AND YEAR(PurchaseDate) = YEAR(now());'
	cursor.execute(query, user)
	total_spent = cursor.fetchall()
	# print("HERE: ", total_spent[0])
	# print(total_spent[0]['SUM(SoldPrice)'])
	if total_spent[0]['SUM(SoldPrice)'] == None:
		total_spent = 0
	else:
		total_spent = total_spent[0]['SUM(SoldPrice)']

	query2 = 'SELECT MONTH(PurchaseDate), SUM(SoldPrice) FROM ticket NATURAL JOIN customer WHERE PurchaseDate > DATE_SUB(now(), INTERVAL 6 MONTH) AND CustomerEmail = %s GROUP BY MONTH(PurchaseDate)'
	cursor.execute(query2, user)
	money_spent = cursor.fetchall()
	s_date = request.form.get("startDate") 
	e_date = request.form.get("endDate")

	query3 = 'SELECT SUM(SoldPrice) FROM ticket NATURAL JOIN customer WHERE CustomerEmail = %s AND PurchaseDate >= %s AND PurchaseDate <= %s';
	cursor.execute(query3, (user, s_date, e_date))
	specific_spent = cursor.fetchall()
	if specific_spent[0]['SUM(SoldPrice)'] == None:
		specific_spent = 0
	else:
		specific_spent = specific_spent[0]['SUM(SoldPrice)']

	return render_template('customertrackspending.html', total_spent = total_spent, six_months = money_spent, specify = specific_spent)

	

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
	session['user'] = [None, 'Guest', -1]
	return redirect('/loginfork')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 3306, debug = True)