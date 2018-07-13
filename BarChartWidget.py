"""Daily Nutrition Bar Chart Widget"""

import tkinter as tk
from tkinter import font
from Data import *

class BarChart(tk.Frame):
    def __init__(self, nutrient, master=None):
        tk.Frame.__init__(self, master)
        self.w = 325 #change these to scale the canvas
        self.h = 200 #^
        self.chartwidth = 300 #change these to scale the chart
        self.chartheight = 100 #^
        self.weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        TitleFont = tk.font.Font(family="Segoe UI", size=12)
        self.title = tk.Label(master, text=nutrient, font=TitleFont)
        self.title.pack(side='top')
        self.win = tk.Canvas(master, width=self.w, height=self.h)
        self.win.pack(side='bottom')
        self.setwidths()
        self.y1 = (self.h + self.chartheight)/2 - 20 #vertical offset from center
        self.createBars()
        self.createDayLabels()
        self.createNumberLabels()

    def setwidths(self): #calculate element widths based on chart width
        self.barw = self.chartwidth/7
        self.x1 = (self.w - self.chartwidth)/2
        self.widths = [(self.x1 + n*self.barw) for n in range(0,8)]

    def setheights(self, values): #calculate element heights based on chart height
        maxv = max(values)
        if maxv > 0:
            yunit = float(self.chartheight/maxv)
        else:
            yunit = float(0)
        self.heights = [(self.y1 - yunit * float(values[n])) for n in range(0,7)]

    def createBars(self): #create bars in chart
        self.bars = []
        for x in range(0,7):
            self.bars.append(self.win.create_rectangle(self.widths[x], self.y1, self.widths[x+1], self.y1, fill='SteelBlue1'))

    def createDayLabels(self): #create labels for days of the week
        self.daylabels = []
        for x in range(0,7):
            self.daylabels.append(self.win.create_text(self.widths[x] + self.barw/2, self.y1 + 5, text=self.weekdays[x], anchor='e', justify='right', angle=90))

    def createNumberLabels(self): #create numerical data labels
        self.numberlabels = []
        for x in range(0,7):
            self.numberlabels.append(self.win.create_text(self.widths[x] + self.barw/2, self.y1 - 10, text=''))

    def refreshTitle(self, nutrient):
        self.title['text'] = nutrient

    def refreshNutrient(self, nutrient, values): #reset chart for new selected nutrient
        self.refreshTitle(nutrient)
        self.setheights(values)
        self.refreshBars()
        self.refreshNumberLabels(values)

    def refreshDay(self, startday, values): #reset chart for new selected date
        self.setheights(values)
        self.refreshBars()
        self.refreshDayLabels(startday)
        self.refreshNumberLabels(values)

    def refreshBars(self):
        for x in range(0,7):
            self.win.coords(self.bars[x], self.widths[x], self.y1, self.widths[x+1], self.heights[x])

    def refreshDayLabels(self, startday):
        for x in range(0,7):
            self.win.itemconfig(self.daylabels[x], text=self.weekdays[(startday + x)%7])

    def formatNumbers(self, numbers):
        numbers = DataRow(numbers)
        return numbers.formatDisplay(1)

    def refreshNumberLabels(self, values): #reposition labels to fit bars
        values = self.formatNumbers(values)
        for x in range(0,7):
            self.win.coords(self.numberlabels[x], self.widths[x] + self.barw/2, self.heights[x] - 10)
            self.win.itemconfig(self.numberlabels[x], text=values[x])