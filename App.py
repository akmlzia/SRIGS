#Module Import
import sqlite3
import tkinter as tk
from os.path import exists
from initiate_db import initiate_db
from tkinter import ttk
import pandas as pd
import pickle
import webbrowser

#For insert and get deck and progress DataFrame
sqlite3.register_converter("pickle", pickle.loads)
sqlite3.register_adapter(pd.DataFrame, pickle.dumps)

class WelcomeFrame(ttk.Frame):
    def __init__(self, container, connection):
        super().__init__(container)

        #fetch all student
        self.connection = connection
        self.welcome_cursor = self.connection.cursor()
        self.welcome_cursor.execute("SELECT * FROM students;")
        self.students_list = self.welcome_cursor.fetchall()
        self.students_list = {self.students_list[i][2]: self.students_list[i] for i in range(len(self.students_list))}

        #Initiate container variable for enter WelcomeFrame
        self.container = container

        #Label Instruction
        self.choose_instruction = ttk.Label(self, text="Pilih Siswa:")
        self.choose_instruction.pack(pady=10)

        #Choose Student ComboBox
        self.person_combobox = ttk.Combobox(self, state='readonly')
        self.person_combobox.pack()

        #ComboBox Inside
        self.person_combobox['values'] = [full_name for full_name in self.students_list.keys()]
        self.person_combobox.bind('<<ComboboxSelected>>', self.change_welcome_button_state)

        #button frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10)
        
        #Choose Student Button
        self.choose_person_button_nd = ttk.Button(self.button_frame, text="Mulai Sesi Baru", 
                                                  command=lambda: self.move2deck(self.students_list[self.person_combobox.get()], True))
        self.choose_person_button_nd.pack()
        self.choose_person_button_nd["state"] = "disabled"
        self.choose_person_button_od = ttk.Button(self.button_frame, text="Mulai Sesi Lama", 
                                                  command=lambda: self.move2deck(self.students_list[self.person_combobox.get()], False))
        self.choose_person_button_od.pack(pady=5)
        self.choose_person_button_od["state"] = "disabled"
        
        #Pack frame to window
        self.pack(expand=True) 
    
    #Change button when combobox item selected function
    def change_welcome_button_state(self, event):
        if self.person_combobox.get():
            self.choose_person_button_nd["state"] = "normal"
            self.choose_person_button_od["state"] = "normal"
        else:
            self.choose_person_button_nd["state"] = "disabled"
            self.choose_person_button_od["state"] = "disabled"

    #Frame change (Welcome -> Deck) function
    def move2deck(self, student_tuple, decrease_days):
        self.destroy()
        DeckFrame(self.container, student_tuple, decrease_days, self.connection)

class DeckFrame(ttk.Frame):
    def __init__(self, container, student_tuple, decrease_days, connection):
        super().__init__(container)

        self.student_tuple = student_tuple
        # student_tuple = (id, nick_name, full_name, group_name, join_date)
        self.progress_list = []

        #fetch all student's deck
        self.connection = connection
        #self.deck_cursor = connection.cursor()
        #self.deck_cursor.execute("COMMAND")
        #self.deck_list = self.deck_cursor.fetchall()

        #Initiate container variable for enter DeckFrame
        self.container = container

        #Label Instruction
        self.greet = ttk.Label(self, text="Hi {}!".format(self.student_tuple[1]))
        self.greet.pack(pady=10)
        
        #Label Instruction
        self.choose_instruction = ttk.Label(self, text="Pilih Deck:")
        self.choose_instruction.pack(pady=10)

        #Treeview Frame (TreeView and NoProgress Label inside)
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(pady=10, expand=True, fill='both')
        
        #No Deck Warn Label
        self.nodeck_warn_label = ttk.Label(self.tree_frame, text="Siswa ini belum mendaftar sebuah deck.")
        self.nodeck_warn_label.grid(column=0,row=0)
        
        #Deck Treeview
        self.columns = ("deck_name", "status")
        self.deck_tree = ttk.Treeview(self.tree_frame, columns=self.columns, show='headings')
        self.deck_tree.heading("deck_name", text="Nama Deck")
        self.deck_tree.heading("status", text="Status")
        self.deck_tree.grid(column=0,row=0)
        self.deck_tree.bind('<Button-1>', self.handle_manual_column_resize)
        self.deck_tree.bind('<Motion>', self.handle_manual_column_resize)

        self.raise_nodeck_label(self.progress_list)

        #Button Frame
        self.deck_button_frame = ttk.Frame(self)
        self.deck_button_frame.pack(pady=10)

        #Choose Deck Button
        self.choose_deck_button = ttk.Button(self.deck_button_frame, text="Mulai Sesi")#, command=lambda: self.start_session(self.deck_combobox.get()))
        self.choose_deck_button.pack(padx=10, pady=10, side='right')

        #Enroll New Deck Button
        self.enroll_deck_button = ttk.Button(self.deck_button_frame, text="Daftar Deck", command=lambda: self.open_DeckEnrollWindow())
            #make new window (deck enroller) with toplevel and focus on that window
        self.enroll_deck_button.pack(pady=10, side='left')
        
        #Pack frame to window
        self.pack(expand=True)

    #Show no deck label function
    def raise_nodeck_label(self, progress_bool):
        if progress_bool:
            self.nodeck_warn_label.grid_remove()
        else:
            self.deck_tree.grid_remove()

    #Open DeckEnrollWindow function
    def open_DeckEnrollWindow(self):
        window = DeckEnrollWindow(self.container, self.connection)
        window.grab_set()
    
    #Disable manual column resizing function
    def handle_manual_column_resize(self, event):
        if self.deck_tree.identify_region(event.x, event.y) == "separator":
            return "break"
    
    #Frame change (Deck -> Session) function
    #def start_session(self):
    #    self.destroy()
    #    SessionFrame(self.container)

class DeckEnrollWindow(tk.Toplevel):
    def __init__(self, container, connection):
        super().__init__(container)

        #Window setting
        self.title('Enroll a Deck')
        self.geometry('200x200')
        self.resizable(False, False)

        #Window Frame
        self.WindowFrame = ttk.Frame(self)

        #Label Instruction
        self.choose_instruction = ttk.Label(self.WindowFrame, text="Pilih Deck:")
        self.choose_instruction.pack()

        #Choose New Deck ComboBox
        self.new_deck_combobox = ttk.Combobox(self.WindowFrame, state='readonly')
        self.new_deck_combobox.pack()

        #ComboBox Inside
        self.new_deck_combobox['values'] = ['A', 'B']
        self.new_deck_combobox.bind('<<ComboboxSelected>>', self.change_deck_enroll_button_state)
        
        #Choose New Deck Button
        self.choose_new_deck_button = ttk.Button(self.WindowFrame, text="Daftar Deck")#, 
                                                  #command=lambda: self.move2deck(self.students_list[self.person_combobox.get()], True, self.connection))
        self.choose_new_deck_button.pack(pady=10)
        self.choose_new_deck_button["state"] = "disabled"

        #expand window to get widget centered
        self.WindowFrame.pack(expand=True)

    #Change button when combobox item selected function
    def change_deck_enroll_button_state(self, event):
        if self.new_deck_combobox.get():
            self.choose_new_deck_button["state"] = "normal"
        else:
            self.choose_new_deck_button["state"] = "disabled"

class SessionFrame(ttk.Frame):
    def __init__(self, container, connection):
        super().__init__(container)

        self.student_tuple = student_tuple
        # student_tuple = (id, nick_name, full_name, group_name, join_date)

        #fetch all student's deck name
        #self.deck_cursor = connection.cursor()
        #self.deck_cursor.execute("COMMAND")
        #self.deck_list = self.deck_cursor.fetchall()

        #Initiate container variable for enter DeckFrame
        self.container = container

        #Label Instruction
        self.greet = ttk.Label(self, text="Hi {}!".format(self.student_tuple[1]))
        self.greet.pack(pady=10)
        
        #Label Instruction
        self.choose_instruction = ttk.Label(self, text="Pilih Deck:")
        self.choose_instruction.pack(pady=10)

        #Deck Treeview
        self.columns = ("deck_name", "status")
        self.deck_tree = ttk.Treeview(self, columns=self.columns, show='headings')
        self.deck_tree.heading("deck_name", text="Nama Deck")
        self.deck_tree.heading("status", text="Status")
        self.deck_tree.pack(pady=10, expand=True)
        self.deck_tree.bind('<Button-1>', self.handle_manual_column_resize)
        self.deck_tree.bind('<Motion>', self.handle_manual_column_resize)

        #Choose Deck Button
        self.choose_deck_button = ttk.Button(self, text="Mulai Sesi")#, command=lambda: self.start_session(self.deck_combobox.get()))
        self.choose_deck_button.pack(pady=10)
        
        #Pack frame to window
        self.pack(expand=True)
    
    #Frame change (Welcome -> Deck) function
    #def start_session(self, student_tuple, decrease_days):
    #    self.destroy()
    #    DeckFrame(self.container, student_tuple, decrease_days)

class AboutWindow(tk.Toplevel):
    def __init__(self, container):
        super().__init__(container)

        #Window setting
        self.title('About')
        self.geometry('500x300')
        self.resizable(False, False)

        #Window Frame
        self.AboutFrame = ttk.Frame(self)

        #App Logo
        self.photo = tk.PhotoImage(file='./assets/logo_50.png')
        self.app_logo = ttk.Label(self.AboutFrame, image=self.photo, padding=5)
        self.app_logo.pack(pady=10)

        self.app_name = ttk.Label(self.AboutFrame, text='SRIGS', font=('bold', 20))
        self.app_name.pack()
        
        self.app_name2 = ttk.Label(self.AboutFrame, text='Spaced Repetition In Group Software')
        self.app_name2.pack()

        self.app_desc = ttk.Label(self.AboutFrame, text='SRIGS is a spaced repetition deck manager for group/school use.')
        self.app_desc.pack(pady=10)
        
        self.author = ttk.Label(self.AboutFrame, text='SRIGS by N. Zia Akmal, 2021')
        self.author.pack()
        
        self.github = ttk.Label(self.AboutFrame, text='go to github repo', foreground='blue')
        self.github.pack(pady=10)
        self.github.bind("<Button-1>", lambda e: self.callback("https://github.com/akmlzia/SRIGS"))

        #expand window to get widget centered
        self.AboutFrame.pack(expand=True)
    
    def callback(self, url):
        webbrowser.open_new_tab(url)

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        #Window setting
        self.title('SRIG4SA')
        self.geometry('400x400')
        self.resizable(False, False)
        self.iconphoto(True, tk.PhotoImage(file='./assets/logo.png'))

        #Menu
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        self.menu.add_command(label='About', command=lambda:self.open_AboutWindow())

    #Open DeckEnrollWindow function
    def open_AboutWindow(self):
        window = AboutWindow(self)
        window.grab_set()

if __name__ == "__main__":
    if not exists('data.db'):
        initiate_db()
    connection = sqlite3.connect('data.db')
    app = App()
    WelcomeFrame(app, connection)
    app.mainloop()
    connection.close()