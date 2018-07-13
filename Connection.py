"""Handles all requests to SQLite Database"""

import sqlite3

class DBConnection(sqlite3.Connection):
    def __init__(self, database='food.db'):
        sqlite3.Connection.__init__(self, database)
        self.cursor = self.cursor()
        self.loadedFood = None
        self.loadedExercise = None # Support for future exercise features

    def close_connection(self):
        self.commit()
        self.close()

    def sanitize_command(self, command, *variables):
        #prevents variable information from being executed as part of the command
        self.cursor.execute(command, variables)

        #Food Catalogue
    def do_loadFood(self, index):
        #retrieve food information from database
        self.loadedFood = self.SelFoods[index]
        self.sanitize_command('SELECT * FROM INGREDIENT WHERE NAME IS ?', self.loadedFood)
        return self.cursor.fetchone()

    def do_addFood(self, name, calories, carb, protein, fat, fiber, fruit, vegetable, quantity, servingunit):
        #add a food to the database
        if calories == '':
            calories = 0
        if carb == '':
            carb = 0
        if protein == '':
            protein = 0
        if fat == '':
            fat = 0
        if fiber == '':
            fiber = 0
        command = 'INSERT INTO INGREDIENT (NAME, CALORIES, CARBOHYDRATE, PROTEIN, FAT, FIBER, FRUIT, VEGETABLE, QUANTITY, SERVING_UNIT) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        self.sanitize_command(command, name, calories, carb, protein, fat, fiber, fruit, vegetable, quantity, servingunit)
        self.commit()
        self.loadedFood = None
		
    def do_delFood(self, index):
        #delete a food and all entries of the food from database
        name = self.SelFoods[index]
        if name == self.loadedFood:
            self.loadedFood = None
        foodid = self.getFoodID(name)
        self.sanitize_command('DELETE FROM FOODLOG WHERE INGREDIENT IS ?', foodid)
        self.sanitize_command('DELETE FROM INGREDIENT WHERE NAME IS ?', name)
        self.commit()

    def do_updFood(self, name, calories, carb, protein, fat, fiber, fruit, vegetable, quantity, servingunit):
        #update the parameters of a food in the database
        if self.loadedFood == None:
            return 'Error'
        if calories == '':
            calories = 0
        if carb == '':
            carb = 0
        if protein == '':
            protein = 0
        if fat == '':
            fat = 0
        if fiber == '':
            fiber = 0
        command = 'UPDATE INGREDIENT SET NAME=?, CALORIES=?, CARBOHYDRATE=?, PROTEIN=?, FAT=?, FIBER=?, FRUIT=?, VEGETABLE=?, QUANTITY=?, SERVING_UNIT=? WHERE NAME IS ?'
        self.sanitize_command(command, name, calories, carb, protein, fat, fiber, fruit, vegetable, quantity, servingunit, self.loadedFood)
        self.commit()
        return ''
		
        #Exercise Catalogue #currently not implemented
    def do_loadExercise(self, index):
        self.loadedExercise = self.SelExercises[index]
        self.sanitize_command('SELECT * FROM EXERCISE WHERE NAME IS ?', self.loadedExercise)
        return self.cursor.fetchone()

    def do_addExercise(self, name, calories, carb, protein, fat, fiber, fruit, vegetable, quantity, servingunit):
        if calories == '':
            calories = 0
        command = 'INSERT INTO INGREDIENT (NAME, CALORIES, CARBOHYDRATE, PROTEIN, FAT, FIBER, FRUIT, VEGETABLE, QUANTITY, SERVING_UNIT) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        self.sanitize_command(command, name, calories, carb, protein, fat, fiber, fruit, vegetable, quantity, servingunit)
        self.commit()
        self.loadedExercise = None
		
    def do_delExercise(self, index):
        name = self.SelExercises[index]
        if name == self.loadedExercise:
            self.loadedExercise = None
        id = self.getExerciseID(name)
        self.sanitize_command('DELETE FROM EXERCISELOG WHERE INGREDIENT IS ?', exerciseid) #change
        self.sanitize_command('DELETE FROM EXERCISE WHERE NAME IS ?', name)
        self.commit()

    def do_updExercise(self, name, calories, carb, protein, fat, fiber, fruit, vegetable, quantity, servingunit):
        if self.loadedExercise == None:
            return 'Error'
        if calories == '':
            calories = 0
        command = 'UPDATE INGREDIENT SET NAME=?, CALORIES=?, CARBOHYDRATE=?, PROTEIN=?, FAT=?, FIBER=?, FRUIT=?, VEGETABLE=?, QUANTITY=?, SERVING_UNIT=? WHERE NAME IS ?'
        self.sanitize_command(command, name, calories, carb, protein, fat, fiber, fruit, vegetable, quantity, servingunit, self.loadedFood)
        self.commit()
        return ''

        #Log Manager
    def get_servingUnit(self, foodname):
        #returns the serving size unit for the selected food
        self.sanitize_command('SELECT SERVING_UNIT FROM INGREDIENT WHERE NAME IS ?', foodname)
        return self.cursor.fetchone()[0]

    def get_repUnit(self, exercise):
        self.sanitize_command('SELECT REP_UNIT FROM EXERCISE WHERE NAME IS ?', exercise)
        return self.cursor.fetchone()[0]

    def do_addEntry(self, date, foodname, quantity):
        #add a food log entry to the database
        foodid = self.getFoodID(foodname)
        self.sanitize_command('INSERT INTO FOODLOG (DATE, INGREDIENT, QUANTITY_EATEN) VALUES (?, ?, ?)', date, foodid, quantity)
        self.commit()

    def do_updEntry(self, date, foodname, quantity, id):
        #update parameters for a food log entry in the database
        foodid = self.getFoodID(foodname)
        command = 'UPDATE FOODLOG SET DATE=?, INGREDIENT=?, QUANTITY_EATEN=? WHERE LOG_ID IS ?'
        self.sanitize_command(command, date, foodid, quantity, id)
        self.commit()

    def do_delEntry(self, id):
        #delete an entry in the database
        self.sanitize_command('DELETE FROM FOODLOG WHERE LOG_ID IS ?', id)
        self.commit()
		
        #Calendar Widget
    def HasLog(self, date):
        #return the log id of a certain date's log, if existing
        self.sanitize_command('SELECT LOG_ID FROM FOODLOG WHERE DATE IS ?', date)
        return self.cursor.fetchone()

        #General Data Retrieval
    def getAllFoods(self):
        #retrieve all foods in the database
        self.cursor.execute('SELECT NAME FROM INGREDIENT')
        self.AllFoods = [tuple[0] for tuple in self.cursor.fetchall()]
        self.AllFoods.sort()
        return self.AllFoods

    def getAllExercises(self):
        self.cursor.execute('SELECT NAME FROM EXERCISE')
        self.AllExercises = [tuple[0] for tuple in self.cursor.fetchall()]
        self.AllExercises.sort()
        return self.AllExercises

    def getSelFoods(self, selectVar):
        #return all foods whose name begins with entered string
        self.SelFoods = [food for food in self.AllFoods if food.lower().startswith(selectVar.lower())]
        return self.SelFoods

    def getSelExercises(self, selectVar):
        self.SelExercises = [exercise for exercise in self.AllExercises if exercise.lower().startswith(selectVar.lower())]
        return self.SelExercises

    def getDayData(self, date):
        #retrieve all food log entries for a certain date
        command = 'SELECT NAME, CALORIES, CARBOHYDRATE, PROTEIN, FAT, FIBER, FRUIT, VEGETABLE, QUANTITY_EATEN, QUANTITY, SERVING_UNIT, LOG_ID FROM INGREDIENT INNER JOIN FOODLOG ON INGREDIENT.ID = FOODLOG.INGREDIENT WHERE DATE = ?'
        self.sanitize_command(command, date)
        return self.cursor.fetchall() #format is a list of tuples, where each tuple contains a row of the log
		
    def getFoodID(self, name):
        #return the id of a food
        self.sanitize_command('SELECT ID FROM INGREDIENT WHERE NAME IS ?', name)
        return self.cursor.fetchone()[0]

    def getLogDate(self, logid):
        #return the date of an entry log given its id
        self.sanitize_command('SELECT DATE FROM FOODLOG WHERE LOG_ID IS ?', logid)
        return self.cursor.fetchone()[0]