"""Functions Relating to Date, Month and Year"""

import calendar

class Calendar(calendar.TextCalendar):
    def __init__(self):
        calendar.TextCalendar.__init__(self)
        self.datetime = calendar.datetime.datetime
        self.timedelta = calendar.datetime.timedelta
        Inityear = self.datetime.now().year
        Initmonth = self.datetime.now().month
        self.date = self.datetime(Inityear, Initmonth, 1)
        self.today = self.datetime.now().day

        #Calendar Widget
    def getHeader(self):
        return self.formatmonthname(self.date.year, self.date.month, 0)

    def getMonthDays(self):
        monthdays = self.monthdayscalendar(self.date.year, self.date.month)
        return [day for week in monthdays for day in week]

    def set_prevMonth(self):
        self.date = self.date - self.timedelta(days=1)
        self.date = self.datetime(self.date.year, self.date.month, 1)

    def set_nextMonth(self):
        self.date = self.date + self.timedelta(days=calendar.monthrange(self.date.year, self.date.month)[1] + 1)
        self.date = self.datetime(self.date.year, self.date.month, 1)

    def set_MonthYear(self, year, month):
        self.date = self.datetime(year, month, 1)

    def isDateReal(self, year, month, day): #validate date
        try:
            self.datetime(year, month, day)
        except ValueError:
            return False
        else:
            return True

    def sqlDateFormat(self, year, month, date): #change date format to integer for db storage
        return year*10000 + month*100 + date

        #Weekly Stats
    def getWeekDay(self, year, month, day): #returns the weekday of the given date
        return calendar.weekday(year, month, day)

    def createSQLDatesWeek(self, year, month, day): #returns the week starting from given date
        datelist = []
        date = self.datetime(year, month, day)
        for x in range(0,7):
            datelist.append(self.sqlDateFormat(date.year, date.month, date.day))
            date = date + self.timedelta(days=1)
            date = self.datetime(date.year, date.month, date.day)
        return datelist

        #Monthly Stats
    def convertMonthNametoNumber(self, monthname): #converts month names to their month number
        monthnames = list(calendar.month_name)
        return monthnames.index(monthname)

    def getDaysinMonth(self, year, month): #returns number of days in the given month
        return calendar.monthrange(year, month)[1]

    def sqlDateUnpack(self, sqldate): #convert integer date into component date
        year, remainder = divmod(sqldate, 10000)
        month, remainder = divmod(remainder, 100)
        date = remainder
        return year, month, date

    def createSQLDatesMonth(self, year, month): #returns the month starting from given date
        datelist = []
        for d in range(0, self.getDaysinMonth(year, month)):
            datelist.append(self.sqlDateFormat(year, month, d+1))
        return datelist