INSERT INTO airline VALUES('China Eastern'), ('Korean Air'), ('American Airlines'), ('United Airlines');

INSERT INTO airport VALUES('001', 'JFK', 'NYC'), ('002', 'PVG', 'Shanghai');

INSERT INTO Customer VALUES('my1590@nyu.edu', 'passw0rd', 'Michelle Yang', '80', 'Lafayette St', 'New York City', 'NY', '8888888888', '5550000303', '2023-09-30', 'United States of America', '2000-09-26'), ('kp2327@nyu.edu', 'kattrippassword', 'Kathy Pan', '370', 'Jay St', 'Brooklyn', 'NY', '7185558888', '7561643301', '2027-12-25', 'United States of America', '2000-08-25'), ('kei231@nyu.edu', 'passw0rd1234', 'Kevin Iza', '5', 'MetroTech', 'New York City', 'NY', '8811882288', '5398248312', '2024-09-30', 'United States of America', '2000-09-30');

INSERT INTO airplane VALUES('001', 'Korean Air', '1069'), ('002', 'American Airlines', '2000'), ('003', 'United Airlines', '2122'), ('001', 'China Eastern', '4206');

INSERT INTO airlinestaff VALUES('MisterBrightside', md5('pw12345*'), 'Brightside', 'Jones', '1982-08-10', 'China Eastern'), ('SoulRider',  md5('LaCroix33'), 'Soul', 'Smith', '1995-07-04', 'China Eastern'), ('YugiMuto',  md5('endGamers!'), 'Yugi', 'Muto', '1980-05-04', 'China Eastern');

INSERT INTO phonenumber VALUES('MisterBrightside', '2123336565'), ('SoulRider', '6465559949'), ('YugiMuto', '3326668899');

INSERT INTO flight VALUES ('00684', '2021-11-11', '10:23:00', 'China Eastern', '2021-11-12', '1:30:00', '800.00', 'on-time', '001', '001','002'), ('09231', '2021-11-24', '09:10:00', 'China Eastern', '2021-11-25', '12:10:00', '300.00', 'delayed', '002','002','001'), ('00732', '2021-11-25', '02:48:00', 'China Eastern', '2021-11-26', '14:30:00', '1200.00', 'on-time', '003','001','002');

INSERT INTO ticket VALUES ('42012', '00684', 'China Eastern', 'my1590@nyu.edu', '800.00', '2021-09-01', '01:12:23'), ('22121', '09231', 'China Eastern', 'kp2327@nyu.edu', '300.00', '2021-10-20', '05:10:30'), ('55437', '00732', 'China Eastern', 'kei231@nyu.edu', '1200.00', '2021-01-24', '06:46:12');

INSERT INTO purchase VALUES ('42012', 'my1590@nyu.edu', 'debit', '5534 2232 1211 2322', 'Visa', '2025-07-01'), ('22121', 'kp2327@nyu.edu', 'credit', '5592 2323 5675 2121', 'Amex', '2026-08-12'), ('55437', 'kei231@nyu.edu', 'debit', '8838 2254 2124 0989', 'Mastercard', '2024-12-01');




INSERT INTO flight VALUES ('99000', '2021-12-11', '10:23:00', 'Korean Air', '2021-12-12', '1:30:00', '803.00', 'on-time', '001', '001', '002'), ('99001', '2021-12-24', '09:10:00', 'China Eastern', '2021-12-25', '12:10:00', '303.00', 'delayed', '001', '001', '002'), ('99002', '2021-12-25', '02:48:00', 'American Airlines', '2021-12-26', '14:30:00', '1203.00', 'on-time', '002', '002', '001');