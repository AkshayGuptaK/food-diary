"""Calendar Widget for Selecting Date"""

import tkinter as tk
from tkinter import font
from tkinter import ttk
from CalendarUtils import *
from Sound import *
from Connection import *

def getcalendar():
    return Calendar() # instantiate imported calendar class

class TextBox():
    def __init__(self, canvas, bbox, labeltext, color='grey90', tag='header'):
        self.canvas = canvas
        self.rect = self.canvas.create_rectangle(bbox, fill=color, outline='')
        self.label = self.canvas.create_text(self.getcenter(bbox), text=labeltext, tags=tag)

    def getcenter(self, bbox): #determine center coordinates of widget
        x1, y1, x2, y2 = bbox
        x = (x1+x2)/2
        y = (y1+y2)/2
        return x, y

    def textconfig(self, cfgtext):
        self.canvas.itemconfig(self.label, text=cfgtext)

    def clear(self):
        self.textconfig('')
		
class DateBox(TextBox): #boxes making up calendar each containing a date number
    def __init__(self, canvas, bbox, labeltext, id):
        self.color = 'SystemWindow'
        self.selcolor = '#ecffc4'
        self.textcolor = 'black'
        self.mutetextcolor = 'gray'
        self.seltextcolor = '#05640e' #not currently being used
        TextBox.__init__(self, canvas, bbox, labeltext, color=self.color, tag=id)

    def mute(self):
        self.canvas.itemconfig(self.label, fill=self.mutetextcolor)

    def unmute(self):
        self.canvas.itemconfig(self.label, fill=self.textcolor)

    def select(self):
        self.canvas.itemconfig(self.rect, fill=self.selcolor)

    def deselect(self):
        self.canvas.itemconfig(self.rect, fill=self.color)

    def getDate(self):
        return self.canvas.itemcget(self.label, 'text')

class CalendarWidget(tk.Frame):
    def __init__(self, master=None, connection=None, mode='day', responseFunction=None):

        tk.Frame.__init__(self, master)

        self.Cn = connection
        self.mode = mode
        self.response = responseFunction
        self.selectedDates = [] # no date selected
        self.filledDateCells = [] #no date cells populated
        
        self.cal = getcalendar()
        
        self.makeVariables()
        self.createValidators()
        
        self.setup_styles()
        self.createHeader()
        self.createCalendar()
        self.createEntryFields()
        
        self.selectdate(self.cal.today) #initialize to current day
        
        self.makeTracers()
        self.win.bind('<ButtonPress-1>', self.pressed)
		
    def setup_styles(self):
        # custom ttk styles
        style = ttk.Style(self.master)
        arrow_layout = lambda dir: (
            [('Button.focus', {'children': [('Button.%sarrow' % dir, None)]})]
        )
        style.layout('L.TButton', arrow_layout('left'))
        style.layout('R.TButton', arrow_layout('right'))

    def makeVariables(self): #variables containing selected date information
        self.date = tk.StringVar()
        self.month = tk.StringVar()
        self.year = tk.StringVar()

    def makeTracers(self): #tracers that respond to changes in date
        self.date.trace('w', self.respondDateChange)
        self.month.trace('w', self.respondDateChange)
        self.year.trace('w', self.respondDateChange)

    def createValidators(self): #validators that ensure date is valid
        self.dv = (self.register(self.DayValidate), '%P', '%s')
        self.mv = (self.register(self.MonthValidate), '%P', '%s')
        self.yv = (self.register(self.YearValidate), '%P', '%s')

    def DayValidate(self, P, s):
        if len(P) > 2:
            Error()
            self.after_idle(lambda: self.date.set(s))
            self.after_idle(lambda: self.dateEntry.config(validate='key'))
            return None
        elif P == '':
            return True
        else:
            try:
                if int(P) < 0 or int(P) > 31:
                    Error()
                    self.after_idle(lambda: self.date.set(s))
                    self.after_idle(lambda: self.dateEntry.config(validate='key'))
                    return None
                else:
                    return True
            except ValueError:
                Error()
                self.after_idle(lambda: self.date.set(s))
                self.after_idle(lambda: self.dateEntry.config(validate='key'))
                return None
	
    def MonthValidate(self, P, s):
        if len(P) > 2:
            Error()
            self.after_idle(lambda: self.month.set(s))
            self.after_idle(lambda: self.monthEntry.config(validate='key'))
            return None
        elif P == '':
            return True
        else:
            try:
                if int(P) < 0 or int(P) > 12:
                    Error()
                    self.after_idle(lambda: self.month.set(s))
                    self.after_idle(lambda: self.monthEntry.config(validate='key'))
                    return None
                else:
                    return True
            except ValueError:
                Error()
                self.after_idle(lambda: self.month.set(s))
                self.after_idle(lambda: self.monthEntry.config(validate='key'))
                return None
	
    def YearValidate(self, P, s):
        if len(P) > 4:
            Error()
            self.after_idle(lambda: self.year.set(s))
            self.after_idle(lambda: self.yearEntry.config(validate='key'))
            return None
        elif P == '':
            return True
        else:
            try:
                if int(P) < 0 or int(P) > 9999:
                    Error()
                    self.after_idle(lambda: self.yearEntry.config(validate='key'))
                    return None
                else:
                    return True
            except ValueError:
                Error()
                self.after_idle(lambda: self.year.set(s))
                self.after_idle(lambda: self.yearEntry.config(validate='key'))
                return None

    def createHeader(self): #create frame with buttons above the date boxes
        frameHeader = tk.Frame(self)
        frameHeader.pack(side='top', pady=4, anchor='center')
        leftButton = ttk.Button(frameHeader, style='L.TButton', command=self.prevmonth)
        leftButton.grid(column=0, row=0)
        rightButton = ttk.Button(frameHeader, style='R.TButton', command=self.nextmonth)
        rightButton.grid(column=2, row=0)
        self.header = ttk.Label(frameHeader, width=15, anchor='center')
        self.header.grid(column=1, row=0, padx=12)

    def createCalendar(self):
        frameCalendar = tk.Frame(self)
        frameCalendar.pack()
        self.w = 210
        self.h = 140
        self.win = tk.Canvas(frameCalendar, width=self.w, height=self.h)
        self.win.pack()
        self.cellw = self.w/7 +0.5
        self.cellh = self.h/7
        self.createDayHeaders()
        self.createDateBoxes()
        self.refreshCalendar()

    def createDayHeaders(self):
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        self.headercells = []
        for x in range(0,7):
            self.headercells.append(TextBox(self.win, (x*self.cellw, 0, (x+1)*self.cellw, self.cellh), days[x]))

    def createDateBoxes(self):
        self.datecells = []
        for y in range(1,7):
            for x in range(0,7):
                self.datecells.append(DateBox(self.win, (x*self.cellw, (y)*self.cellh, (x+1)*self.cellw, (y+1)*self.cellh), '', str(x)+str(y) ))

    def createEntryFields(self): #create fields for date entry
        frameEntry = tk.Frame(self)
        frameEntry.pack(side='bottom', pady=5, padx=5)

        self.dateEntry = tk.Entry(frameEntry, justify='center', width=4, textvariable=self.date, validate='key', validatecommand=self.dv)
        self.monthEntry = tk.Entry(frameEntry, justify='center', width=4, textvariable=self.month, validate='key', validatecommand=self.mv)
        self.yearEntry = tk.Entry(frameEntry, justify='center', width=6, textvariable=self.year, validate='key', validatecommand=self.yv)

        tk.Label(frameEntry, text="Date").pack(side='left')
        self.dateEntry.pack(side='left')
        tk.Label(frameEntry, text=" ").pack(side='left') #spacing
        tk.Label(frameEntry, text="Month").pack(side='left')
        self.monthEntry.pack(side='left')
        tk.Label(frameEntry, text=" ").pack(side='left') #spacing
        tk.Label(frameEntry, text="Year").pack(side='left')
        self.yearEntry.pack(side='left')
		
    def refreshCalendar(self): #reset calendar for new selected month
        header = self.cal.getHeader()
        self.header['text'] = header.title()

        for i in range(0, len(self.filledDateCells)):
            self.filledDateCells.pop(0).clear()
		
        caldays = self.cal.getMonthDays()
        for i in range(0, len(caldays)):
            if caldays[i] == 0:
                self.datecells[i].textconfig('')
            else:
                self.datecells[i].textconfig(caldays[i])
                self.filledDateCells.append(self.datecells[i])
        self.muteCheck()
	
    def muteCheck(self): #grey out all date boxes with no log
        for datebox in self.filledDateCells:
            date = self.cal.sqlDateFormat(self.cal.date.year, self.cal.date.month, int(datebox.getDate()))
            if not self.Cn.HasLog(date):
                datebox.mute()
            else:
                datebox.unmute()

    def prevmonth(self):
        self.cal.set_prevMonth()
        self.clearSelection()
        self.refreshCalendar()

    def nextmonth(self):
        self.cal.set_nextMonth()
        self.clearSelection()
        self.refreshCalendar()

    def unpackID(self, id): #converts date box 'coordinate' into date
        x, y = int(id[0]), int(id[1])
        return 7 * y + x - 7

    def getParentDateBox(self, textItem): #return the date box containing text item
        index = self.unpackID(self.win.gettags(textItem)[0])
        return self.datecells[index], index

    def pressed(self, event): #selects a date box after text in it is clicked
        if self.win.type('current') == 'text':
            selbox, index = self.getParentDateBox('current')
            self.showSelection(selbox, index)

    def showSelection(self, datebox, index):
            self.updateEntryFields(datebox) #as a result of tracer, this also clears the current selection
            if self.mode == 'day':
                self.doSelection(datebox)
            elif self.mode == 'week':
                for i in range(0,7):
                    j = index + i
                    if j <= 41:
                        selbox = self.datecells[j]
                        self.doSelection(selbox)

    def doSelection(self, datebox):
        datebox.select()
        self.selectedDates.append(datebox)

    def clearSelection(self):
        for i in range(0, len(self.selectedDates)):
            self.selectedDates.pop(0).deselect()

    def respondDateChange(self, *args): #runs the response function specified at widget creation when date changes
        self.clearSelection()
        if self.response:
            if self.date.get() and self.month.get() and self.year.get():
                self.response()

    def updateEntryFields(self, datebox): #fill entry fields with values of selected date
        self.date.set(datebox.getDate())
        self.month.set(self.cal.date.month)
        self.year.set(self.cal.date.year)

    def selectYrMth(self, year, month): #update calendar to show selected month and year
        self.cal.set_MonthYear(year, month)
        self.refreshCalendar()

    def selectdate(self, day):
        index = self.cal.getMonthDays().index(day)
        self.showSelection(self.datecells[index], index)