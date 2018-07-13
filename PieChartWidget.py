"""Calories Breakdown Pie Chart Widget"""

import math
import tkinter as tk
from tkinter import font
from Data import *

def polar2cart(radius, theta): #converts polar coordinates into cartesian
    theta = math.radians(theta)
    x = radius * math.cos(theta)
    y = radius * math.sin(theta)
    return x, y

def offset(position, xoffset, yoffset): #adjusts a position by specified offsets
    x = position[0] + xoffset
    y = -position[1] + yoffset
    return x, y

class PieChart(tk.Frame):
    def __init__(self, master, title='top'):
        tk.Frame.__init__(self, master)
        self.w = 350 #change these to scale the canvas
        self.h = 200 #^
        self.piesize = 160 #change this to scale the pie chart
        TitleFont = tk.font.Font(family="Segoe UI", size=12)
		
        if title:
            self.title = tk.Label(master, text='Calorie Breakdown by Macronutrient (%)', font=TitleFont)
            self.title.pack(side=title)
		
        self.win = tk.Canvas(master, width=self.w, height=self.h)
        self.win.pack(side='bottom')
        self.createPie()
        self.createLabels()

    def getPieDimensions(self): #set chart dimensions by widget size
        x1 = (self.w - self.piesize)/2
        x2 = self.w - x1
        y1 = (self.h - self.piesize)/2
        y2 = self.h - y1
        return x1, y1, x2, y2
		
    def createPie(self): #create pie slices for each nutrient
        x1, y1, x2, y2 = self.getPieDimensions()
        self.Carc = self.win.create_arc(x1, y2, x2, y1, fill='medium sea green', extent=120, outline='')		
        self.Parc = self.win.create_arc(x1, y2, x2, y1, fill='salmon', start=120, extent=120, outline='')		
        self.Farc = self.win.create_arc(x1, y2, x2, y1, fill='lemon chiffon', start=240, extent=120, outline='')		
		
    def createLabels(self): #create nutrition name and value labels
        self.size = 0.3 * self.piesize
        self.pushout = 0.85

        self.width = self.w/2
        self.height = self.h/2 #these mark the center spot coordinates
		
        cpos = offset(polar2cart(self.size, 60), self.width, self.height)
        ppos = offset(polar2cart(self.size, 180), self.width, self.height)
        fpos = offset(polar2cart(self.size, 300), self.width, self.height)
        self.Cnum = self.win.create_text(cpos, text='0', justify='center')
        self.Pnum = self.win.create_text(ppos, text='0', justify='center')
        self.Fnum = self.win.create_text(fpos, text='0', justify='center')

        cpos = (cpos[0]+self.pushout*(cpos[0]-self.width), cpos[1]+self.pushout*(cpos[1]-self.height))
        self.Cname = self.win.create_text(cpos, text='Carbohydrate', anchor='w')

        ppos = (ppos[0]+self.pushout*(ppos[0]-self.width), ppos[1]+self.pushout*(ppos[1]-self.height))
        self.Pname = self.win.create_text(ppos, text='Protein', anchor='e')

        fpos = (fpos[0]+self.pushout*(fpos[0]-self.width), fpos[1]+self.pushout*(fpos[1]-self.height))
        self.Fname = self.win.create_text(fpos, text='Fat', anchor='w')
		
    def refresh(self, values): #reset slice sizes and number labels
        props = self.calcProportions(values[0], values[1], values[2])
        if props:
            angles = self.calcAngles(props)
            self.refreshSlices(angles)
            self.refreshLabels(angles, props)
        else:
            for item in self.win.find_all():
                self.win.delete(item)
            self.createPie()
            self.createLabels()
		
    def calcProportions(self, carb, prot, fat): #convert nutrient value into portions
        self.total = carb*4 + prot*4 + fat*9
        if self.total == 0:
            return 0
			
        carbp = 4 * carb/self.total
        protp = 4 * prot/self.total
        fatp = 9 * fat/self.total
        return carbp, protp, fatp
		
    def calcAngles(self, proportions):
        return [x * 360 for x in proportions]
		
    def convert360(self, angles):
        newlist = []
        for angle in angles:
            if angle == 360:
                newlist.append(359.99)
            else:
                newlist.append(float(angle))
        return newlist

    def refreshSlices(self, angles):
        carb, prot, fat = self.convert360(angles)
		
        self.win.itemconfig(self.Carc, extent=carb)
        self.win.itemconfig(self.Parc, start=carb)
        self.win.itemconfig(self.Parc, extent=prot)
        self.win.itemconfig(self.Farc, start=carb+prot)
        self.win.itemconfig(self.Farc, extent=fat)
	
    def formatNumbers(self, values): #convert numbers into percentage and round
        newvalues = []
        for number in values:
            x = DisplayNumber(100*number, 1)
            newvalues.append(x.get())
        return newvalues
	
    def refreshLabels(self, angles, props): #reposition chart labels to fit slices
        carb, prot, fat = angles
        carbp, protp, fatp = self.formatNumbers(props)

        cpos = offset(polar2cart(self.size, carb/2), self.width, self.height)
        ppos = offset(polar2cart(self.size, carb+prot/2), self.width, self.height)
        fpos = offset(polar2cart(self.size, carb+prot+fat/2), self.width, self.height)

        self.win.coords(self.Cnum, cpos)
        self.win.itemconfig(self.Cnum, text=carbp)
        self.win.coords(self.Pnum, ppos)
        self.win.itemconfig(self.Pnum, text=protp)
        self.win.coords(self.Fnum, fpos)
        self.win.itemconfig(self.Fnum, text=fatp)

        cpos = (cpos[0]+self.pushout*(cpos[0]-self.width), cpos[1]+self.pushout*(cpos[1]-self.height))
        ppos = (ppos[0]+self.pushout*(ppos[0]-self.width), ppos[1]+self.pushout*(ppos[1]-self.height))
        fpos = (fpos[0]+self.pushout*(fpos[0]-self.width), fpos[1]+self.pushout*(fpos[1]-self.height))
		
        self.win.coords(self.Cname, cpos)
        self.win.coords(self.Pname, ppos)
        self.win.coords(self.Fname, fpos)
		
        if cpos[0] > self.width:
            self.win.itemconfig(self.Cname, text='Carbohydrate', anchor='w')
        else:
            self.win.itemconfig(self.Cname, text='Carbohydrate', anchor='e')

        if ppos[0] > self.width:
            self.win.itemconfig(self.Pname, text='Protein', anchor='w')
        else:
            self.win.itemconfig(self.Pname, text='Protein', anchor='e')

        if fpos[0] > self.width:
            self.win.itemconfig(self.Fname, text='Fat', anchor='w')
        else:
            self.win.itemconfig(self.Fname, text='Fat', anchor='e')