import sqlite3
import datetime
from decimal import *
from calendar import monthrange

#Global Dictionaries:
veg = {'G': 0, 'R': 1, 'S': 2, 'B': 3, 'O': 4}
keyname = {'ingredient': 'name', 'log': 'id'}
fieldnames = {'ingredient': ('calories', 'carbohydrate', 'protein', 'fat', 'fiber', 'fruit', 'vegetable', 'quantity', 'serving_unit'), 
'log': ('date', 'ingredient', 'quantity_eaten')}


def YesNoConversion(input):
	if input in ['1', 'y', 'yes', 'yeah', 'yup', 'ya']:
		return 1
	elif input in ['0', 'n', 'no', 'nah']:
		return 0
	#else return error, print incorrect input error

def vegetableConversion(input):
	if input in ['g', 'green', 'greens', 'dark green', 'dark greens']:
		return 'G'
	elif input in ['r', 'red', 'orange', 'red and orange']:
		return 'R'
	elif input in ['s', 'starch', 'starchy']:
		return 'S'
	elif input in ['b', 'beans', 'peas', 'beans and peas']:
		return 'B'
	elif input in ['o', 'other']:
		return 'O'
	elif input in ['n', 'none']:
		return 'N'
	#else return error, print incorrect input error
	
def quantityConversion(input):
	return input.split(' ', 1)
	
def ingredientNameInput():
	return input('Name of ingredient: ')
	
def sanitizedCommand(cursor, command, *variables):
	cursor.execute(command, variables)
	return cursor

def convertDate(date):
	return 10000 * date.year + 100 * date.month + date.day
	
def convertDates(dates):
	formatteddates = []
	for date in dates:
		date = convertDate(date)
		formatteddates.append(date)
	return formatteddates
	
def countIngredient(cursor, ingredient):
	cursor = sanitizedCommand(cursor, 'SELECT count(*) FROM INGREDIENT WHERE NAME IS ?', ingredient)
	return cursor.fetchone()[0]
	
def ingredientDoesntExist():
	print ("Ingredient does not exist in database.")

def getWeekStartDate(date):
	return date - datetime.timedelta(days = date.weekday())
	
def makeDate(year, month, day):
	return datetime.date(year, month, day)
	
def getMonthStartDate(date):
	return makeDate(date.year, date.month, 1)

def getDates(date, numdates):
	dates = []
	for x in range(0, numdates):
		dates.append(date)
		date += datetime.timedelta(days = 1)
	return convertDates(dates)
		
def getWeekDates(date):
	date = getWeekStartDate(date)
	return getDates(date, 7)
	
def daysinMonth(date):
	return monthrange(date.year, date.month)[1]

def getMonthDates(date):
	return getDates(date, daysinMonth(date))
	
def dateInput():
	date = []
	for number in input('Enter Date in YYYY/MM/DD format: ').split('/', 2):
		date.append(int(number))
	return makeDate(date[0], date[1], date[2])

def datePrompt(inputstring):
	if YesNoConversion(input(inputstring )) == 1:
		date = datetime.datetime.today()
	else:
		date = dateInput()
	return convertDate(date)
	
def weekPrompt():
	if YesNoConversion(input('Do you wish to view totals for the current week? ')) == 1:
		return getWeekStartDate(datetime.datetime.today())
	else:
		print('Enter the starting date of the week you wish to see')
		return dateInput()
	
def monthPrompt():
	if YesNoConversion(input('Do you wish to view totals for the current month? ')) == 1:
		return getMonthStartDate(datetime.datetime.today())
	else:
		print('Enter the starting date of the month you wish to see')
		return dateInput()

def printDayLog(cursor, date):
	cursor = sanitizedCommand(cursor, 'SELECT ID, INGREDIENT, QUANTITY_EATEN FROM LOG WHERE DATE IS ?', date)
	print(cursor.fetchall())

def isVegetable(code):
	if code in ['G', 'R', 'S', 'B', 'O']:
		return 1
	else:
		return 0

def vegCount(code):
	vegcount = [0, 0, 0, 0, 0]
	if isVegetable(code) == 1:
		vegcount[veg[code]] = 1
	return vegcount

def getDayData(cursor, date):
	data = []
	for row in sanitizedCommand(cursor, 'SELECT NAME, CALORIES, CARBOHYDRATE, PROTEIN, FAT, FIBER, FRUIT, VEGETABLE, QUANTITY_EATEN, QUANTITY FROM INGREDIENT INNER JOIN LOG ON INGREDIENT.NAME = LOG.INGREDIENT WHERE DATE = ?', date):
		data.append(list(row))
	return data
	
def adjustDataByServings(data):
	for row in data:
		row.append (row[8]/row[9]) #determines number of servings eaten in each entry
		for i in range(1, 7):
			row[i] = row[i] * row[10]
	return data
	
def tabulateVegetableDay(data):
	for row in data:
		row[7] = isVegetable(row[7]) * row[10]
	return data
		
def tabulateVegetableWeek(data):
	for row in data:
		row[7] = vegCount(row[7])
		for number in row[7]:
			number = number * row[10]
	return data

def getEntryTotals(data):
	totals = [0, 0, 0, 0, 0, 0, 0, 0]
	for row in data:
		for i in range(1, 7):
			totals[i] += Decimal(row[i])
	return totals

def getVegDayTotals(totals, data):
	for row in data:
		totals[7] += row[7]
	return totals
	
def getVegWeekTotals(totals, data):
	totals[7] = [0, 0, 0, 0, 0]
	for row in data:
		totals[7] = [x + y for x, y in zip(totals[7], row[7])]
	return totals
	
def getAverages(totals, divisor):
	for i in range(1, 7):
		totals[i] = totals[i]/divisor
	return totals
	
def displayServingUnit(cursor, ingredient):
	cursor = sanitizedCommand(cursor, 'SELECT SERVING_UNIT FROM INGREDIENT WHERE NAME IS ?', ingredient)
	print(cursor.fetchone())

def printAverages(averages):
	print("Calories: {}".format(averages[1]))
	print("Carbohydrate: {}".format(averages[2]))
	print("Protein: {}".format(averages[3]))
	print("Fat: {}".format(averages[4]))
	print("Fiber: {}".format(averages[5]))
	print("Fruits: {}".format(averages[6]))

def addIngredient(cursor):
	name = ingredientNameInput()
	if countIngredient(cursor, name) > 0:
		print("Ingredient already in database.")
	else:
		calories = (input('Calories: '))
		carb = (input('Carbohydrate: '))
		protein = (input('Protein: '))
		fat = (input('Fat: '))
		fiber = (input('Fiber: '))
		fruit = YesNoConversion(input('Is this a fruit? ').lower())
		vegetable = vegetableConversion(input('What vegetable group does this come under? ').lower())
		qs = quantityConversion(input('How much is one serving? '))
		quantity = (qs[0])
		servingunit = qs[1]
		sanitizedCommand(cursor, 'INSERT INTO INGREDIENT VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', name, calories, carb, protein, fat, fiber, fruit, vegetable, quantity, servingunit)
		print("Ingredient added!")

def delIngredient(cursor):
	name = ingredientNameInput()
	if countIngredient(cursor, name) == 0:
		ingredientDoesntExist()
	else:
		cursor = sanitizedCommand(cursor, 'DELETE FROM INGREDIENT WHERE NAME IS ?', name)
		print("Ingredient deleted.")

def inputFields():
	return input('Which field(s) do you wish to edit? Enter * for all: ').split()

def convertAsterisk(table):
	return fieldnames[table]
	
def inputValues(fields):
	values = []
	for field in fields:
		values.append(input('{}: '.format(field)))
	return values
	
def doUpdate(cursor, tablename, fields, values, keyvar):
	key = keyname[tablename]
	command = 'UPDATE {} SET ? = ? WHERE {} IS ?'.format(tablename, key)
	print(command) #test
	index = 0
	for field in fields:
		sanitizedCommand(cursor, command, field, values[index], keyvar)
		index += 1

def handleUpdate(table, key):
	fields = inputFields()
	if '*' in fields:
		fields = convertAsterisk(table)
	values = inputValues(fields)
	doUpdate(cursor, table, fields, values, key)
		
def updateIngredient(cursor):
	name = ingredientNameInput()
	if countIngredient(cursor, name) == 0:
		ingredientDoesntExist()
	else:
		cursor = sanitizedCommand(cursor, 'SELECT * FROM INGREDIENT WHERE NAME IS ?', name)
		print(cursor.fetchall())
		handleUpdate('ingredient', name)
		print("Ingredient updated!")
		
def addLog(cursor):
	date = datePrompt('Is entry for today? ')
	name = ingredientNameInput()
	if countIngredient(cursor, name) == 0:
		ingredientDoesntExist()
	else:
		displayServingUnit(cursor, name)
		quantity = Decimal(input('Quantity: '))
		sanitizedCommand(cursor, 'INSERT INTO LOG (DATE, INGREDIENT, QUANTITY_EATEN) VALUES (?, ?, ?)', date, name, quantity)
		print("Entry added!")

def delLog(cursor):
	date = datePrompt('Is entry from today? ')
	printDayLog(cursor, date)
	id = input('Enter the ID of the entry to be deleted: ')
	cursor = sanitizedCommand(cursor, 'DELETE FROM LOG WHERE ID IS ?', id)
	print("Entry deleted.")

def updateLog(cursor):
	date = datePrompt('Is entry from today? ')
	getDayLog(cursor, date)
	id = input('Enter the ID of the entry to be updated: ')
	handleUpdate('log', id)
	print("Entry updated!")

def showDailyLog(cursor):
	date = datePrompt("Is it today's log you wish to see? ")
	data = tabulateVegetableDay(adjustDataByServings(getDayData(cursor, date)))
	totals = getVegDayTotals(getEntryTotals(data), data)
	for row in data:
		print(row[0], row[10], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
	print("Totals: ", totals[1], totals[2], totals[3], totals[4], totals[5], totals[6], totals[7])

def showWeeklyAverages(cursor):
	date = weekPrompt()
	dates = getWeekDates(date)
	data = []
	for day in dates:
		data += tabulateVegetableWeek(adjustDataByServings(getDayData(cursor, day)))
	totals = getVegWeekTotals(getEntryTotals(data), data)
	averages = getAverages(totals, 7)
	print("Week Summary: ")
	printAverages(averages)
	print("Vegetables: {}".format(totals[7]))

def showMonthlyAverages(cursor):
	date = monthPrompt()
	dates = getMonthDates(date)
	for day in dates:
		data = adjustDataByServings(getDayData(cursor, date))
	averages = getAverages(getEntryTotals(data), daysinMonth(date))
	print("Month Summary: ")
	printAverages(averages)


getcontext().prec = 4

conn = sqlite3.connect('food.db')
cursor = conn.cursor()
print ("Opened database successfully");

# testing
#addIngredient(cursor)
addLog(cursor)
#delLog(cursor)
#showDailyLog(cursor) #make this readable
#showWeeklyAverages(cursor) #make vegetables readable
#showMonthlyAverages(cursor)
#updateIngredient(cursor)
#updateLog(cursor)

#fix update command parse correctly to sql

#insert main function here

conn.commit()	
conn.close()