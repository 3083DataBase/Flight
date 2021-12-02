CREATE TABLE Customer(
        CustomerEmail varchar(100),
        Password varchar(300) NOT NULL,
        CustomerName varchar(100) NOT NULL,
        BuildingNumber bigint NOT NULL,
        Street varchar(50) NOT NULL,
        City varchar(50) NOT NULL,
        State varchar(50) NOT NULL,
        PhoneNumber bigint NOT NULL,
        PassportNumber varchar(10) NOT NULL,
        PassportExpiration date NOT NULL,
        PassportCountry varchar(50) NOT NULL,
        DateOfBirth date NOT NULL,

        PRIMARY KEY (CustomerEmail)
);

CREATE TABLE Airport(
    AirportID varchar(100),
    AirportName varchar(100) NOT NULL,
    City varchar(100) NOT NULL,

    PRIMARY KEY (AirportID)
);

CREATE TABLE Airline(
    AirlineName varchar(100),

    PRIMARY KEY (AirlineName)
);

CREATE TABLE AirlineStaff (
    StaffUsername varchar(100),
    Password varchar(300) NOT NULL,
    FirstName varchar(50) NOT NULL,
    LastName varchar(50) NOT NULL,
    DateOfBirth date NOT NULL,
    AirlineName varchar(100) NOT NULL,

    PRIMARY KEY (StaffUsername),
    FOREIGN KEY (AirlineName) references Airline(AirlineName)
);




CREATE TABLE PhoneNumber (
StaffUsername varchar(100),
StaffPhoneNum bigint NOT NULL,

PRIMARY KEY (StaffUsername, StaffPhoneNum),
FOREIGN KEY (StaffUsername) references AirlineStaff(StaffUsername)
);




CREATE TABLE WorksFor (
    StaffUsername varchar(100),
    AirlineName varchar(100) NOT NULL,

    PRIMARY KEY (StaffUsername),
    FOREIGN KEY (StaffUsername) references AirlineStaff(StaffUsername),
    FOREIGN KEY (AirlineName) references Airline(AirlineName)
);




CREATE TABLE Airplane (
    AirplaneID varchar(100),
    AirlineName varchar(100) NOT NULL,
    NumSeats bigint NOT NULL,

    PRIMARY KEY (AirplaneID, AirlineName),
    FOREIGN KEY (AirlineName) references Airline(AirlineName)
);




CREATE TABLE Flight (
    FlightNumber bigint,
    DepartureDate date,
    DepartureTime time,
    AirlineName varchar(100) NOT NULL,
    ArrivalDate date NOT NULL,
    ArrivalTime time NOT NULL,
    BasePrice float (10, 2) NOT NULL,
    Status varchar(100) NOT NULL,
    AirplaneID varchar(100) NOT NULL,
    DepartAirportID varchar(100) NOT NULL,
    ArrivalAirportID varchar(100) NOT NULL,

    PRIMARY KEY (FlightNumber, DepartureDate, DepartureTime),
    FOREIGN KEY (AirlineName) references Airline(AirlineName),
    FOREIGN KEY (AirplaneID) references Airplane(AirplaneID),
    FOREIGN KEY (DepartAirportID) references Airport(AirportID),
    FOREIGN KEY (ArrivalAirportID) references Airport(AirportID),
    UNIQUE(FlightNumber, DepartureDate, DepartureTime)
);


CREATE TABLE Depart (
    FlightNumber bigint,
    DepartureDate date,
    DepartureTime time,
    AirportID varchar(100),

    PRIMARY KEY (FlightNumber, DepartureDate, DepartureTime, AirportID),
    FOREIGN KEY (AirportID) references Airport(AirportID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (FlightNumber, DepartureDate, DepartureTime) references Flight(FlightNumber, DepartureDate, DepartureTime)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE Arrive (
    FlightNumber bigint,
    DepartureDate date,
    DepartureTime time,
    AirportID varchar(100),

    PRIMARY KEY (FlightNumber, DepartureDate, DepartureTime),
    FOREIGN KEY (AirportID) references Airport(AirportID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (FlightNumber, DepartureDate, DepartureTime) references Flight(FlightNumber, DepartureDate, DepartureTime)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE views (
    CustomerEmail varchar(100),
    FlightNumber bigint,
    DepartureDate date,
    DepartureTime time,
    Rate float(2,1),
    Comment varchar(2000),

    PRIMARY KEY ( CustomerEmail, FlightNumber, DepartureDate, DepartureTime),
    FOREIGN KEY (CustomerEmail) References Customer(CustomerEmail),
    FOREIGN KEY (FlightNumber, DepartureDate, DepartureTime) references Flight(FlightNumber, DepartureDate, DepartureTime)
);


CREATE TABLE Ticket (
    TicketID varchar(100),
    FlightNumber bigint NOT NULL,
    AirlineName varchar(100) NOT NULL,
    CustomerEmail varchar(100) NOT NULL,
    SoldPrice float NOT NULL,
    PurchaseDate date NOT NULL,
    PurchaseTime time NOT NULL,

    PRIMARY KEY (TicketID),
    FOREIGN KEY (CustomerEmail) references Customer(CustomerEmail),
    FOREIGN KEY (FlightNumber) references Flight(FlightNumber),
    FOREIGN KEY (AirlineName) references Airline(AirlineName)
);

CREATE TABLE Purchase (
    TicketID varchar(100),
    CustomerEmail varchar(100),
    CardType varchar(20) NOT NULL,
    CardNumber bigint NOT NULL,
    NameOfCard varchar(100) NOT NULL,
    ExpirationDate date NOT NULL,

    PRIMARY KEY (TicketID, CustomerEmail),
    FOREIGN KEY (TicketID) references Ticket(TicketID),
    FOREIGN KEY (CustomerEmail) references Customer(CustomerEmail)
);
