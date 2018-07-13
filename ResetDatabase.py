"""Creates a new database. 
Running this will delete existing database including all data.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from schema import *

class Application(tk.Toplevel):
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self.withdraw()
        self.frame = tk.Frame(self)
        self.frame.pack(pady=10)
        self.createLabel()
        self.createProgressBar()
        self.center()
        if messagebox.askyesno('Reset Database', 'This will reset the database, or create a new database if none exists. All existing data will be deleted. Continue?'):
            self.resetDatabase()

    def center(self): #center app window on screen
        self.update()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        winsize = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = w/2 - winsize[0]/2
        y = h/2 - winsize[1]/2
        self.geometry("%dx%d+%d+%d" % (winsize + (x, y)))
        self.deiconify()
		
    def createLabel(self):
        self.labeltext = tk.StringVar()
        tk.Label(self.frame, text='', textvariable=self.labeltext).pack(side='top', anchor='w', padx=10)
        self.labeltext.set('Awaiting confirmation...')
		
    def createProgressBar(self): #create a bar to display progress
        self.progress = tk.IntVar()
        progressbar = ttk.Progressbar(self.frame, orient='horizontal', length=200, mode='determinate', value=0, variable=self.progress)
        progressbar.pack(padx=10)
		
    def resetDatabase(self): #perform the database reset
        self.openConnection()
        self.delTables()
        self.createTables()
        self.close()
		
    def openConnection(self): #open database
        self.conn = sqlite3.connect('food.db')
        self.cursor = self.conn.cursor()
        self.labeltext.set('Opening database...')
        self.progress.set(10)
	
    def delTables(self): #delete existing tables from database
        self.cursor.execute('DROP TABLE IF EXISTS INGREDIENT')
        self.labeltext.set('Deleting food table...')
        self.progress.set(30)
        self.cursor.execute('DROP TABLE IF EXISTS LOG')
        self.labeltext.set('Deleting log table...')
        self.progress.set(50)

    def createTables(self): #create new tables according to schema
        self.cursor.execute('CREATE TABLE {}'.format(ingredientSchema))
        self.labeltext.set('Creating food table...')
        self.progress.set(70)
        self.cursor.execute('CREATE TABLE {}'.format(foodlogSchema))
        self.labeltext.set('Creating log table...')
        self.progress.set(90)

    def close(self): #close database and update display to show completion
        self.conn.commit()
        self.conn.close()
        self.labeltext.set('Reset complete.')
        self.progress.set(100)
        buttonframe = tk.Frame(self.frame)
        buttonframe.pack(side='bottom')
        okbutton = tk.Button(buttonframe, text='OK', command=self.quit)
        okbutton.pack(side='bottom', pady = 10)
		
    def quit(self):
        root.destroy()
		
def main():
    root.withdraw()
    root.wm_title("Reset Database")
    app.mainloop()
    return True

root = tk.Tk()
app = Application(master=root)
main()