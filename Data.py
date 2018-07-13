"""Formats and analyses all data returned by database"""

class DataCollection(list): #a list of DataLog type objects
    def __init__(self):
        list.__init__(self)

    def append_data_log(self, data):
        #add a log's data to the collection
        self.append(DataLog(data))

    def zero_row(self):
        return DataRow(['', 0, 0, 0, 0, 0, 0, 'N', 0, 1, '', ''])

    def getCTotals(self):
        #return a formatted row containing calorie totals of the logs
        Ctotals = self.zero_row()
        Ctotals.format()
        for Log in self:
            Ctotals = Ctotals + Log.getTotals()
        return Ctotals
		
    def get_averages(self):
        Ctotals = self.getCTotals()
        return Ctotals/len(self)

    def get_nutrient_totals(self, index): #get total for each nutrient
        totals = []
        for Log in self:
            totals.append(Log.getTotals()[index])
        totals = DataRow(totals)
        if index == 7:
            for index in range(0,7):
                totals.combineVegData(index)
        return totals
	
class DataLog(list): #a list of DataRow type objects
    def __init__(self, data):
        list.__init__(self)
        self.setTo(data)
	
    def setTo(self, data): #sets log to contain specified data
        for tuple in data:
            r = DataRow(tuple)
            r.format()
            self.append(r)
			
    def LMformat(self):
        for tuple in self:
            tuple.formatLM()
			
    def createZeroRow(self): #create a row with default values for each field
        return DataRow(['', 0, 0, 0, 0, 0, 0, 'N', 0, 1, '', ''])
	
    def getTotals(self): #returns a datarow that is the total of all datarows
        totals = self.createZeroRow()
        totals.format()
        for row in self:
            totals = totals + row
        return totals
		
class DataRow(list):
    def __init__(self, row): #takes an iterable as argument
        list.__init__(self)
        self.setvalues(row)
	
    def format(self):
        self.Vegdict = {'G': (1,0,0,0,0), 'R': (0,1,0,0,0), 'B': (0,0,1,0,0), 'S': (0,0,0,1,0), 'O': (0,0,0,0,1), 'N': (0,0,0,0,0)}
        self.convertVegData()
        self.convertLogID()
        self.adjustbyServings()
	
    def setvalues(self, row): #set values to those of given iterable
        del self[:]
        for object in row:
            self.append(object)

    def convertVegData(self): #convert vegetable data into totalling friendly form
        self[7] = self.Vegdict[self[7]]

    def convertLogID(self): #turn log id into string
        self[11] = str(self[11])

    def adjustbyServings(self):
        self.setvalues(self * (self[8]/self[9]))

    def formatLM(self):
        self.combineVegData()
        self.setvalues(self.formatDisplay(2))
        self.combineQtyESU()
        self.deleteQty()

    def combineVegData(self, index=7): #condense veg data into single total value
        v = 0
        for x in self[index]:
            v += x
        self[index] = v
		
    def combineQtyESU(self): #remove trailing zeroes and combine quantity and serving unit
        qty = str(self[9])
        qty = qty.rstrip('0').rstrip('.') if '.' in qty else qty
        self[8] = qty + ' ' + self[10]

    def deleteQty(self): #remove quantity related values
        self.pop(9)
        self.pop(9)

    def formatDisplay(self, precision):
        newrow = []
        for object in self:
            if isinstance(object, str):
                newrow.append(object)
            else:
                try:
                    t = ()
                    t = t + tuple(self.format_number(item, precision) for item in object)
                except TypeError:
                    newrow.append(self.format_number(object, precision))
                else:
                    newrow.append(t)
        return DataRow(newrow)

    def format_number(self, number, precision):
        x = DisplayNumber(number, precision)
        return x.get()

    def __add__(self, row): #add rows
        newrow = []
        for x, y in zip(self, row):
            if isinstance(x, str):
                newrow.append(x)
            else:
                try:
                    t = tuple(a + b for a, b in zip(x, y))
                except TypeError:
                    newrow.append(x + y)
                else:
                    newrow.append(t)		
        return DataRow(newrow)

    def __sub__(self, row): #subtract rows
        newrow = []
        for x, y in zip(self, row):
            if isinstance(x, str):
                newrow.append(x)
            else:
                try:
                    t = tuple(a - b for a, b in zip(x, y))
                except TypeError:
                    newrow.append(x - y)
                else:
                    newrow.append(t)
        return DataRow(newrow)

    def __mul__(self, factor): #multiply row values by constant
        newrow = []
        for object in self:
            if isinstance(object, str):
                newrow.append(object)
            else:
                try:
                    t = ()
                    t = t + tuple((item * factor) for item in object)
                except TypeError:
                    newrow.append(object * factor)
                else:
                    newrow.append(t)
        return DataRow(newrow)

    def __truediv__(self, factor): #divide row values by constant
        newrow = []
        for object in self:
            if isinstance(object, str):
                newrow.append(object)
            else:
                try:
                    t = ()
                    t = t + tuple((item / factor) for item in object)
                except TypeError:
                    newrow.append(object / factor)
                else:
                    newrow.append(t)
        return DataRow(newrow)
		
class DisplayNumber():
    def __init__(self, float, precision):
        self.precision = precision
        self.digits, self.exp = self.index(str(float))
        self.length = self.exp + self.precision

        self.digits = self.pad()

        if self.length < len(self.digits): #if number has too many digits
            self.digits = self.cut()

    def index(self, floatstring):
        try:
            exponent = floatstring.index('.') #position of decimal dot
        except ValueError:
            exponent = len(floatstring) #if no decimal then digits of float
        else:
            floatstring = floatstring[:exponent] + floatstring[exponent+1:] #remove decimal dot
        return floatstring, exponent

    def pad(self): #add zeroes to format number to calculated length
        return self.digits.ljust(self.length, '0')

    def cut(self): #cut extraneous decimal places by rounding
        return self.round(self.digits[:self.length], self.digits[self.length])

    def round(self, number, rounder):
        if int(rounder) > 4: #if 5 or higher round up
            newdigit, position = self.roundloop(number) #conduct follow up roundings
            return number[:position] + str(newdigit) + ''.zfill(-position-1)
        else:
            return number

    def roundloop(self, number):
        i = 0
        rounded = 10
        while rounded == 10: #while digits are being rounded up from 9 to 10
            i -=1
            try:
                rounded = int(number[i]) + 1
            except IndexError: #all numbers rounded
                rounded = 1 #turn loop off
                self.exp = self.exp + 1
        return rounded, i

    def get(self): #returns number with decimal dot added back
        return self.digits[:self.exp] + '.' + self.digits[self.exp:]