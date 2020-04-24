import sqlite3
import time
import sys
from getpass import getpass
import re
#from datetime import datetime, date
import datetime
import random

# python Municipal_proj.py mp1.db

connection = None
cursor = None


def connect(path):
	#connect to the database specified by path, code taken from lab example slides
	global connection, cursor

	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute(" PRAGMA foreign_keys=ON; ")
	connection.commit()
	return
	
def logon():
	#have the user type their username and pasword to logon or quit 
	global connection, cursor
	
	userID = input("Enter Your User ID: ")
	#give a way for users to leave the infinite logon loop
	if(re.search("quit", userID, re.IGNORECASE)):
		print("Have a good day.")
		return False, 'q'
		
	#working with the userID and pswrd combo in python instead of sql prevents injections
	cursor.execute("SELECT uid, pwd, fname, utype FROM users WHERE uid=" + userID + ";")
	#should only ever be one result, since uid is a key, also prevents injection of userID
	combo = cursor.fetchone()
	
	#if sql query returned nothing, that userID is not in the database
	while combo == None:
		print("No such User ID exists. Please try again, or type quit to exit.")
		userID = input("Enter Your User ID: ")
		cursor.execute("SELECT uid, pwd, fname, utype FROM users WHERE uid=" + userID + ";")
		combo = cursor.fetchone()
	pwd = getpass("Enter Your Password: ")
	#why we pull pwd out of sql: so you can't do "pwd='test' OR 1=1" injection
	
	while (pwd != combo[1]):
		print("User ID and Password combination do not match. Please try again, or type quit to exit.")
		userID = input("Enter Your User ID: ")
		cursor.execute("SELECT uid, pwd, fname, utype FROM users WHERE uid=" + userID + ";")
		combo = cursor.fetchone()
		pwd = getpass("Enter Your Password: ")
	if (pwd == combo[1]):
		print("Logon Successful. Welcome back, " + combo[2])
		return True, combo[3], combo[0]

def get_gender():
	# This function checks if user input the right gender
	
	while True:
		gender = input("gender (M/F) : ")
		if gender.upper() == 'F' or gender.upper() == 'M':
			break
		else:
			print("Invalid input for gender.")
			print("Enter M for Male or F for Female.")
			continue
			
	return gender.upper()

def add_null (i):
	# adds NULL if user did not input anything
	
	u_input = i
	
	if u_input == ' ':
		u_input = "NULL"
		
	return u_input

def get_name():
	
	# make sure user enters a value for name
	
	while True:
		first = input("  >> first name: ")
		last = input("  >> last name: ")
		if first == ' ' or last == ' ':		#if empty
			print("Invalid input. Can't leave name blank. Please try again!")
			continue
		else:
			break
	
	
	return first, last
  
def reg_person(fname, lname, x):
	
	global connection, cursor
	#register a person if it does not exist in database
	check = True
	name = (fname, lname)
	
	while check == True:
		# check if person is in database
		cursor.execute('SELECT fname, lname FROM persons WHERE fname like ? AND lname like ?;', name)
		f_exist = cursor.fetchone()
		
		#if not in database, register
		
		if f_exist == None:
			print("Person's information is not in database.\n")
			print("Register Person's information in database. Enter the following information:")
		
			fname, lname = get_name()			   #get the name of person
		
			place = input("Place of birth: ")	   #p.o.b
			bplace = add_null(place)				#add NULL if input is empty
			
			addr = input ("current address: ")	  #address
			address = add_null(addr)
			
			p_num = input("phone number [000-000-0000]: ")
			phone = add_null(p_num)
			
			bday = check_date(datetime.date.today())	#check date validity
			bdate = add_null(bday)
			
			# register / insert person info into persons table
			
			person = (fname, lname, bdate, bplace, address, phone)
			cursor.execute('INSERT INTO persons VALUES (?,?,?,?,?,?);', person)

			name = (fname, lname)
			
			# check if successful
			cursor.execute('SELECT fname, lname FROM persons WHERE fname like ? AND lname like ?;', name)
			# line above
			pFetch = cursor.fetchone()
			
			if pFetch != None:
				print("Person registered!")	
				time.sleep(1)
				if x == 1:
					print("Resume birth registration ... ")
					time.sleep(1)
				else:
					print("Resume marriage registration ... ")
					time.sleep(1)
			break	
		else:
			#if it already exists in database, return True
			
			check == False
			return True	

def reg_birth(uid):
	global connection, cursor
	#needs user id logon.userid ??

	#persons(fname, lname, bdate, bplace, address, phone)
	#users(uid, pwd, utype, fname, lname, city)
	#births(regno, fname, lname, regdate, regplace, gender, f_fname, f_lname, m_fname, m_lname)
	'''
	The information is obtained and recorded in persons and births tables
	The registration date and place are correctly set **
	A unique registration number is assigned to the birth record
	The address and phone for the newborn is correctly set
	The parents are recorded in persons table (if not there already)
	'''
	userid = (uid,)
	print("To register a birth, please enter the following information, following the format in brackets: ")
	#child's informations

	#child's name:
	fname, lname = get_name()
 
	#check if name is already registered  
	cursor.execute('SELECT fname, lname FROM persons WHERE fname like ? AND lname like ?;', (fname, lname))
	f_exist = cursor.fetchone()	

	#if YES: cannot continue registration
	x = 1 # redirect the registration for "Persons" into registration for births

	if f_exist != None:
		print("Error. Name already exists.")
		print("Registration failed.")

	#if not: continue registration
	else:
		
	#get gender (check validity)
		gender = get_gender()

	#get place of birth
		bplace = input("place of birth: ")
		
	#get register place == city of user
		cursor.execute('SELECT city FROM users WHERE uid = ?;', userid)
		regplace = cursor.fetchone()
		
	#regdate = current date
		regdate = datetime.date.today()
		
	#generate random regno.. if regno already exists, keep generating
		#random number until you get one that is not used
	

		while True:
			regnum = random.randint(100, 998)
			regno = (regnum, )
			cursor.execute('SELECT * FROM births WHERE regno = ?;', regno)
			exists = cursor.fetchone()
			if exists == None:
				break
			else:
				continue
	
	#parent's information

	#get father's first name
		print("Enter Father's name. ")
		f_fname, f_lname = get_name()
		reg_person(f_fname, f_lname, x)	#check if father exists in record
	
	#get mother's first name
		print("Enter Mother's name. ")
		m_fname, m_lname = get_name()
		m_exists = reg_person(m_fname, m_lname, x) #check if mother exists in record
		
	# check if mother is registered in person
	# if yes, get her phone and address --> set to child's record
		if m_exists:
			cursor.execute('SELECT phone, address FROM persons WHERE fname like ? AND lname like ?;', (m_fname, m_lname))
			result = cursor.fetchone()
			phone = result[0]
			address = result[1]
		
	#check if birthdate input is valid
		bdate = check_date(regdate)
		
		person = (fname,lname, bdate, bplace, address, phone)
		birth = (regno[0], fname, lname, regdate, regplace[0], gender, f_fname, f_lname, m_fname, m_lname)

	# also add child into persons table
		cursor.execute('INSERT INTO persons VALUES (?,?,?,?,?,?);', person)
 
	# insert registration details in registrations table

		cursor.execute('INSERT INTO births VALUES (?,?,?,?,?,?,?,?,?,?);', birth)
		cursor.execute('SELECT fname, lname FROM births WHERE fname like ? AND lname like ?;',  (fname, lname))
		bFetch = cursor.fetchone()

	#check if successful:		
		if bFetch != None:
			print("Registration successful!")

		cursor.execute('SELECT fname, lname FROM persons WHERE fname like ? AND lname like ?;', (fname, lname))
		pFetch = cursor.fetchone()
		
	# check if successful		
		if pFetch != None:
			print("Registration successful. Goodbye.")
			#time.sleep(1)
		connection.commit()

	return

def reg_marriage(uid):
	'''
	Register a marriage
	The information is ontained and recorded in the marriages table
	The registration date and place are correctly set
	A unique registration number is assigned 
	If a partner is not in persons table, the information is obtained and recorded in persons table 
	Any field that is not provided is set to null
	'''
	#marriages (regno, regdate, regplace, p1_fname, p1_lname, p2_fname, p2_lname)
	
	# redirect the registration for "Persons" into registration for "marriage"
	x = 0

	userid = (uid, )
	print("To register a marriage,enter the following informations.")

	print("Enter the informations of Partner 1.")
	p1_first, p1_last = get_name()
	reg_person(p1_first, p1_last, x)
	#reg_person(p1_first, p1_last,0)

	print("Enter the informations of Partner 2.")
	p2_first, p2_last = get_name()	
	reg_person(p2_first, p2_last, x)
	#reg_person(p2_first, p2_last,0)
	
	while True:
		regnum = random.randint(100, 999)   #generate a random num bet 100-999
		regno = (regnum, )
		
		cursor.execute('SELECT * FROM marriages WHERE regno = ?;', regno)   #check if random generated num in marriages
		exists = cursor.fetchone()
		
		if exists == None:  #if regno not in marriages, break out of loop
			break
		else:			   #if regno exists, generate another number
			continue
	
	regdate = datetime.date.today() #YYYY-MM-DD

	cursor.execute('SELECT city FROM users WHERE uid = ?', userid)
	regplace = cursor.fetchone()	#regplace is the city of user
	
	#tuple for marriages input values	
	marriage = (regno[0], regdate, regplace[0], p1_first, p1_last, p2_first, p2_last)
	cursor.execute('INSERT INTO marriages VALUES (?,?,?,?,?,?,?);', marriage)
	
	#check if insert successful:
	cursor.execute('SELECT * FROM marriages WHERE regno = ?;', regno)
	success = cursor.fetchone()
	
	if success != None:
		print("Marriage successfully registered!")
		#time.sleep(1)
		#print("Please enter another command, or enter quit to exit.")

	connection.commit()
	return

def check_date(current):
	
	today = str(current)
	while True:
		try:
			d = input("Birth of date [YYYY-MM-DD]: ")
			date = datetime.date(*map(int, d.split('-')))
			
		except:
			print("Invalid date input!")
			print("Make sure to follow given format and enter a valid date")
		
		else:
			if (d > today):
				print("Error. Please input date in the past.")
				continue
			else:
				break
	
	return d

def renew_vreg():
	'''
	Renew a vehicle registration
	The registration record is correctly updated
	The expiry date is correctly set
	'''
	#vehicles(vin,make,model,year,color)
	#registrations(regno, regdate, expiry, plate, vin, fname, lname)	

	print("To renew your vehicle registration,")
	
	while True:
		r_num = input("Please enter your vehicle registration number: ")
		regno = (r_num, )
		cursor.execute('SELECT * FROM registrations WHERE regno = ?;', regno)
		exists = cursor.fetchone()
		if exists == None:
			print("Registration number not matched!")
			again = input("Try again (y/n)? ")
			
			if again.lower() == 'y':
				continue
			else:
				return
				
		else:
			cDate = datetime.date.today()			#current date
			cursor.execute('SELECT expiry FROM registrations WHERE regno = ?;', regno)
			eDate = cursor.fetchone()							   #expiry date
			
			curr = str(cDate)
			exp = str(eDate[0])
			
			if curr >= exp:		 # vehicle is expired
				new_exp = datetime.date(cDate.year +1, cDate.month, cDate.day)
				break
			else:
				exp_date = datetime.date(*map(int, exp.split('-')))
				new_exp = datetime.date(exp_date.year + 1, exp_date.month, exp_date.day)
				break

	renew = (new_exp, regno[0])
	cursor.execute('UPDATE registrations SET expiry = ? WHERE regno=?;', renew)

	cursor.execute('SELECT * FROM registrations WHERE expiry = ? AND regno = ?;', renew)
	rFetch = cursor.fetchone()
	
	if rFetch != None:
		print("Your car registration has been renewed!")
		time.sleep(1)
		print("Your registration expired or will expire on: " + exp)
		print("The new expiration date is: " + str(new_exp) + ". Thank you!")
		time.sleep(1)
	#break?

	return

def process_bill():

	global connection, cursor

	# Break the loop if pre-req is fulfilled, can proceed to register new owner
	while(True):
		print("Please enter information required to process a bill of sale as prompted.")

		vin = input("Vin:")
		o_fname = input("Current owner's first name: ")
		o_lname = input("Current owner's last name: ")
		n_fname = input("New owner's first name: ")
		n_lname = input("New owner's last name: ")
		plate = input("The plate number for the new registration: ")

		# Check if the new owner entered is in the system
		cursor.execute('''SELECT fname, lname FROM persons WHERE fname like ? AND lname like ?;''', (n_fname, n_lname))
		exist_names = cursor.fetchone()
		if exist_names == None:
			yn1 = input("The new owner's name is not in the system, transfer can't be made, process another bill of sale? y/n \n")
			if yn1 == 'y':
				continue
			else:
				return
		
		else: 
			#check if the name of the current owner match the name of the most recent owner of the car
			today = datetime.date.today()	
			vin_in = (vin, )
			cursor.execute('''SELECT fname, lname, expiry FROM registrations WHERE vin= ? ORDER BY expiry DESC LIMIT 1;''', vin_in)
			result = cursor.fetchone()
			#fname = result[0]
			#lname = result[1]

			if result == None:
				print("The car with vin ", vin, " has no owner, it has never been registered. Registering the new owner now...")
				break
			elif result[0] != o_fname or result[1] != o_lname:
				yn = input("Sorry, invalid owner name or vin, transfer can not be made, process another bill of sale? y/n \n")
				if yn == 'y':
					continue
				else:
					return
			else:
				print("Registering the new owner now...")
				break

	today = datetime.date.today()
	
	#update expiry date of current registration
	eandv = (today, vin)
	cursor.execute('''UPDATE registrations SET expiry=? WHERE vin=?;''', eandv)
	
	#new registration
	regdate = datetime.date.today()
	expiry = datetime.date(today.year + 1, today.month, today.day)
	fname = n_fname
	lname = n_lname
	
	#system generate a regno - find the max regno and plus one every time
	cursor.execute('''SELECT regno FROM registrations WHERE regno = (SELECT max(regno) FROM registrations);''')
	max_regno = cursor.fetchone()[0]
	regno = max_regno + 1

	cursor.execute("INSERT INTO registrations VALUES(" + str(regno) + ", " + str(regdate) + ", " + str(expiry) + ", '" + plate + "', '" + vin + "', '" + fname + "', '" + lname + "');")
	# cursor.execute("INSERT INTO registrations VALUES (regno, regdate, expiry, plate, vin, fname, lname);")
	connection.commit()
	return

def process_payment():
	
	global cursor, connection

	while(True):
		print("Please enter the ticket number and amount of payment as prompted below")
		tno = input("Ticket number: ")
		while not(tno.isdigit()):
			tno = input("Please make sure Ticket number is digit only: ")


		# type string converted to float type
		amount = input("Amount of payment: ")
		while not(amount.replace('.','1').isdigit()):
			amount = input("Please make sure amount of payment is integer or float: ")
		amount = float(amount)

		data = (tno, )
		# check if the tno already has some amount paid
		cursor.execute('''SELECT p.amount, t.fine FROM tickets AS t LEFT OUTER JOIN payments AS p
							USING(tno) WHERE t.tno = ?;''', data)
		record = cursor.fetchone()
		paid = 0.0
		remain = 0.0

		if record == None:
			yn = input("Ticket number is not in they system, payment can't be made, would you like to enter again?")
			if yn == 'y' or yn == 'Y':
				continue
			else:
				return 
		#no prior payments
		elif isinstance(record[0], type(None)):
			fine = record[1]
			# Exact, no more needed
			if amount == fine:
				print("Ticket paid in full with current payment, thank you.")
			
			# More payments to go
			elif amount < fine:
				print("Payment accepted, $", fine - amount, "left to be paid next time.")
			
			# Paid too much, only the fine amount is accepted
			else:
				print("Only $", fine, "needed, thank you.")
				data = (str(tno), datetime.date.today(), str(fine))
				cursor.execute('''INSERT INTO payments (tno, pdate, amount)
					VALUES (?,?,?);''', data)
				return 
			
			data = (str(tno), datetime.date.today(), str(amount))
			cursor.execute('''INSERT INTO payments (tno, pdate, amount) VALUES (?,?,?);''', data)
			
		# some payments already been made
		else:
			# type float
			paid = record[0]
			# type float
			fine = record[1]
			remain = fine - paid

			# been paid in full
			if remain <= 0:
				print("Ticket has already been paid in full, thank you.")
				return 

			# payment accepted, no more payment needed
			elif remain == amount:
				print("Ticket paid in full with current payment, thank you.")
				data = (datetime.date.today(), str(amount), str(tno))
				cursor.execute('''UPDATE payments SET pdate = ?, amount = ? WHERE tno = ?;''', data)

			# more payments to go
			elif remain > amount:
				print("Payment accepted, $", remain - amount, "left to be paid next time.")
				data = (datetime.date.today(), str(amount), str(tno))
				cursor.execute('''UPDATE payments SET pdate = ?, amount = ? WHERE tno = ?;''', data)
			
			# pay too much, only record the amount needed
			else:
				print("Only $", remain, "needed, thank you.")
				new_data = (datetime.date.today(), str(remain), str(tno))
				cursor.execute('''UPDATE payments SET pdate = ?, amount = ? WHERE tno = ?;''', new_data)

	return

def driver_abstract():
	
	global connection, cursor

	fname = input("First name: ")
	lname = input("Last name: ")
	
	# get num of tickets, num of demerit notice, 
	# sum of d.pt w/in past 2 years, sum of d.pt w/in lifetime

	today = datetime.date.today()
	l2_year = datetime.date(today.year - 2, today.month, today.day)
	name_date = (fname, lname, fname, lname, fname, lname, l2_year) 

	cursor.execute('''SELECT count(tno) AS num_of_tickets, 
	count(d.desc) AS num_of_dnotice, sum(d.points) AS sum_dpt_lifetime,
	sum(d2.points) AS sum_dpt_2yr
	
	FROM tickets AS t, demeritNotices AS d, demeritNotices AS d2, 
	registrations AS r
	
	WHERE r.regno = t.regno AND r.fname like ? AND r.lname like ? 
	AND d.fname like ? AND d.lname like ? AND d2.fname like ? AND d2.lname like ?
	AND d2.ddate > ?;''', name_date)

	# Ticket: tno, vdate, violation, fine, regno, make, model
	name = (fname, lname)
	cursor.execute('''SELECT tno, vdate, violation, fine, t.regno, make, model

	FROM tickets AS t, vehicles AS v, registrations AS r
	
	WHERE t.regno = r.regno AND v.vin = r.vin AND 
	r.fname like ? AND r.lname like ?;''', name)


	# show only five
	result = cursor.fetchall()
	num_of_result = len(result)

	print("There are ", num_of_result, " results, maximum of 5 displayed below:")
	for row in result[0:5]:
		print(row)

	remain = num_of_result - 5
	while remain > 0:
		yn_response = input("Would you like to see more records? Please type y or n ")
		if yn_response == 'y':
			request = input("How many more would you like to see? ")
			# too many requested
			if request > remain:
				print("Only ", remain, " left, those will all be displayed below")
				remain = 0
			else:
				print(request, "records displayed below")
				remain -= request
		else:
			return
	return

def getReg():
	#gets user input registration number, for ticketing purposes
	regNum = input("Enter registration number: ")
	while (not regNum.isdigit()) or re.search("quit", regNum, re.IGNORECASE):
		if re.search("quit", regNum, re.IGNORECASE):
			return "q"
		regNum = input("No such registration exits. Please try again, or type quit to return to main.\n")
	return regNum

def getvDate():
	#recursively gets the user to type in a date or quit
	vDate = input("Enter the Violation Date, in yyyy-mm-dd format, leave blank for today, or quit to return to main:\n")
	if re.search("quit", vDate, re.IGNORECASE):
		return 'q'
	elif vDate == '':
		vDate = datetime.now().strftime("%Y-%m-%d")
	try:
		datetime.strptime(vDate, "%Y-%m-%d")
	except ValueError:
		print("Data entered is not a date, please try again")
		vDate = getvDate()
	vDate = vDate.replace('-', ', ')
	vDate = datetime.strptime(vDate, "%Y, %m, %d")
	print("Entered date is: " + vDate.strftime("%Y %B %d"))
	return str(vDate)[:10]


def issueTicket():
	#issue a ticket to a registration. takes a date, description, and fine amount
	global connection, cursor
	
	regNum = getReg()
	if regNum == "q":
		return
	cursor.execute("SELECT fname, lname, make, model, year, color FROM registrations, vehicles WHERE registrations.vin=vehicles.vin AND registrations.regno=" + regNum + ";")
	reg = cursor.fetchone()
	if reg is None:
		print("No such registration exits. Please try again, or type quit to return to main.\n")
		#if user types bad info, recursively call this function until they quit or complete it
		issueTicket()
		return
	print("Registration found:\n" + str(reg))
	
	vDate = getvDate()
	if vDate == 'q':
		return
		
	vText = input("Enter the Violation Text, or quit to return to main:\n")
	# need to check only the first 4 letters of input incase quit comes up organically in the desc
	if re.search("quit", vText[:4], re.IGNORECASE):
		return
		
	vFine = input("Enter the Violation Fine, or quit to return to main:\n")
	while not vFine.isDigit():
		if re.search("quit", vFine, re.IGNORECASE):
			return
		vFine = input("Entered fine is not a number, please try again")
		
	cursor.execute("SELECT tno FROM tickets ORDER BY tno desc")
	tickets = cursor.fetchall()
	if not tickets:
		vNo = 1
	else:
		vNo = tickets[0] + 1
		
	print("Entering ticket number " + str(vNo) + " occuring on date " + vDate.strftime("%Y %m %d") + " with description " + str(vText) + " and fine amount " + str(vFine) + "$.")
	cursor.execute("INSERT INTO tickets VALUES(" + str(vNo) + ", " + str(regNum) + ", " + str(vFine) + ", '" + vText + "', '" + vDate.strftime("%Y %m %d") + "');")
	connection.commit()
		
def search():
	#get user input for the make, model, year, color, and plate for thier search
	global connection, cursor
	
	isValid = False
	#while the input string isn't empty
	while not isValid:
		specList = ["make LIKE \"", "model LIKE \"", "year =	 ", "color LIKE \"", "plate LIKE \""]
		#iterate through the list, appending values when entered or removing if empty
		for i in range(5):
			query = input("Enter the " + specList[i][:-7] + " of the car, or leave blank:\n")
			if query == '':
				specList[i] = ''
			elif re.search("quit", query[:4], re.IGNORECASE):
				return
			else:
				specList[i] += query + '\"'
				if i == 2:
					specList[i] = specList[i][:-1]
				isValid = True
		if not isValid:
			print("No entries entered, please enter some fields or type quit to return to main\n")
	#build a statement to hand to sql
	statement = ''
	for i in range(5):
		if not specList[i] == '':
			statement += specList[i] + " AND "	
	cursor.execute("SELECT make, model, year, color, plate FROM vehicles, registrations WHERE registrations.vin=vehicles.vin AND " + statement[:-5] + ";")
	cars = cursor.fetchall()
	if len(cars) > 4:
		print("Select from these results")
		for i in range(len(cars)):
			print(str(i + 1) + ": " + str(cars[i]))
		num = int(input()) - 1
		cursor.execute("SELECT make, model, year, color, plate, regdate, expiry, fname, lname FROM vehicles, registrations WHERE registrations.vin=vehicles.vin AND " + statement[:-5] + ";")
		cars = cursor.fetchall()
		print("Results: " + str(cars[num]))
	else:
		cursor.execute("SELECT make, model, year, color, plate, regdate, expiry, fname, lname FROM vehicles, registrations WHERE registrations.vin=vehicles.vin AND " + statement[:-5] + ";")
		cars = cursor.fetchall()
		for i in range(len(cars)):
			print("Results: " + str(cars[i]))
		
		 
def main():
	global connection, cursor
	
	#there should be exactly one database specified in the arguement
	if(len(sys.argv) > 3):
		print("ERROR! Too many databases given")
		return
	elif(len(sys.argv) == 2):
		dbPath = sys.argv[1]
		connect(dbPath)
		print("Successfully connected to " + dbPath)
	else:
		print("ERROR! No database specified")
		return
		
	#loggedIn is a boolean determining login status
	loggedIn = False
	#userType should only be 4 different chars: 'a' for agent, 'o' for officer,
	#'q' in the special occasion of quitting during logon,
	#and 'x' when no one is logged on
	userType = 'x'
	
	while(True):
		while(loggedIn == False):
			loggedIn, userType, userID = logon()
			#cascade from user typing quit during logon
			if userType == 'q':
				return
		not_execute = input("\nEnter to quit, logout or any other key(s) to proceed to main menu?")
		if(re.search("quit", not_execute, re.IGNORECASE)):
			print("Have a good day.")
			return
		elif(re.search("logout", not_execute, re.IGNORECASE)):
			loggedIn = False
			userType = 'x'
		else:
			if userType == 'o':
				print("\nPlease choose from the following options:\n")
				command = input("Officer:\nquit (the program),\nissue (a traffic ticket),\nsearch (for a vehicle)\n")
				if(re.search("issue", command, re.IGNORECASE)):
					issueTicket()
				if(re.search("search", command, re.IGNORECASE)):
					search()
			elif userType == 'a':
				print("")
				print("Please choose from the following options:")
				print("")
				command = input("Agent:\nquit (the program),\nlog out (the program),\nbirth (to register birth),\nmarriage (to register marriage),\nrenew (to renew a vehicle registration),\nbill (to process a bill of sale of vehicles),\npayment (process a payment for a traffic ticket),\ndriver (see abstract of a driver)\n")
				if(re.search("birth", command, re.IGNORECASE)):
					reg_birth(userID)
				if(re.search("marriage", command, re.IGNORECASE)):
					reg_marriage(userID)
				if(re.search("renew", command, re.IGNORECASE)):
					renew_vreg()
				if(re.search("bill", command, re.IGNORECASE)):
					process_bill()
				if(re.search("payment", command, re.IGNORECASE)):
					process_payment()
				if(re.search("driver", command, re.IGNORECASE)):
					driver_abstract()
		
		
	

if __name__ == "__main__":
	main()
