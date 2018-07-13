import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter import messagebox
from CalendarUtils import *
from Connection import *
from Data import *
from Sound import *
from CalendarWidget import *
from PieChartWidget import *
from BarChartWidget import *

class DisplayTable(ttk.Treeview):
    def __init__(self, master, columnnames, columnwidths, header, selectionmode, rows=2):
        ttk.Treeview.__init__(self, master, columns=columnnames, show='', selectmode=selectionmode, height=rows)
        self.headerColor = 'grey90'
        self.setWidths(columnnames, columnwidths)
        self.center(columnnames)
		
        if header:
            self.createHeader(columnnames)
			
    def setWidths(self, columns, widths):
        for i in range(0, len(columns)):
            try:
                self.column(columns[i], width=widths[i])
            except TypeError: #if widths is fixed and not an iterable
                self.column(columns[i], width=widths)

    def createHeader(self, columnnames):
        self.insert('', 0, 'header', values=columnnames, tags='header')
        self.tag_configure('header', background=self.headerColor)

    def center(self, columns): #center text in columns
        for column in columns:
            self.column(column, anchor='center')
			
    def get_entryRows(self):
        entryRows = []
        for entry in self.get_children():
            if not self.item(entry, 'tags'): #returns entries that aren't tagged e.g. header
                entryRows.append(entry)
        return entryRows


class SubWindow:
    def __init__(self, master, connection, title):
        self.WindowTitleFont = tk.font.Font(family="Segoe UI", size=14)
        self.MinorTitleFont = tk.font.Font(family="Segoe UI", size=12)
        self.master = master
        self.Cn = connection
        self.master.withdraw()
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        self.master.resizable(width=False, height=False)
		
        self.createFrames()
        tk.Label(self.frameTitle, text=title, font=self.WindowTitleFont, pady=5).pack() #Title		
        self.createWidgets()
        self.center()
		
    def center(self): #center the window on the screen
        self.master.update()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        winsize = tuple(int(_) for _ in self.master.geometry().split('+')[0].split('x'))
        x = w/2 - winsize[0]/2
        y = h/2 - winsize[1]/2
        self.master.geometry("%dx%d+%d+%d" % (winsize + (x, y)))
        self.master.deiconify()
		
    def createFrames(self):
        self.frameTitle = tk.Frame(self.frame)
        self.frameTitle.pack()
		
    def createWidgets(self):
        pass
		
    def quit(self):
        self.master.destroy()
        app.deiconify()


class Application(tk.Toplevel):
    def __init__(self, master=None):
        self.Cn = DBConnection()
        tk.Toplevel.__init__(self, master)
        self.withdraw()
        self.MainMenuFont = tk.font.Font(family="Segoe UI", size=16)
        self.frame = tk.Frame(self)
        self.frame.pack()
        self.resizable(width=False, height=False)
        self.createLabels()
        self.createButtons()
        self.center()

    def center(self): #center the application on the screen
        self.update()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        winsize = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = w/2 - winsize[0]/2
        y = h/2 - winsize[1]/2
        self.geometry("%dx%d+%d+%d" % (winsize + (x, y)))
        self.deiconify()
	
    def createLabels(self):
        tk.Label(self.frame, text="Welcome!").pack()
        tk.Label(self.frame, text="© 2018 Akshay Gupta.  All rights reserved.").pack(side="bottom")
	
    def openFM(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = FoodManager(self.newWindow, self.Cn)
        self.withdraw()
		
    def openLM(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = LogManager(self.newWindow, self.Cn)
        self.withdraw()

    def openWS(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = WeeklyStats(self.newWindow, self.Cn)
        self.withdraw()

    def openMS(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = MonthlyStats(self.newWindow, self.Cn)
        self.withdraw()

    def createButton(self, button, name, command):
        self.button = tk.Button(self.frame)
        self.button["text"] = name
        self.button["font"] = self.MainMenuFont
        self.button["command"] = command
        self.button.pack(ipadx=1, padx=5, fill="x")

    def createButtons(self):
        self.createButton('FoodManager', 'Food Catalogue', self.openFM)
        self.createButton('LogManager', 'Log Manager', self.openLM)
        self.createButton('WeekStats', 'Weekly Stats', self.openWS)
        self.createButton('MonthStats', 'Monthly Stats', self.openMS)
        self.createButton('QUIT', 'EXIT', self.quit)

    def quit(self):
        self.Cn.close_connection()
        root.destroy()


class FoodManager(SubWindow):
    def __init__(self, master, connection):
        SubWindow.__init__(self, master, connection, 'Food Catalogue')
        self.vegVar.set('N')
        self.UnsavedChanges = False
		
    def createWidgets(self):
        self.makeVariables()
        self.makeInputTracers()
        self.registerValidators()
        self.createInputFields()
        self.createFruitButton()
        self.createVegButtons()
        self.createQtyFields()
        self.createFuncButtons()
        self.createListbox()
        self.RefreshListbox()
	
    def makeVariables(self):
        self.nameVar = tk.StringVar()
        self.calVar = tk.StringVar()
        self.carbVar = tk.StringVar()
        self.protVar = tk.StringVar()
        self.fatVar = tk.StringVar()
        self.fibVar = tk.StringVar()
        self.fruitVar = tk.IntVar()
        self.vegVar = tk.StringVar()
        self.qtyVar = tk.StringVar()
        self.serveVar = tk.StringVar()
        self.selectVar = tk.StringVar()
		
    def makeInputTracers(self): #tracers that track when a field value is changed
        self.nameVar.trace('w', self.trackUnsavedChanges)
        self.calVar.trace('w', self.trackUnsavedChanges)
        self.carbVar.trace('w', self.trackUnsavedChanges)
        self.protVar.trace('w', self.trackUnsavedChanges)
        self.fatVar.trace('w', self.trackUnsavedChanges)
        self.fibVar.trace('w', self.trackUnsavedChanges)
        self.fruitVar.trace('w', self.trackUnsavedChanges)
        self.vegVar.trace('w', self.trackUnsavedChanges)
        self.qtyVar.trace('w', self.trackUnsavedChanges)
        self.serveVar.trace('w', self.trackUnsavedChanges)
		
    def trackUnsavedChanges(self, *args):
        self.UnsavedChanges = True
	
    def registerValidators(self): #validators check whether entered values are legal
        self.fnv = (root.register(self.FoodNameValidate), '%P', '%s')
        self.suv = (root.register(self.ServingUnitValidate), '%P', '%s')
        self.kcv = (root.register(self.CaloriesValidate), '%P', '%s')
        self.chv = (root.register(self.CarbValidate), '%P', '%s')
        self.pv = (root.register(self.ProteinValidate), '%P', '%s')
        self.fatv = (root.register(self.FatValidate), '%P', '%s')
        self.fibv = (root.register(self.FiberValidate), '%P', '%s')
        self.qtyv = (root.register(self.QuantityValidate), '%P', '%s')
	
    def FoodNameValidate(self, P, s):
        if len(P) > 32:
            play_error_sound()
            root.after_idle(lambda: self.nameVar.set(s))
            root.after_idle(lambda: self.foodname.config(validate='key'))
            return None
        else:
            return True

    def CaloriesValidate(self, P, s):
        if len(P) > 5:
            play_error_sound()
            root.after_idle(lambda: self.calVar.set(s))
            root.after_idle(lambda: self.kcal.config(validate='key'))
            return None
        elif P == '':
            return True
        else:
            try:
                if float(P) < 0 or float(P) > 9999:
                    play_error_sound()
                    root.after_idle(lambda: self.kcal.config(validate='key'))
                    return None
                else:
                    return True
            except ValueError:
                play_error_sound()
                root.after_idle(lambda: self.calVar.set(s))
                root.after_idle(lambda: self.kcal.config(validate='key'))
                return None

    def CarbValidate(self, P, s):
        if len(P) > 5:
            play_error_sound()
            root.after_idle(lambda: self.carbVar.set(s))
            root.after_idle(lambda: self.carb.config(validate='key'))
            return None
        elif P == '':
            return True
        else:
            try:
                if float(P) < 0 or float(P) > 9999:
                    play_error_sound()
                    root.after_idle(lambda: self.carb.config(validate='key'))
                    return None
                else:
                    return True
            except ValueError:
                play_error_sound()
                root.after_idle(lambda: self.carbVar.set(s))
                root.after_idle(lambda: self.carb.config(validate='key'))
                return None
    
    def ProteinValidate(self, P, s):
        if len(P) > 5:
            play_error_sound()
            root.after_idle(lambda: self.protVar.set(s))
            root.after_idle(lambda: self.protein.config(validate='key'))
            return None
        elif P == '':
            return True
        else:
            try:
                if float(P) < 0 or float(P) > 9999:
                    play_error_sound()
                    root.after_idle(lambda: self.protein.config(validate='key'))
                    return None
                else:
                    return True
            except ValueError:
                play_error_sound()
                root.after_idle(lambda: self.protVar.set(s))
                root.after_idle(lambda: self.protein.config(validate='key'))
                return None
    
    def FatValidate(self, P, s):
        if len(P) > 5:
            play_error_sound()
            root.after_idle(lambda: self.fatVar.set(s))
            root.after_idle(lambda: self.fat.config(validate='key'))
            return None
        elif P == '':
            return True
        else:
            try:
                if float(P) < 0 or float(P) > 9999:
                    play_error_sound()
                    root.after_idle(lambda: self.fat.config(validate='key'))
                    return None
                else:
                    return True
            except ValueError:
                play_error_sound()
                root.after_idle(lambda: self.fatVar.set(s))
                root.after_idle(lambda: self.fat.config(validate='key'))
                return None
    
    def FiberValidate(self, P, s):
        if len(P) > 5:
            play_error_sound()
            root.after_idle(lambda: self.fibVar.set(s))
            root.after_idle(lambda: self.fiber.config(validate='key'))
            return None
        elif P == '':
            return True
        else:
            try:
                if float(P) < 0 or float(P) > 9999:
                    play_error_sound()
                    root.after_idle(lambda: self.fiber.config(validate='key'))
                    return None
                else:
                    return True
            except ValueError:
                play_error_sound()
                root.after_idle(lambda: self.fibVar.set(s))
                root.after_idle(lambda: self.fiber.config(validate='key'))
                return None

    def QuantityValidate(self, P, s):
        if len(P) > 5:
            play_error_sound()
            root.after_idle(lambda: self.qtyVar.set(s))
            root.after_idle(lambda: self.Qty.config(validate='key'))
            return None
        elif P == '':
            return True
        else:
            try:
                if float(P) < 0 or float(P) > 9999:
                    play_error_sound()
                    root.after_idle(lambda: self.Qty.config(validate='key'))
                    return None
                else:
                    return True
            except ValueError:
                play_error_sound()
                root.after_idle(lambda: self.qtyVar.set(s))
                root.after_idle(lambda: self.Qty.config(validate='key'))
                return None

    def ServingUnitValidate(self, P, s):
        if len(P) > 12:
            play_error_sound()
            root.after_idle(lambda: self.serveVar.set(s))
            root.after_idle(lambda: self.Serving.config(validate='key'))
            return None
        else:
            return True
        
    def createInputLabel(self, containerframe, textstr, rowNumber, columnNumber, spanLabel):
        tk.Label(containerframe, text=textstr).grid(row=rowNumber, column=columnNumber, columnspan=spanLabel, sticky='W')
    
    def createVegetableRadioButton(self, button, rowNumber, columnNumber, vegValue):
        self.button = tk.Radiobutton(self.frameVeg, variable=self.vegVar, value=vegValue)
        self.button.grid(row=rowNumber, column=columnNumber)
    
    def createFrames(self):
        self.frameTitle = tk.Frame(self.master)
        self.frameTitle.pack(side='top')
        self.frameUser = tk.Frame(self.master)
        self.frameUser.pack()
        self.createUserSubFrames()
        self.frameButtons = tk.Frame(self.master)
        self.frameButtons.pack(side='bottom')
        
    def createUserSubFrames(self):
        self.frameInput = tk.Frame(self.frameUser)
        self.frameInput.grid(row=1, column=1, sticky='w')
        self.frameVeg = tk.Frame(self.frameUser)
        self.frameVeg.grid(row=2, column=1, sticky='w')
        self.frameQty = tk.Frame(self.frameUser)
        self.frameQty.grid(row=3, column=1, sticky='w')
        self.frameList = tk.Frame(self.frameUser)
        self.frameList.grid(row=1, column=0, rowspan=3, padx=12)
        
    def createInputFields(self):
        self.createInputLabel(self.frameInput, 'Name', 1, 0, 1)
        self.foodname = tk.Entry(self.frameInput, textvariable=self.nameVar, validate='key', validatecommand=self.fnv)
        self.foodname.grid(row=1, column=1, columnspan=4, sticky='W')
        
        tk.Label(self.frameInput, text='kCal').grid(row=2, column=0, sticky='W')
        self.kcal = tk.Entry(self.frameInput, width=4, textvariable=self.calVar, validate='key', validatecommand=self.kcv)
        self.kcal.grid(row=2, column=1, sticky='W')
    
        tk.Label(self.frameInput, text='     ').grid(row=2, column=2) #column spacing
        
        tk.Label(self.frameInput, text='Carb').grid(row=3, column=0, sticky='W')
        self.carb = tk.Entry(self.frameInput, width=4, textvariable=self.carbVar, validate='key', validatecommand=self.chv)
        self.carb.grid(row=3, column=1, sticky='W')
        
        tk.Label(self.frameInput, text='Protein').grid(row=3, column=3, sticky='W')
        self.protein = tk.Entry(self.frameInput, width=4, textvariable=self.protVar, validate='key', validatecommand=self.pv)
        self.protein.grid(row=3, column=4, sticky='W')
        
        tk.Label(self.frameInput, text='Fat').grid(row=4, column=0, sticky='W')
        self.fat = tk.Entry(self.frameInput, width=4, textvariable=self.fatVar, validate='key', validatecommand=self.fatv)
        self.fat.grid(row=4, column=1, sticky='W')
        
        tk.Label(self.frameInput, text='Fiber').grid(row=4, column=3, sticky='W')
        self.fiber = tk.Entry(self.frameInput, width=4, textvariable=self.fibVar, validate='key', validatecommand=self.fibv)
        self.fiber.grid(row=4, column=4, sticky='W')
        
    def createFruitButton(self):
        tk.Label(self.frameInput, text="Fruit").grid(row=5, column=0, sticky='W')
        self.FruitButton = tk.Checkbutton(self.frameInput, variable=self.fruitVar)
        self.FruitButton.grid(row=5, column=1, sticky='W')
        
    def createVegButton(self, name, button, rowNumber, columnNumber, spanLabel, code):
        self.createInputLabel(self.frameVeg, name, rowNumber, columnNumber, spanLabel)
        self.createVegetableRadioButton(button, rowNumber, columnNumber+spanLabel, code)
        
    def createVegButtons(self):
        self.createInputLabel(self.frameVeg, 'Vegetable Group:', 6, 0, 3)
        self.createVegButton('Dark Green', 'DarkGreen', 7, 0, 2, 'G')
        self.createVegButton('Red & Orange', 'Red', 8, 0, 2, 'R')
        self.createVegButton('Beans/Lentils', 'Beans', 9, 0, 2, 'B')
        self.createVegButton('Starchy', 'Starchy', 7, 3, 1, 'S')
        self.createVegButton('Other', 'Other', 8, 3, 1, 'O')
        self.createVegButton('None', 'None', 9, 3, 1, 'N')

    def createQtyFields(self):	
        tk.Label(self.frameQty, text="Amount in 1 Serving:").grid(row=0, columnspan=2, sticky='w')
        tk.Label(self.frameQty, text="Qty").grid(row=1, column=0)
        self.Qty = tk.Entry(self.frameQty, width=4, textvariable=self.qtyVar, validate='key', validatecommand=self.qtyv)
        self.Qty.grid(row=2, column=0)
        tk.Label(self.frameQty, text="Serving Unit").grid(row=1, column=1 )
        self.Serving = tk.Entry(self.frameQty, width=11, textvariable=self.serveVar, validate='key', validatecommand=self.suv)
        self.Serving.grid(row=2, column=1)
    
    def createListbox(self):
        self.SelField = tk.Entry(self.frameList, textvariable=self.selectVar, width=25)
        self.scroll = tk.Scrollbar(self.frameList, orient='vertical')
        self.select = tk.Listbox(self.frameList, activestyle='none', yscrollcommand=self.scroll.set, height=15, width=25)
        self.scroll.config (command=self.select.yview)
        self.SelField.pack(side="top", anchor='nw')
        self.scroll.pack(side='right', fill='y')
        self.select.pack(side='left',  fill='both')			
        self.selectVar.trace('w', self.ListboxDisplayUpdate)
        self.select.bind("<Double-Button-1>", self.loadFood)
    
    def createFunctionButton(self, name, textstr, buttonCommand):
        self.name = tk.Button(self.frameButtons, text=textstr,command=buttonCommand)
        self.name.pack(side='left', pady = 5)
        
    def createFuncButtons(self):
        self.createFunctionButton('LoadButton',' Edit ', self.loadFood)
        self.createFunctionButton('AddButton', ' Add  ', self.addFood)
        self.createFunctionButton('UpdButton', 'Update', self.updateFood)
        self.createFunctionButton('DelButton', 'Delete', self.deleteFood)
        self.createFunctionButton('QuitButton', 'Quit and Return to Main Menu', self.quit)
    
    def whichSelected(self):
        if self.select.curselection():
            return int(self.select.curselection()[0])
        else:
            return 'Error'
    
    def loadFood(self, *args):
        if self.whichSelected() == 'Error':
            messagebox.showwarning('Invalid Request', 'Please select a food for editing first.', parent=self.master)
            return
        if self.UnsavedChanges:
            if not messagebox.askyesno('Unsaved Changes', 'If you proceed all your changes will be lost. Do you still wish to proceed?', parent=self.master):
                return
        foodinfo = self.Cn.do_loadFood(self.whichSelected())
        self.nameVar.set(foodinfo[1])
        self.calVar.set(foodinfo[2])
        self.carbVar.set(foodinfo[3])
        self.protVar.set(foodinfo[4])
        self.fatVar.set(foodinfo[5])
        self.fibVar.set(foodinfo[6])
        self.fruitVar.set(foodinfo[7])
        self.vegVar.set(foodinfo[8])
        self.qtyVar.set(foodinfo[9])
        self.serveVar.set(foodinfo[10])
        self.UnsavedChanges = False
    
    def addFood(self):
        if self.nameVar.get() in self.Cn.AllFoods:
            messagebox.showwarning('Invalid Entry!', 'A food item with this name already exists. Please choose another name or modify the existing item first.', parent=self.master)
            return
        elif self.qtyVar.get() == '' or float(self.qtyVar.get()) == 0:
            messagebox.showwarning('Invalid Entry!', 'Quantity cannot be zero.', parent=self.master)
            return
        elif self.serveVar.get() == '':
            messagebox.showwarning('Invalid Entry!', 'Serving unit must be defined.', parent=self.master)
            return
        self.Cn.do_addFood(self.nameVar.get(), self.calVar.get(), self.carbVar.get(), self.protVar.get(), self.fatVar.get(), self.fibVar.get(), self.fruitVar.get(), self.vegVar.get(), self.qtyVar.get(), self.serveVar.get())
        self.nameVar.set('')
        self.calVar.set('')
        self.carbVar.set('')
        self.protVar.set('')
        self.fatVar.set('')
        self.fibVar.set('')
        self.fruitVar.set(0)
        self.vegVar.set('N')
        self.qtyVar.set('')
        self.serveVar.set('')
        self.UnsavedChanges = False
        self.RefreshListbox()
    
    def updateFood(self):
        if self.qtyVar.get() == '' or float(self.qtyVar.get()) == 0:
            messagebox.showwarning('Invalid Entry!', 'Quantity cannot be zero.', parent=self.master)
            return
        elif self.serveVar.get() == '':
            messagebox.showwarning('Invalid Entry!', 'Serving unit must be defined.', parent=self.master)
            return
        Return = self.Cn.do_updFood(self.nameVar.get(), self.calVar.get(), self.carbVar.get(), self.protVar.get(), self.fatVar.get(), self.fibVar.get(), self.fruitVar.get(), self.vegVar.get(), self.qtyVar.get(), self.serveVar.get())
        if Return == 'Error':
            messagebox.showwarning('Invalid Request', 'Please press the edit button or double click the food you wish to edit first.', parent=self.master)
            return
        self.UnsavedChanges = False
        self.RefreshListbox()
    
    def deleteFood(self):
        if not self.whichSelected():
            messagebox.showwarning('Invalid Request', 'Please select a food to delete first.', parent=self.master)
            return
        if messagebox.askokcancel('Delete Confirmation', 'Deleting this food will also delete all log entries referencing this food. Proceed?', default='cancel', parent=self.master) :
            self.Cn.do_delFood(self.whichSelected())
            self.RefreshListbox()
    
    def RefreshListbox(self):
        self.Cn.getAllFoods()
        self.ListboxDisplayUpdate()
        
    def ListboxDisplayUpdate(self, *args):
        self.select.delete(0, 'end')
        for food in self.Cn.getSelFoods(self.selectVar.get()):
            self.select.insert('end', food)

			
class ExerciseCatalogue(SubWindow):
    def __init__(self, master, connection):
        SubWindow.__init__(self, master, connection, 'Exercise Catalogue')
        self.UnsavedChanges = False
        self.Muscles = ['', 'Abdominal', 'Back', 'Biceps', 'Calves', 'Chest', 'Forearm', 'Glutes', 'Hamstrings', 'Quads', 'Shoulders', 'Triceps']
        self.Motions = ['', 'Horizontal Push', 'Horizontal Pull', 'Vertical Push', 'Vertical Pull', 'Quad Dominant', 'Hip Dominant', 'Elbow Flexion', 'Elbow Extension']
        
    def createWidgets(self):
        self.makeVariables()
        self.makeInputTracers()
        self.registerValidators()
        self.createInputFields()
        self.createQtyFields()
        self.createFuncButtons()
        self.createListbox()
        self.RefreshListbox()
    
    def makeVariables(self):
        self.nameVar = tk.StringVar()
        self.primaryVar = tk.StringVar()
        self.secondary1Var = tk.StringVar()
        self.secondary2Var = tk.StringVar()
        self.secondary3Var = tk.StringVar()
        self.calVar = tk.StringVar()
        self.motionVar = tk.StringVar()
        self.qtyVar = tk.StringVar()
        self.repVar = tk.StringVar()
        self.selectVar = tk.StringVar()
        
    def makeInputTracers(self):
        self.nameVar.trace('w', self.trackUnsavedChanges)
        self.primaryVar.trace('w', self.trackUnsavedChanges)
        self.secondary1Var.trace('w', self.trackUnsavedChanges)
        self.secondary2Var.trace('w', self.trackUnsavedChanges)
        self.secondary3Var.trace('w', self.trackUnsavedChanges)
        self.calVar.trace('w', self.trackUnsavedChanges)
        self.motionVar.trace('w', self.trackUnsavedChanges)
        self.qtyVar.trace('w', self.trackUnsavedChanges)
        self.repVar.trace('w', self.trackUnsavedChanges)
        
    def trackUnsavedChanges(self, *args):
        self.UnsavedChanges = True
	
    def registerValidators(self):
        self.env = (root.register(self.ExerciseNameValidate), '%P', '%s')
        self.qtyv = (root.register(self.QuantityValidate), '%P', '%s')
        self.ruv = (root.register(self.RepUnitValidate), '%P', '%s')
        self.kcv = (root.register(self.CaloriesValidate), '%P', '%s')
    
    def ExerciseNameValidate(self, P, s):
        if len(P) > 32:
            play_error_sound()
            root.after_idle(lambda: self.nameVar.set(s))
            root.after_idle(lambda: self.exercisename.config(validate='key'))
            return None
        else:
            return True
    
    def CaloriesValidate(self, P, s):
        if len(P) > 5:
            play_error_sound()
            root.after_idle(lambda: self.calVar.set(s))
            root.after_idle(lambda: self.kcal.config(validate='key'))
            return None
        elif P == '':
            return True
        else:
            try:
                if float(P) < 0 or float(P) > 9999:
                    play_error_sound()
                    root.after_idle(lambda: self.kcal.config(validate='key'))
                    return None
                else:
                    return True
            except ValueError:
                play_error_sound()
                root.after_idle(lambda: self.calVar.set(s))
                root.after_idle(lambda: self.kcal.config(validate='key'))
                return None

    def QuantityValidate(self, P, s):
        if len(P) > 5:
            play_error_sound()
            root.after_idle(lambda: self.qtyVar.set(s))
            root.after_idle(lambda: self.Qty.config(validate='key'))
            return None
        elif P == '':
            return True
        else:
            try:
                if float(P) < 0 or float(P) > 9999:
                    play_error_sound()
                    root.after_idle(lambda: self.Qty.config(validate='key'))
                    return None
                else:
                    return True
            except ValueError:
                play_error_sound()
                root.after_idle(lambda: self.qtyVar.set(s))
                root.after_idle(lambda: self.Qty.config(validate='key'))
                return None
    
    def RepUnitValidate(self, P, s):
        if len(P) > 12:
            play_error_sound()
            root.after_idle(lambda: self.repVar.set(s))
            root.after_idle(lambda: self.RepUnit.config(validate='key'))
            return None
        else:
            return True
        
    def createInputLabel(self, containerframe, textstr, rowNumber, columnNumber, spanLabel):
        tk.Label(containerframe, text=textstr).grid(row=rowNumber, column=columnNumber, columnspan=spanLabel, sticky='W')
    
    def createFrames(self):
        self.frameTitle = tk.Frame(self.master)
        self.frameTitle.pack(side='top')
        self.frameUser = tk.Frame(self.master)
        self.frameUser.pack()
        self.createUserSubFrames()
        self.frameButtons = tk.Frame(self.master)
        self.frameButtons.pack(side='bottom')
		
    def createUserSubFrames(self):
        self.frameInput = tk.Frame(self.frameUser)
        self.frameInput.grid(row=1, column=1, sticky='w')
        self.frameQty = tk.Frame(self.frameUser)
        self.frameQty.grid(row=2, column=1, sticky='w')
        self.frameList = tk.Frame(self.frameUser)
        self.frameList.grid(row=1, column=0, rowspan=3, padx=12)
        
    def createInputFields(self):
        self.createInputLabel(self.frameInput, 'Name', 1, 0, 1)
        self.exercisename = tk.Entry(self.frameInput, textvariable=self.nameVar, validate='key', validatecommand=self.env)
        self.exercisename.grid(row=1, column=1, columnspan=4, sticky='W')
        
        primarylistname = ttk.Labelframe(self.frameInput, text='Primary Muscle')
        primarylist = ttk.Combobox(primarylistname, values=self.Muscles, state='readonly', textvariable = self.primaryVar, width=10)
        primarylist.current(0)
        primarylistname.grid(row=2, column=1)
        primarylist.pack(pady=5, padx=10)
    
        secondarylistname = ttk.Labelframe(self.frameInput, text='Secondary Muscles')
        secondarylistA = ttk.Combobox(secondarylistname, values=self.Muscles, state='readonly', textvariable = self.secondary1Var, width=10)
        secondarylistA.current(0)
        secondarylistB = ttk.Combobox(secondarylistname, values=self.Muscles, state='readonly', textvariable = self.secondary2Var, width=10)
        secondarylistB.current(0)
        secondarylistC = ttk.Combobox(secondarylistname, values=self.Muscles, state='readonly', textvariable = self.secondary3Var, width=10)
        secondarylistC.current(0)
        secondarylistname.grid(row=3, column=1)
        secondarylistA.pack(pady=5, padx=10)
        secondarylistB.pack(pady=5, padx=10)
        secondarylistC.pack(pady=5, padx=10)
    
        motionlistname = ttk.Labelframe(self.frameInput, text='Movement Type')
        motionlist = ttk.Combobox(motionlistname, values=self.Motions, state='readonly', textvariable = self.motionVar, width=10)
        motionlist.current(0)
        motionlistname.grid(row=4, column=1)
        motionlist.pack(pady=5, padx=10)
        
        tk.Label(self.frameInput, text='Calories Expended').grid(row=2, column=0, sticky='W')
        self.kcal = tk.Entry(self.frameInput, width=4, textvariable=self.calVar, validate='key', validatecommand=self.kcv)
        self.kcal.grid(row=2, column=1, sticky='W')
		
    def createQtyFields(self):	
        tk.Label(self.frameQty, text="Standard Exercise Consists of:").grid(row=0, columnspan=2, sticky='w') #change text
        tk.Label(self.frameQty, text="Qty").grid(row=1, column=0)
        self.Qty = tk.Entry(self.frameQty, width=4, textvariable=self.qtyVar, validate='key', validatecommand=self.qtyv)
        self.Qty.grid(row=2, column=0)
        tk.Label(self.frameQty, text="Activity Unit").grid(row=1, column=1 )
        self.RepUnit = tk.Entry(self.frameQty, width=11, textvariable=self.repVar, validate='key', validatecommand=self.suv)
        self.RepUnit.grid(row=2, column=1)
    
    def createListbox(self):
        self.SelField = tk.Entry(self.frameList, textvariable=self.selectVar, width=25)
        self.scroll = tk.Scrollbar(self.frameList, orient='vertical')
        self.select = tk.Listbox(self.frameList, activestyle='none', yscrollcommand=self.scroll.set, height=15, width=25)
        self.scroll.config (command=self.select.yview)
        self.SelField.pack(side="top", anchor='nw')
        self.scroll.pack(side='right', fill='y')
        self.select.pack(side='left',  fill='both')			
        self.selectVar.trace('w', self.ListboxDisplayUpdate)
        self.select.bind("<Double-Button-1>", self.loadExercise)
    
    def createFunctionButton(self, name, textstr, buttonCommand):
        self.name = tk.Button(self.frameButtons, text=textstr,command=buttonCommand)
        self.name.pack(side='left', pady = 5)
        
    def createFuncButtons(self):
        self.createFunctionButton('LoadButton',' Edit ', self.loadExercise)
        self.createFunctionButton('AddButton', ' Add  ', self.addExercise)
        self.createFunctionButton('UpdButton', 'Update', self.updateExercise)
        self.createFunctionButton('DelButton', 'Delete', self.deleteExercise)
        self.createFunctionButton('QuitButton', 'Quit and Return to Main Menu', self.quit)
    
    def whichSelected(self):
        if self.select.curselection():
            return int(self.select.curselection()[0])
        else:
            return 'Error'
	
    def loadExercise(self, *args):
        if self.whichSelected() == 'Error':
            messagebox.showwarning('Invalid Request', 'Please select an exercise for editing first.', parent=self.master)
            return
        if self.UnsavedChanges:
            if not messagebox.askyesno('Unsaved Changes', 'If you proceed all your changes will be lost. Do you still wish to proceed?', parent=self.master):
                return
        exerciseinfo = self.Cn.do_loadExercise(self.whichSelected())
        self.nameVar.set(exerciseinfo[1])
        self.primaryVar.set(exerciseinfo[2])
        self.secondary1Var.set(exerciseinfo[2])
        self.secondary2Var.set(exerciseinfo[2])
        self.secondary3Var.set(exerciseinfo[2])
        self.motionVar.set(exerciseinfo[2])
        self.calVar.set(exerciseinfo[2])
        self.qtyVar.set(exerciseinfo[9])
        self.repVar.set(exerciseinfo[10])
        self.UnsavedChanges = False
    
    def addExercise(self):
        if self.nameVar.get() in self.Cn.AllExercises:
            messagebox.showwarning('Invalid Entry!', 'An exercise item with this name already exists. Please choose another name or modify the existing item first.', parent=self.master)
            return
        elif self.qtyVar.get() == '' or float(self.qtyVar.get()) == 0:
            messagebox.showwarning('Invalid Entry!', 'Quantity cannot be zero.', parent=self.master)
            return
        elif self.serveVar.get() == '':
            messagebox.showwarning('Invalid Entry!', 'Repetition unit must be defined.', parent=self.master)
            return
        self.Cn.do_addExercise(self.nameVar.get(), self.primaryVar.get(), self.secondary1Var.get(), self.secondary2Var.get(), self.secondary3Var.get(), self.motionVar.get(), self.calVar.get(), self.qtyVar.get(), self.repVar.get())
        self.nameVar.set('')
        self.primaryVar.set(exerciseinfo[2]) #fix
        self.secondary1Var.set(exerciseinfo[2])
        self.secondary2Var.set(exerciseinfo[2])
        self.secondary3Var.set(exerciseinfo[2])
        self.motionVar.set(exerciseinfo[2]) #fix
        self.calVar.set('')
        self.qtyVar.set('')
        self.repVar.set('')
        self.UnsavedChanges = False
        self.RefreshListbox()
	
    def updateExercise(self):
        if self.qtyVar.get() == '' or float(self.qtyVar.get()) == 0:
            messagebox.showwarning('Invalid Entry!', 'Quantity cannot be zero.', parent=self.master)
            return
        elif self.repVar.get() == '':
            messagebox.showwarning('Invalid Entry!', 'Repetition unit must be defined.', parent=self.master)
            return
        Return = self.Cn.do_updExercise(self.nameVar.get(), self.primaryVar.get(), self.secondary1Var.get(), self.secondary2Var.get(), self.secondary3Var.get(), self.motionVar.get(), self.calVar.get(), self.qtyVar.get(), self.repVar.get())
        if Return == 'Error':
            messagebox.showwarning('Invalid Request', 'Please press the edit button or double click the exercise you wish to edit first.', parent=self.master)
            return
        self.UnsavedChanges = False
        self.RefreshListbox()
    
    def deleteExercise(self):
        if not self.whichSelected():
            messagebox.showwarning('Invalid Request', 'Please select an exercise to delete first.', parent=self.master)
            return
        if messagebox.askokcancel('Delete Confirmation', 'Deleting this exercise will also delete all log entries referencing this exercise. Proceed?', default='cancel', parent=self.master) :
            self.Cn.do_delExercise(self.whichSelected())
            self.RefreshListbox()
    
    def RefreshListbox(self):
        self.Cn.getAllExercises()
        self.ListboxDisplayUpdate()
        
    def ListboxDisplayUpdate(self, *args):
        self.select.delete(0, 'end')
        for exercise in self.Cn.getSelExercises(self.selectVar.get()):
            self.select.insert('end', exercise)
	
class LogManager(SubWindow):
    def __init__(self, master, connection):
        self.widths = [120, 50, 50, 50, 50, 50, 50, 50, 100]
        SubWindow.__init__(self, master, connection, 'Log Manager')
        self.UnsavedChanges = False
        self.loadedEntry = None
    
    def createFrames(self):
        self.frameTitle = tk.Frame(self.master)
        self.frameTitle.pack(side='top')
        self.frameMain = tk.Frame(self.master)
        self.frameMain.pack(side='top')
        self.frameQuit = tk.Frame(self.master)
        self.frameQuit.pack(side='bottom', fill='x', padx=15)
        self.frameFooter = tk.Frame(self.master)
        self.frameFooter.pack(side='bottom', pady=5)
    
        self.frameLeft = tk.Frame(self.frameMain)
        self.frameLeft.pack(side='top', fill='x', padx=10, pady=5)
        self.frameRight = tk.Frame(self.frameMain)
        self.frameRight.pack(side='bottom', padx=5, pady=5)
        
        self.frameInput = tk.Frame(self.frameFooter)
        self.frameInput.pack(side='left', padx=5, anchor='w')
        
        self.frameList = tk.Frame(self.frameRight)
        self.frameList.pack(side='top')
        
    def createWidgets(self):
        self.makeValidators()
        self.makeCalendar()
        self.makePieChart()
        self.makeEntryFields()
        self.makeButtons()
        self.makeListbox()
        self.makeDisplayTable()
        
    def makeValidators(self):
        self.fv = (root.register(self.FoodValidate), '%P', '%s')
        self.qv = (root.register(self.QuantityValidate), '%P', '%s')
		
    def FoodValidate(self, P, s):
        if len(P) > 32:
            play_error_sound()
            root.after_idle(lambda: self.selectedFood.set(s))
            root.after_idle(lambda: self.foodlist.config(validate='key'))
            return None
        else:
            return True
    
    def QuantityValidate(self, P, s):
        if len(P) > 5:
            play_error_sound()
            root.after_idle(lambda: self.quantity.set(s))
            root.after_idle(lambda: self.quantityField.config(validate='key'))
            return None
        elif P == '':
            return True
        else:
            try:
                if float(P) < 0 or float(P) > 9999:
                    play_error_sound()
                    root.after_idle(lambda: self.quantityField.config(validate='key'))
                    return None
                else:
                    return True
            except ValueError:
                play_error_sound()
                root.after_idle(lambda: self.quantity.set(s))
                root.after_idle(lambda: self.quantityField.config(validate='key'))
                return None
    
    def makeCalendar(self):
        self.tkcal = CalendarWidget(master=self.frameLeft, connection=self.Cn, responseFunction=self.loadLog)
        self.tkcal.pack(side='left')
        
    def makePieChart(self):
        self.piechart = PieChart(self.frameLeft, title=False)
        self.piechart.pack(side='right')	
		
    def makeEntryFields(self):
        self.foods = (self.Cn.getAllFoods())
        self.selectedFood = tk.StringVar()
        foodlistname = ttk.Labelframe(self.frameInput, text='Foods')
        foodldbutton = tk.Button(self.frameInput, text='>', command=self.updateServingUnit)
        quantityname = ttk.Labelframe(self.frameInput, text='Quantity', height=50, width=130)
    
        foodlistname.pack(side='left', padx = 5)
        foodldbutton.pack(side='left')
        quantityname.pack(side='left', padx = 5)
        quantityname.pack_propagate(False)
        
        foodlist = ttk.Combobox(foodlistname, values=self.foods, textvariable = self.selectedFood, width=15, validate='key', validatecommand=self.fv)
        foodlist.pack(pady=5, padx=10)
    
        self.quantity = tk.StringVar()
        self.quantityField = tk.Entry(quantityname, width = 4, state='disabled', textvariable = self.quantity, validate='key', validatecommand=self.qv)
        self.quantityField.pack(side='left', pady=5, padx=5)
        self.servingunit = tk.StringVar()
        tk.Label(quantityname, textvariable=self.servingunit).pack(side='left', padx=5)
        self.selectedFood.trace('w', self.disableQuantityField)
        self.selectedFood.trace('w', self.regUnsavedChanges)
        self.quantity.trace('w', self.regUnsavedChanges)
        
    def regUnsavedChanges(self, *args):
        self.UnsavedChanges = True
        
    def disableQuantityField(self, *args):
        self.quantityField['state'] = 'disabled'
    
    def updateServingUnit(self):
        if self.selectedFood.get() not in self.foods:
            messagebox.showwarning('Invalid Entry!', 'Food does not exist in database.', parent=self.master)
            return
        self.servingunit.set(self.Cn.get_servingUnit(self.selectedFood.get()))
        self.quantityField['state']='normal'
    
    def createFunctionButton(self, name, textstr, buttonCommand):
        self.name = tk.Button(self.frameFooter, text=textstr,command=buttonCommand)
        self.name.pack(side='left', pady = 5)
		
    def makeButtons(self):
        tk.Label(self.frameFooter, text='   ').pack(side='left') #spacing
        self.createFunctionButton('EditButton',' Edit ', self.loadEntry)
        self.createFunctionButton('AddButton', ' Add  ', self.addEntry)
        self.createFunctionButton('UpdButton', 'Update', self.updateEntry)
        self.createFunctionButton('DelButton', 'Delete', self.deleteEntry)
        
        self.QuitButton = tk.Button(self.frameQuit, text='Quit and Return to Main Menu',command=self.quit)
        self.QuitButton.pack(pady = 5, fill='x')
    
    def whichSelected(self):
        if self.select.selection():
            return self.select.selection()[0]
        else:
            return 'Error'
    
    def loadEntry(self, *args):
        if self.whichSelected() == 'Error':
            messagebox.showwarning('Invalid Request', 'Please select an entry for editing first.', parent=self.master)
            return
        if self.UnsavedChanges:
            if not messagebox.askyesno('Unsaved Changes', 'If you proceed your changes will be lost. Do you still wish to proceed?', parent=self.master):
                return
        self.loadedEntry = self.whichSelected()
        sqldate = self.Cn.getLogDate(self.loadedEntry)
        year, month, day = self.tkcal.cal.sqlDateUnpack(sqldate)
        self.tkcal.selectYrMth(year, month)
        self.tkcal.selectdate(day)
        self.selectedFood.set(self.select.set(self.loadedEntry, 'Food'))
        self.updateServingUnit()
        qty = self.select.set(self.loadedEntry, 'Quantity').split(" ", 2)
        self.quantity.set(qty[0])
        self.UnsavedChanges = False
		
    def addEntry(self):
        year, month, day = self.getDate()
        if self.quantity.get() == '' or float(self.quantity.get()) == 0:
            messagebox.showwarning('Invalid Entry!', 'Quantity cannot be zero.', parent=self.master)
            return
        elif not self.tkcal.cal.isDateReal(year, month, day):
            messagebox.showwarning('Invalid Entry!', 'Date entered is invalid.', parent=self.master)
            return
        elif self.quantityField.config()['state'][4] == 'disabled':
            messagebox.showwarning('Invalid Entry!', 'Serving unit not updated to match food. Please press the > button.', parent=self.master)
            return
        self.Cn.do_addEntry(self.getSQLDate(year, month, day), self.selectedFood.get(), self.quantity.get())
        self.UnsavedChanges = False
        self.loadLog()
        self.tkcal.muteCheck()
        
    def updateEntry(self):
        year, month, day = self.getDate()
        if self.loadedEntry == None:
            messagebox.showwarning('Invalid Request', 'Please press the edit button or double click the entry you wish to edit first.', parent=self.master)
            return
        if self.quantity.get() == '' or float(self.quantity.get()) == 0:
            messagebox.showwarning('Invalid Entry!', 'Quantity cannot be zero.', parent=self.master)
            return
        elif not self.tkcal.cal.isDateReal(year, month, day):
            messagebox.showwarning('Invalid Entry!', 'Date entered is invalid.', parent=self.master)
            return
        elif self.quantityField.config()['state'][4] == 'disabled':
            messagebox.showwarning('Invalid Entry!', 'Serving unit not updated to match food. Please press the > button.', parent=self.master)
            return
        self.Cn.do_updEntry(self.getSQLDate(year, month, day), self.selectedFood.get(), self.quantity.get(), self.loadedEntry)
        self.UnsavedChanges = False
        self.loadLog()
        self.tkcal.muteCheck()
        
    def deleteEntry(self):
        if not self.whichSelected():
            messagebox.showwarning('Invalid Request', 'Please select an entry to delete first.', parent=self.master)
            return
        self.Cn.do_delEntry(self.whichSelected())
        self.loadLog()
        self.tkcal.muteCheck()

    def makeListbox(self):
        self.frameTable = tk.Frame(self.frameList)
        self.frameTable.pack(side='left', fill='both')
        cols = ['Food', 'Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Fruit', 'Veg', 'Quantity']
        self.scroll = tk.Scrollbar(self.frameList, orient='vertical')
        selectheader = DisplayTable(self.frameTable, cols, self.widths, True, 'none', rows=1) #header only
        self.select = DisplayTable(self.frameTable, cols, self.widths, False, 'browse', rows=8)
        self.select.config (yscrollcommand=self.scroll.set)
        self.scroll.config (command=self.select.yview)
        self.scroll.pack(side='right', fill='y')
        selectheader.pack(side='top')
        self.select.pack(side='bottom',  fill='both')
        self.select.bind("<Double-Button-1>", self.loadEntry)
    
    def makeDisplayTable(self):
        cols = ('Totals', 'Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Fruit', 'Vegetables')
        self.table = DisplayTable(self.frameRight, cols, self.widths[:-1], False, 'none', rows=1)
        self.table.pack(side='bottom', anchor='w')
    
    def getDate(self):
        year = int(self.tkcal.year.get())
        month = int(self.tkcal.month.get())
        day = int(self.tkcal.date.get())
        return year, month, day
        
    def getSQLDate(self, year, month, day):
        return self.tkcal.cal.sqlDateFormat(year, month, day)
    
    def loadLog(self):
        year, month, day = self.getDate()
        if self.tkcal.cal.isDateReal(year, month, day):
            sqldate = self.getSQLDate(year, month, day)
            self.log = DataLog(self.Cn.getDayData(sqldate))
            self.TotalsDisplayUpdate()
            self.piechart.refresh(self.macrototals)
            self.log.LMformat()
            self.ListboxDisplayUpdate()
        else:
            messagebox.showwarning('Invalid Entry!', 'The date entered is invalid.', parent=self.master)
		
    def ListboxDisplayUpdate(self, *args):
        for entry in self.select.get_entryRows():
            self.select.delete(entry)
        for entry in self.log:
            self.select.insert('', 'end', entry[9], values=entry)
            
    def TotalsDisplayUpdate(self):
        if self.table.exists('totals'):
            self.table.delete('totals')
        totals = self.log.getTotals()
        totals.combineVegData()
        self.macrototals = [totals[x] for x in range(2,5)]
        totals = totals.formatDisplay(2)
        totals = ['Totals'] + [totals[i] for i in range(1,8)]
        self.table.insert('', 0, 'totals', values=totals)

class WeeklyStats(SubWindow):
    def __init__(self, master, connection):
        SubWindow.__init__(self, master, connection, 'Weekly Statistics')
        self.WeekData = None
    
    def createFrames(self):
        self.frameTitle = tk.Frame(self.master)
        self.frameTitle.pack(side='top')
        self.frameCalendar = tk.Frame(self.master)
        self.frameCalendar.pack(padx=5, pady=5)
        self.frameNotebook = tk.Frame(self.master)
        self.frameNotebook.pack()
        self.frameQuit = tk.Frame(self.master)
        self.frameQuit.pack(side='bottom', fill='x')		
        
    def createWidgets(self):
        self.makeCalendar()
        self.makeNotebook()
        self.makeSummaryTab()
        self.makePercentageTab()
        self.makeDaybyDayTab()
        self.MakeQuitButton()
        
    def makeCalendar(self):
        self.tkcal = CalendarWidget(master=self.frameCalendar, connection=self.Cn, mode='week', responseFunction=self.loadData)
        self.tkcal.pack(expand=1, fill='both')
        
    def makeNotebook(self):
        self.nb = ttk.Notebook(self.frameNotebook, name='notebook')
        self.nb.enable_traversal()
        self.nb.pack(fill='both', padx=2, pady=3)
    
    def makeSummaryTab(self):
        self.frameSummary = tk.Frame(self.nb, name='summary')
        self.MakeDisplayTableRegular()
        self.MakeDisplayTableVeg()
        self.nb.add(self.frameSummary, text='Summary', underline=0, padding=2)
    
    def MakeDisplayTableRegular(self):
        tk.Label(self.frameSummary, text=' ').pack() #spacing
        tk.Label(self.frameSummary, text="Averages per Day", font=self.MinorTitleFont).pack()
        cols = ('Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Fruit')
        self.table = DisplayTable(self.frameSummary, cols, 75, True, 'none')
        self.table.pack(padx = 5, pady = 5)
		
    def MakeDisplayTableVeg(self):
        tk.Label(self.frameSummary, text=' ').pack() #spacing
        tk.Label(self.frameSummary, text="Vegetable Totals for Week", font=self.MinorTitleFont).pack()
        cols = ('Dark Green', 'Red & Orange', 'Beans & Lentils', 'Starchy', 'Other')
        self.tableV = DisplayTable(self.frameSummary, cols, 90, True, 'none')
        self.tableV.pack(padx = 5, pady = 5)
        
    def makePercentageTab(self):
        self.framePercentage = tk.Frame(self.nb, name='percentage')
        self.piechart = PieChart(self.framePercentage)
        self.piechart.pack()
        self.nb.add(self.framePercentage, text='CPF Breakdown', underline=4, padding=2)
        
    def makeDaybyDayTab(self):
        self.frameDaybyDay = tk.Frame(self.nb, name='daybyday')
        nutrients = ('Calories', 'Carbohydrate', 'Protein', 'Fat', 'Fiber', 'Fruits', 'Vegetables')
        self.selectedNutrient = tk.StringVar()
        nutlistname = ttk.Labelframe(self.frameDaybyDay, text='Nutrient')
        self.nutlist = ttk.Combobox(nutlistname, values=nutrients, state='readonly', textvariable=self.selectedNutrient, width=12)
        self.nutlist.current(0)
        nutlistname.pack(side='left', anchor='n', padx=10, pady=25)
        self.nutlist.pack(padx=5, pady=5)
        self.barchart = BarChart(self.selectedNutrient.get(), self.frameDaybyDay)
        self.barchart.pack(side='right')
        self.nb.add(self.frameDaybyDay, text='Day By Day', underline=0, padding=2)
        self.selectedNutrient.trace('w', self.refreshByNutrient)
    
    def loadData(self):
        year = int(self.tkcal.year.get())
        month = int(self.tkcal.month.get())
        day = int(self.tkcal.date.get())
        if not self.tkcal.cal.isDateReal(year, month, day):
            messagebox.showwarning('Invalid Entry!', 'Date entered is invalid.', parent=self.master)
            return
        self.startday = self.tkcal.cal.getWeekDay(year, month, day)
        self.WeekData = DataCollection()
        for date in self.tkcal.cal.createSQLDatesWeek(year, month, day):
            self.WeekData.append_data_log(self.Cn.getDayData(date))
        self.calculateData()
    
    def calculateNutrientTotals(self):
        self.nutrientTotals = self.WeekData.get_nutrient_totals(self.nutlist.current()+1)	

    def calculateData(self):
        averages = DataRow(self.WeekData.get_averages())
        averages = averages.formatDisplay(2)
        self.averages = [averages[i] for i in range(1,7)]
        totals = DataRow(self.WeekData.getCTotals())
        self.macrototals = [totals[x] for x in range(2,5)]
        totals = totals.formatDisplay(2)
        self.vegtotals = totals[7]
        self.calculateNutrientTotals()
        self.refreshTabs()
    
    def refreshTabs(self):
        self.refreshSummaryTab()
        self.piechart.refresh(self.macrototals)
        self.barchart.refreshDay(self.startday, self.nutrientTotals)
    
    def refreshByNutrient(self, *args):
        if self.WeekData == None:
            self.barchart.refreshTitle(self.selectedNutrient.get())
            return
        self.calculateNutrientTotals()
        self.barchart.refreshNutrient(self.selectedNutrient.get(), self.nutrientTotals)
    
    def refreshSummaryTab(self):
        if self.table.exists('averages'):
            self.table.delete('averages')
        self.table.insert('', 'end', 'averages', values=self.averages)
        
        if self.tableV.exists('totals'):
            self.tableV.delete('totals')
        self.tableV.insert('', 'end', 'totals', values=self.vegtotals)
    
    def MakeQuitButton(self):	
        self.QuitButton = tk.Button(self.frameQuit, text='Quit and Return to Main Menu',command=self.quit)
        self.QuitButton.pack(pady=5, padx=5, fill='x')

class MonthlyStats(SubWindow):
    def __init__(self, master, connection):
        SubWindow.__init__(self, master, connection, 'Monthly Statistics')
        self.selectedMonth.trace('w', self.loadData)
        self.selectedYear.trace('w', self.loadData)
    
    def createFrames(self):
        self.frameTitle = tk.Frame(self.master)
        self.frameTitle.pack(side='top')
        self.frameInput = tk.Frame(self.master)
        self.frameInput.pack(padx=5, pady=5)
        self.frameDisplay = tk.Frame(self.master)
        self.frameDisplay.pack()
        self.frameQuit = tk.Frame(self.master)
        self.frameQuit.pack(side='bottom', fill='x')
        
    def createWidgets(self):
        self.cal = Calendar()
        
        self.MakeMonthList()
        self.MakeYearList()
        self.MakeDisplayTable()
        self.MakePieChart()
        self.MakeQuitButton()
    
    def MakeMonthList(self):
        months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
        self.selectedMonth = tk.StringVar()
        monthlistname = ttk.Labelframe(self.frameInput, text='Month')
        monthlist = ttk.Combobox(monthlistname, values=months, state='readonly', textvariable = self.selectedMonth, width=10)
        monthlist.current(self.cal.date.month - 1)
        monthlistname.grid()
        monthlist.pack(pady=5, padx=10)
    
    def MakeYearList(self):
        years = [self.cal.date.year - x for x in range(0, self.cal.date.year - 2000)]
        self.selectedYear = tk.StringVar()
        yearlistname = ttk.Labelframe(self.frameInput, text='Year')
        yearlist = ttk.Combobox(yearlistname, values=years, state='readonly', textvariable = self.selectedYear, width=5)
        yearlist.current(0)
        yearlistname.grid(row=0, column=1)
        yearlist.pack(pady=5, padx=10)
	
    def loadData(self, *args):
        year, month = int(self.selectedYear.get()), self.cal.convertMonthNametoNumber(self.selectedMonth.get())
        self.MonthData = DataCollection()
        for date in self.cal.createSQLDatesMonth(year, month):
            self.MonthData.append_data_log(self.Cn.getDayData(date))
        self.displayData()
        
    def displayData(self): #
        if self.table.exists('averages'):
            self.table.delete('averages')
        averages = DataRow([self.MonthData.get_averages()[i] for i in range(1,8)])
        averages = averages.formatDisplay(2)
        self.table.insert('', 'end', 'averages', values=averages)
        totals = DataRow(self.MonthData.getCTotals())
        self.macrototals = [totals[x] for x in range(2,5)]
        self.piechart.refresh(self.macrototals)
        totals = totals.formatDisplay(2)
        
    def MakePieChart(self):
        self.piechart = PieChart(self.frameDisplay)
        self.piechart.pack(side='top')
        
    def MakeDisplayTable(self):
        tk.Label(self.frameDisplay, text=" ").pack(side='bottom') #spacing
        cols = ('Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Fruit')
        self.table = DisplayTable(self.frameDisplay, cols, 50, True, 'none')
        self.table.pack(side='bottom', padx=5)
        tk.Label(self.frameDisplay, text="Averages per Day", font=self.MinorTitleFont).pack(side='bottom', pady=5)
        
    def MakeQuitButton(self):	
        self.QuitButton = tk.Button(self.frameQuit, text='Quit and Return to Main Menu',command=self.quit)
        self.QuitButton.pack(pady=5, padx=5, fill='x')

def main():
    root.withdraw()
    root.title("Food Diary")
    app.title("Food Diary")
    app.mainloop()
    return None

root = tk.Tk()
app = Application(master=root)
main()