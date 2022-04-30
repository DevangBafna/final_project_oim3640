from cProfile import label
import datetime
from tkinter import *
import tkinter.messagebox as mb
from tkinter import ttk
from tkcalendar import DateEntry  # pip install tkcalendar
import sqlite3
import urllib.request
import json
from config import API_KEY
import pandas_datareader as pdr
from matplotlib import pyplot as plt
import yfinance as yf
from matplotlib import rcParams
from datetime import datetime
from collections import defaultdict
from urllib.error import HTTPError
from PIL import Image

# Database connection
connector = sqlite3.connect('ExpenseTracker.db')
cursor = connector.cursor()

# Create table in database
connector.execute(
"CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT, password TEXT, budget REAL, location TEXT)")

connector.execute(
"CREATE TABLE IF NOT EXISTS expenses (expense_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, description TEXT, amount REAL, category TEXT, date TEXT, location TEXT)")

# Inserting a dummy user for other users to login and after login they can change their details
connector.execute('INSERT INTO users (username, password, budget, location) VALUES (?,?,?,?)', ('testuser', 'testpassword', 500, 'Wellesley'))

connector.commit()

# Creating the universal font variables
headerfont = ("Noto Sans CJK TC", 15, 'bold')
labelfont = ('Garamond', 14)
entryfont = ('Garamond', 12)

# All functions

# Get current temperature
def get_current_temp(city):
    """Returns current temperature in Celsius in your hometown
     from api.openweathermap.org
    Notice: the temperature returned from the API is in Kelvin.
    Below is the conversion formula form Kelvin to Celsius:
    T(°C) = T(°K) - 273.15"""

    APIKEY = API_KEY
    country_code = 'us'
    city_for_result = city.replace(' ', '%20')
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_for_result},{country_code}&APPID={APIKEY}'
    f = urllib.request.urlopen(url)
    response_text = f.read().decode('utf-8')
    response_data = json.loads(response_text)
    temp_k = (response_data['main']['temp'])
    temp_c = round(temp_k - 273.15,2)
    temp_f = round((temp_c * (9/5)) + 32,2)
    return(f'{temp_c} °C',f'{temp_f} °F')

# Get current location
def get_current_location():
    '''Return current location from the database for the user'''

    current_location = connector.execute('SELECT location FROM users').fetchall()
    return current_location[0][0]

# Get current stock price
def get_stock_price(symbol):
    '''Return the closing stock price of the ticker the user has inputed'''
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return todays_data['Close'][0]

# Show stock price as graph
def show_stock_price():
    '''Show the stock price of the ticker the user has inputed over the past 5 years in a plot'''
    global ticker_entry
    symbol = ticker_entry.get().upper()
    if not symbol:
        mb.showerror('Error!', "Please fill in a ticker!")
        reset_fields()
    else:
        try:
            data = pdr.get_data_yahoo(symbol,start = '2017-01-01')['Close']
            rcParams['figure.figsize'] = 12,6
            plt.plot(data)
            plt.grid(True)
            plt.title('Stock Price (USD) 2017-Present')
            plt.legend([symbol])
            rcParams['legend.loc'] = 'best'
            plt.xlabel('Date')
            plt.ylabel('Stock Price')
            mb.showinfo('Stock Price', f'Latest Closing Price for {symbol} is ${round(get_stock_price(symbol),2)}')
            plt.show()
            reset_fields()
        except:
            mb.showerror('Error!', "Please enter a valid ticker")
            reset_fields()

# Bitcoin price as graph
def show_bitcoin_price():
    '''Show the bitcoin price over the past 6 months in a plot'''
    data = yf.download(tickers='BTC-USD', period = '6mo', interval = '1d')
    data.reset_index(inplace = True)
    data = data.drop(['Open', 'High', 'Low','Adj Close', 'Volume'], axis=1)
    rcParams['figure.figsize'] = 12,6
    plt.plot(data['Date'],data['Close'])
    plt.grid(True)
    plt.title('Bitcoin Prices (USD) Last 6 Months')
    plt.legend(['BTC'])
    rcParams['legend.loc'] = 'best'
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()

# Expenditure by category graph
def show_categorical_expense():
    '''Show the user's expenses in a pie chart which is sorted by category'''
    data = connector.execute('SELECT category, amount from expenses').fetchall()
    sum_restaurant = 0
    sum_home = 0
    sum_transport = 0
    sum_shopping = 0
    sum_entertainment = 0
    sum_miscell = 0
    sum_total = 0
    for i in data:
        sum_total = sum_total + i[1]
        if i[0] == 'Restaurants & Dining':
            sum_restaurant = sum_restaurant + i[1]
        elif i[0] == 'Home & Utilities':
            sum_home = sum_home + i[1]
        elif i[0] == 'Transportation':
            sum_transport = sum_transport + i[1]
        elif i[0] == 'Shopping':
            sum_shopping = sum_shopping + i[1]
        elif i[0] == 'Entertainment':
            sum_entertainment = sum_entertainment + i[1]
        else:
            sum_miscell = sum_miscell + i[1]
    pie_labels = []
    data_graph = []
    data_dict = {'Restaurants & Dining': sum_restaurant, 'Home & Utilities': sum_home, 'Transportation': sum_transport, 'Shopping': sum_shopping, 'Entertainment':sum_entertainment, 'Miscellaneous':sum_miscell }
    for i,j in data_dict.items():
        if j != 0:
            pie_labels.append(i)
            data_graph.append(j)
    rcParams['figure.figsize'] = 10,6
    plt.pie(data_graph, labels = pie_labels, autopct='%1.1f%%', startangle = 90, shadow = True)
    plt.grid(True)
    plt.title('Your Spending by Category (USD)')
    plt.legend(loc='best', title = 'Categories')
    rcParams['legend.loc'] = 'upper left'
    plt.show() 

# Expenditure by month graph
def monthly_spending():
    '''Show the user's spending in a bar plot sorted by monthly expenditure'''
    data = connector.execute('SELECT date, amount from expenses').fetchall()
    data_list = [list(ele) for ele in data] 
    #https://www.geeksforgeeks.org/python-convert-list-of-tuples-to-list-of-list/

    for i in range(len(data_list)):
        data_list[i][0] = datetime.strptime(data_list[i][0], '%Y-%m-%d').date()
    d = defaultdict(int)
    for date, val in data_list:
        d[date.strftime('%Y-%m')] += val
    #https://stackoverflow.com/questions/51863147/total-sum-amount-per-month-using-date-time-in-python

    res = list(map(list, d.items()))
    monthly_dict = {}
    for i in res:
        monthly_dict[i[0]] = i[1]
    sort_keys = monthly_dict.items()
    sorted_monthly_dict = dict(sorted(sort_keys))
    #https://pythonguides.com/python-dictionary-sort/#:~:text=To%20sort%20dictionary%20key%20in,key%2Dvalue%20pairs%20of%20dictionaries.

    x_values = sorted_monthly_dict.keys()
    y_values = sorted_monthly_dict.values()
    y_values_list = list(y_values)

    rcParams['figure.figsize'] = 10,6
    plt.bar(x_values, y_values)
    plt.title('Your Monthly Spending (USD)')
    plt.xlabel('Year-Month')
    plt.ylabel('Spending')
    # fix tomorrow
    for index, value in enumerate(y_values_list):
        plt.text(value, 1, str())
    plt.show()

# Update details
def update_details():
    '''Update the user details such as their username, password, budget and their current location'''
    global new_username_entry, new_password_entry, new_budget_entry, new_location_entry

    new_username = new_username_entry.get()
    new_password = new_password_entry.get()
    new_budget = new_budget_entry.get()
    new_location = new_location_entry.get()

    if not new_username and not new_password and not new_budget and not new_location:
        mb.showerror('Error!', "Please fill 1 of the missing fields!")
    elif not new_password and not new_budget and not new_location:
            connector.execute('UPDATE users SET username = ? WHERE user_id = 1', [new_username])
            connector.commit()
            mb.showinfo('Done!', 'Username was successfully updated')
            reset_fields()
            display_records_table()

    elif not new_username and not new_budget and not new_location:
            connector.execute('UPDATE users SET password = ? WHERE user_id = 1', [new_password])
            connector.commit()
            mb.showinfo('Done!', 'Password was successfully updated')
            reset_fields()
            display_records_table()

    elif not new_username and not new_password and not new_location:
            if new_budget.isdigit() == True:
                connector.execute('UPDATE users SET budget = ? WHERE user_id = 1', [new_budget])
                connector.commit()
                mb.showinfo('Done!', 'Budget was successfully updated')
                reset_fields()
                update_budget_label()
                display_records_table()
            else:
                mb.showerror('Error!','Only whole numbers are allowed. Please try again!')
                reset_fields()

    elif not new_username and not new_password and not new_budget:
            connector.execute('UPDATE users SET location = ? WHERE user_id = 1', [new_location])
            connector.commit()
            mb.showinfo('Done!', 'Location was successfully updated')
            reset_fields()
            update_location_label()
            display_records_table()
            
    elif new_username and new_password and not new_budget and not new_location :
                connector.execute('UPDATE users SET username = ? WHERE user_id = 1', [new_username])
                connector.execute('UPDATE users SET password = ? WHERE user_id = 1', [new_password])
                connector.commit()
                mb.showinfo('Done!', 'All details were successfully updated')
                reset_fields()
                display_records_table()
    
    elif new_username and new_budget and not new_password and not new_location :
        if new_budget.isdigit():
                connector.execute('UPDATE users SET username = ? WHERE user_id = 1', [new_username])
                connector.execute('UPDATE users SET budget = ? WHERE user_id = 1', [new_budget])
                connector.commit()
                mb.showinfo('Done!', 'All details were successfully updated')
                reset_fields()
                update_budget_label()
                display_records_table()
        else:
            mb.showerror('Error!','Only whole numbers are allowed. Please try again!')
            reset_fields()

    elif new_username and new_location and not new_budget and not new_password:
                connector.execute('UPDATE users SET username = ? WHERE user_id = 1', [new_username])
                connector.execute('UPDATE users SET location = ? WHERE user_id = 1', [new_location])
                connector.commit()
                mb.showinfo('Done!', 'All details were successfully updated')
                reset_fields()
                update_location_label()
                display_records_table()

    elif new_password and new_budget and not new_username and not new_location:
        if new_budget.isdigit():
                connector.execute('UPDATE users SET username = ? WHERE user_id = 1', [new_username])
                connector.execute('UPDATE users SET password = ? WHERE user_id = 1', [new_password])
                connector.execute('UPDATE users SET budget = ? WHERE user_id = 1', [new_budget])
                connector.execute('UPDATE users SET location = ? WHERE user_id = 1', [new_location])
                connector.commit()
                mb.showinfo('Done!', 'All details were successfully updated')
                reset_fields()
                update_budget_label()
                display_records_table()
        else:
            mb.showerror('Error!','Only whole numbers are allowed. Please try again!')
            reset_fields()

    elif new_password and new_location and not new_budget and not new_username:
                connector.execute('UPDATE users SET password = ? WHERE user_id = 1', [new_password])
                connector.execute('UPDATE users SET location = ? WHERE user_id = 1', [new_location])
                connector.commit()
                mb.showinfo('Done!', 'All details were successfully updated')
                reset_fields()
                update_location_label()
                display_records_table()

    elif new_budget and new_location and not new_password and not new_username:
        if new_budget.isdigit():
                connector.execute('UPDATE users SET budget = ? WHERE user_id = 1', [new_budget])
                connector.execute('UPDATE users SET location = ? WHERE user_id = 1', [new_location])
                connector.commit()
                mb.showinfo('Done!', 'All details were successfully updated')
                reset_fields()
                update_budget_label()
                update_location_label()
                display_records_table()
        else:
            mb.showerror('Error!','Only whole numbers are allowed. Please try again!')
            reset_fields()

    elif new_username and new_password and new_budget and new_location:
        if new_budget.isdigit():
                connector.execute('UPDATE users SET username = ? WHERE user_id = 1', [new_username])
                connector.execute('UPDATE users SET password = ? WHERE user_id = 1', [new_password])
                connector.execute('UPDATE users SET budget = ? WHERE user_id = 1', [new_budget])
                connector.execute('UPDATE users SET location = ? WHERE user_id = 1', [new_location])
                connector.commit()
                mb.showinfo('Done!', 'All details were successfully updated')
                reset_fields()
                update_budget_label()
                update_location_label()
                display_records_table()
        else:
            mb.showerror('Error!','Only whole numbers are allowed. Please try again!')
            reset_fields()
            
# Logout
def logout():
    '''Quit the program after clicking logout button'''
    frame.destroy()

# Reset fields
def reset_fields():
    '''Reset the fields after buttons are clicked so user can input another record'''
    try:
        global description_entry, category_entry, amount_entry, date_entry, location_entry, ticker_entry, new_username_entry, new_password_entry, new_location_entry, new_budget_entry

        for i in ['description_entry', 'amount_entry', 'category_entry', 'location_entry','ticker_entry', 'new_username_entry', 'new_password_entry', 'new_budget_entry', 'new_location_entry']:
            exec(f"{i}.set('')")
        date_entry.set_date(datetime.datetime.now().date())
    except Exception:
        pass

# Show labels, textbox after logging in
def show_frame_after_login():
        '''Shows all the features after the user has logged in and hides the login features'''
        username_textbox.place_forget()
        password_textbox.place_forget()
        username_label.place_forget()
        password_label.place_forget()
        login_button.place_forget()

        title_table_label.pack(side=TOP, fill=X)
        X_scroller.pack(side=BOTTOM, fill=X)
        Y_scroller.pack(side=RIGHT, fill=Y)
        tree.place(y=25, relwidth=1, relheight=0.8, relx=0)
        display_records_table()

        description_label.place(relx=0.5, rely=0.05, anchor=CENTER)
        description_textbox.place(relx=0.5, rely=0.1, anchor=CENTER)
        amount_label.place(relx=0.5, rely=0.15, anchor=CENTER)
        amount_textbox.place(relx=0.5, rely=0.20, anchor=CENTER)
        location_label.place(relx=0.5, rely=0.25, anchor=CENTER)
        location_textbox.place(relx=0.5, rely=0.30, anchor=CENTER)
        category_label.place(relx=0.5, rely=0.35, anchor=CENTER)
        category_optionbox.place(relx=0.5, rely=0.4, relwidth=0.5, anchor=CENTER)
        date_label.place(relx=0.5, rely=0.46, anchor=CENTER)
        date_entry.place(relx=0.5, rely=0.51, anchor=CENTER)
        addexpense_button.place(relx=0.5, rely=0.61, anchor=CENTER)
        delete_expense_button.place(relx=0.5, rely=0.71, anchor=CENTER)

        temperature_label.place(relx=0.5 , rely=0.88, anchor=CENTER)
        temperature_location_label.place(relx=0.5 , rely=0.92, anchor=CENTER)

        ticker_label.place(relx=0.5 , rely=0.55, anchor=CENTER)
        ticker_textbox.place(relx=0.5 , rely=0.6, anchor=CENTER)
        view_stock_button.place(relx=0.5 , rely=0.65, anchor=CENTER)
        view_bitcoin_button.place(relx=0.5 , rely=0.7, anchor=CENTER)
        category_expense_button.place(relx=0.5 , rely=0.75, anchor=CENTER)
        monthly_spending_button.place(relx=0.5, rely=0.8, anchor=CENTER)
        username_change_label.place(relx=0.5, rely=0.05, anchor=CENTER)
        username_change_textbox.place(relx=0.5, rely=0.1, anchor=CENTER)
        password_change_label.place(relx=0.5, rely=0.15, anchor=CENTER)
        password_change_textbox.place(relx=0.5, rely=0.2, anchor=CENTER)
        budget_change_label.place(relx=0.5, rely=0.25, anchor=CENTER)
        budget_change_textbox.place(relx=0.5, rely=0.3, anchor=CENTER)
        location_change_label.place(relx=0.5, rely=0.35, anchor=CENTER)
        location_change_textbox.place(relx=0.5, rely=0.4, anchor=CENTER)
        update_details_button.place(relx=0.5, rely=0.47, anchor=CENTER)
        logout_button.place(relx=0.5, rely=0.9, anchor=CENTER)

        budget_label.place(relx=0.5, rely = 0.88, anchor=CENTER)
        over_under_label.place(relx=0.5, rely = 0.92, anchor=CENTER)

        update_budget_label()

# Update location after update button
def update_location_label():
    '''This function will update the display of location and temperature after the user has updated their current location'''
    try:
        current_location = connector.execute('SELECT location FROM users').fetchall()
        current_temperature_c = get_current_temp(current_location[0][0])[0]
        current_temperature_f = get_current_temp(current_location[0][0])[1]
        temperature_label['text'] = f'Current Temp: {current_temperature_c}, {current_temperature_f}'
        temperature_location_label['text'] = f"Current Location: {get_current_location()}"
    except HTTPError:
        mb.showerror('Error!', 'Please update location to a valid location!')

# Update budget after update button
def update_budget_label():
    '''This function will update the display of budget after the user has updated their current budget'''
    current_budget = connector.execute('SELECT budget FROM users').fetchall()
    current_budget = current_budget[0][0]
    current_budget = connector.execute('SELECT budget FROM users').fetchall()
    current_budget = current_budget[0][0]
    total_spending = connector.execute('SELECT SUM(amount) FROM expenses').fetchall()
    budget_label['text'] = f'Current Budget: ${current_budget}, Total Spending: ${total_spending[0][0]}'

    if total_spending[0][0] == None:
        over_under_label.config(foreground='Black')
        over_under_label['text'] = 'Over or Under Budget?'
    elif current_budget > total_spending[0][0]:
        over_under_label.config(foreground='DarkGreen')
        over_under_label['text'] = 'Under Budget'
    elif current_budget < total_spending[0][0]:
        over_under_label.config(foreground='Red')
        over_under_label['text'] = 'Over Budget'
    else:
        over_under_label.config(foreground='Black')
        over_under_label['text'] = 'Break Even'

# Check login details
def check_details():
    '''This function will check the username and password when the user tries to log in'''
    global username_entry, password_entry
    
    username_from_database = connector.execute('SELECT username FROM users').fetchall()
    password_from_database = connector.execute('SELECT password FROM users').fetchall()

    if username_entry.get() == username_from_database[0][0] and password_entry.get() == password_from_database[0][0]:
        mb.showinfo('Login', 'Your login was successful!')
        show_frame_after_login()
        
    else:
        mb.showerror('Error!', "Incorrect login details, try again!")
        reset_fields()

# Display records 
def display_records():
    '''This function will display records from the users table'''
    curr = connector.execute('SELECT * FROM users')
    data = curr.fetchall()

    for records in data:
        print(records)

# Display records in the table
def display_records_table():
    '''This function will display records from the expenses table into the expense records table for the user'''
    tree.delete(*tree.get_children())

    curr = connector.execute('SELECT description, amount, category, date, location FROM expenses')
    data = curr.fetchall()

    for records in data:
        tree.insert('', END, values=records)

# Remove record from the table
def remove_record():
    '''This function will remove a record from the table once the user has clicked which one to remove and after clicking delete expense button'''
    if not tree.selection():
        mb.showerror('Error!', 'Please select an item from the expense table')
    else:
        current_item = tree.focus()
        values = tree.item(current_item)
        selection = values["values"]

        tree.delete(current_item)

        connector.execute('DELETE FROM expenses WHERE description= ?', [selection[0]])
        connector.commit()

        mb.showinfo('Done!', 'The record was successfully deleted!')

        update_budget_label()
        display_records_table()

# Add expenses to the table
def add_expense():
    '''This function will add a record into the expenses table after the user has clicked the add expense button'''
    global description_entry, category_entry, amount_entry, date_entry, location_entry

    description = description_entry.get()
    amount = amount_entry.get()
    category = category_entry.get()
    date = date_entry.get_date()
    location = location_entry.get()

    if not description or not amount or not category or not date or not location:
        mb.showerror('Error!', "Please fill all the missing fields!")
    else:
        if amount.isdigit() == True:
            try:
                connector.execute(
                'INSERT INTO expenses (description, amount, category, date, location) VALUES (?,?,?,?,?)', (description, amount, category, date, location))
                connector.commit()
                mb.showinfo('Done!', 'Expense was successfully added')
                reset_fields()
                update_budget_label()
                display_records_table()
            except:
                mb.showerror('Error!','The type of the values entered is not accurate. Please try again!')
                reset_fields()
        else:
            mb.showerror('Error!','Only whole numbers are allowed. Please try again!')
            reset_fields()

# Initializing the GUI window
frame = Tk()
frame.title('Budget and Expense Tracker')
frame.geometry('1425x870')
frame.resizable(True, True)
frame.state("zoomed")

# title label
title_label = Label(frame, text="EASY BUDGET", font=headerfont, bg='DodgerBlue')
title_label.pack(side=TOP, fill=X)

# left frame
left_frame = Frame(frame, bg='SkyBlue2')
left_frame.place(x=0, y=30, relheight=1, relwidth=0.2)

# center frame 
center_frame = Frame(frame, bg="SkyBlue2")
center_frame.place(relx=0.2, y=30, relheight=1, relwidth=0.6)

# right frame
right_frame = Frame(frame, bg='SkyBlue2')
right_frame.place(relx=0.8, y=30, relheight=1, relwidth=0.2)

# data entry
username_entry = StringVar()
password_entry = StringVar()

# username label
username_label = Label(center_frame, text="User Name:", font=labelfont, bg='SkyBlue2')
username_label.place(relx=0.5 , rely=0.32, anchor=CENTER)

# username textbox
username_textbox = Entry(center_frame, width=19, textvariable=username_entry, font=entryfont)
username_textbox.place(relx=0.5 , rely=0.37, anchor=CENTER)

#password label
password_label = Label(center_frame, text="Password:", font=labelfont, bg='SkyBlue2')
password_label.place(relx=0.5 , rely=0.42, anchor=CENTER)

#password textbox
password_textbox = Entry(center_frame, width=19, textvariable=password_entry, font=entryfont)
password_textbox.place(relx=0.5 , rely=0.47, anchor=CENTER)

# button for login
login_button = Button(center_frame, text='Login', font=labelfont, command=check_details, width=18)
login_button.place(relx=0.5 , rely=0.57, anchor=CENTER)

description_entry = StringVar()
amount_entry = StringVar()
location_entry = StringVar()
category_entry = StringVar()

# description label
description_label = Label(left_frame, text="Description:", font=labelfont, bg='SkyBlue2')
description_label.place_forget()
description_textbox = Entry(left_frame, width=19, textvariable=description_entry, font=entryfont)
description_textbox.place_forget()

# LEFT SIDE

# amount label
amount_label = Label(left_frame, text="Amount:", font=labelfont, bg='SkyBlue2')
amount_label.place_forget()
amount_textbox = Entry(left_frame, width=19, textvariable=amount_entry, font=entryfont)
amount_textbox.place_forget()

# location label
location_label = Label(left_frame, text="Location (City, Country):", font=labelfont, bg='SkyBlue2')
location_label.place_forget()
location_textbox = Entry(left_frame, width=19, textvariable=location_entry, font=entryfont)
location_textbox.place_forget()

# category label
category_label = Label(left_frame, text="Category:", font=labelfont, bg='SkyBlue2')
category_label.place_forget()
category_optionbox = OptionMenu(left_frame, category_entry, 'Restaurants & Dining', 'Home & Utilities', 'Transportation', 'Shopping', 'Entertainment', 'Miscellaneous',)
category_optionbox.place_forget()

#date label
date_label = Label(left_frame, text="Transaction Date:", font=labelfont, background='SkyBlue2')
date_label.place_forget()
date_entry = DateEntry(left_frame, font=("Arial", 12), width=15)
date_entry.place_forget()

#button to add record
addexpense_button = Button(left_frame, text='Add Record', font=labelfont, command=add_expense, width=18)
addexpense_button.place_forget()

#button to delete record
delete_expense_button = Button(left_frame, text='Delete Record', font=labelfont, command=remove_record, width=18)
delete_expense_button.place_forget()

# current temperature
current_location = connector.execute('SELECT location FROM users').fetchall()
current_temperature_c = get_current_temp(current_location[0][0])[0]
current_temperature_f = get_current_temp(current_location[0][0])[1]

# temperature label
temperature_label = Label(left_frame, text=f"Current Temp: {current_temperature_c}, {current_temperature_f}", font=labelfont, bg='SkyBlue2')
temperature_label.place_forget()

# temperature location label
temperature_location_label = Label(left_frame, text=f"Current Location: {get_current_location()}", font=labelfont, bg='SkyBlue2')
temperature_location_label.place_forget()

# CENTER

# table for showing all the expenses
title_table_label = Label(center_frame, text='Expense Records', font=headerfont, bg='DodgerBlue4', fg='White')
title_table_label.pack_forget()

tree = ttk.Treeview(center_frame, height=100, selectmode=BROWSE,
columns=("Description", "Amount ($)", "Category", "Date", "Location"))

X_scroller = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview)
Y_scroller = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
X_scroller.pack_forget()
Y_scroller.pack_forget()

s=ttk.Style()
s.configure('Treeview', rowheight=20)
s.configure('Treeview.Heading', font=('Garamond', 12,'bold'))
tree.config(yscrollcommand=Y_scroller.set, xscrollcommand=X_scroller.set)

tree.heading('Description', text='Description', anchor=CENTER)
tree.heading('Amount ($)', text='Amount ($)', anchor=CENTER)
tree.heading('Category', text='Category', anchor=CENTER)
tree.heading('Date', text='Date', anchor=CENTER)
tree.heading('Location', text='Location', anchor=CENTER)   

tree.column('#0', width=0, stretch=NO)
tree.column('#1', minwidth=200, width=200, stretch=NO)
tree.column('#2', minwidth=100, width=100, stretch=NO)
tree.column('#3', minwidth=170, width=170, stretch=NO)
tree.column('#4', minwidth=100, width=100, stretch=NO)
tree.column('#5', minwidth=200, width=200, stretch=NO)

tree.place_forget()

# budget label

total_spending = connector.execute('SELECT SUM(amount) FROM expenses').fetchall()

if total_spending[0][0] == None:
    current_budget = connector.execute('SELECT budget FROM users').fetchall()
    budget_label = Label(center_frame, text=f'Current Budget: ${current_budget[0][0]}', font=labelfont, bg='SkyBlue2')
    budget_label.place_forget()

    over_under_label = Label(center_frame, text=f'Over or Under Budget?', font=labelfont, bg='SkyBlue2')
    over_under_label.place_forget()
else:
    current_budget = connector.execute('SELECT budget FROM users').fetchall()
    budget_label = Label(center_frame, text=f'Current Budget: ${current_budget[0][0]}', font=labelfont, bg='SkyBlue2')
    budget_label.place_forget()
    over_under_label = Label(center_frame, text=f'Over or Under Budget?', font=labelfont, bg='SkyBlue2')
    if current_budget[0][0] > total_spending[0][0]:
        over_under_label.config(foreground='DarkGreen')
        over_under_label['text'] = 'Under Budget'
    if current_budget[0][0] < total_spending[0][0]:
        over_under_label.config(foreground='Red')
        over_under_label['text'] = 'Over Budget'
    else:
        over_under_label.config(foreground='Black')
        over_under_label['text'] = 'Break Even'
    over_under_label.place_forget()

# RIGHT SIDE

# ticker label
ticker_label = Label(right_frame, text='Ticker:', font=labelfont, bg='SkyBlue2')
ticker_label.place_forget()

ticker_entry = StringVar()
new_username_entry = StringVar()
new_password_entry = StringVar()
new_budget_entry = StringVar()
new_location_entry = StringVar()

# ticker textbox
ticker_textbox = Entry(right_frame, width=19, textvariable=ticker_entry, font=entryfont)
ticker_textbox.place_forget()

# button for stock price
view_stock_button = Button(right_frame, text='View Stock Price', font=labelfont, command=show_stock_price, width=18)
view_stock_button.place_forget()

# button for bitcoin price
view_bitcoin_button = Button(right_frame, text='View Bitcoin Price', font=labelfont, command=show_bitcoin_price, width=18)
view_bitcoin_button.place_forget()

# button for categorical spending - change function
category_expense_button = Button(right_frame, text='View Category Spending', font=labelfont, command=show_categorical_expense, width=18)
category_expense_button.place_forget()

# button for monthly spending - change function
monthly_spending_button = Button(right_frame, text='View Monthly Spending', font=labelfont, command=monthly_spending, width=18)
monthly_spending_button.place_forget()

# username change label
username_change_label = Label(right_frame, text='New Username:', font=labelfont, bg='SkyBlue2')
username_change_label.place_forget()

# username change textbox
username_change_textbox = Entry(right_frame, width=19, textvariable=new_username_entry, font=entryfont)
username_change_textbox.place_forget()

# password change label
password_change_label = Label(right_frame, text='New Password:', font=labelfont, bg='SkyBlue2')
password_change_label.place_forget()

# password change textbox
password_change_textbox = Entry(right_frame, width=19, textvariable=new_password_entry, font=entryfont)
password_change_textbox.place_forget()

# budget change label
budget_change_label = Label(right_frame, text='New Budget:', font=labelfont, bg='SkyBlue2')
budget_change_label.place_forget()

# budget change textbox
budget_change_textbox = Entry(right_frame, width=19, textvariable=new_budget_entry, font=entryfont)
budget_change_textbox.place_forget()

# location change label
location_change_label = Label(right_frame, text='New Location (City in USA):', font=labelfont, bg='SkyBlue2')
location_change_label.place_forget()

# location change textbox
location_change_textbox = Entry(right_frame, width=19, textvariable=new_location_entry, font=entryfont)
location_change_textbox.place_forget()

# button for updating details
update_details_button = Button(right_frame, text='Update Details', font=labelfont, command=update_details, width=18)
update_details_button.place_forget()

# button for logging out
logout_button = Button(right_frame, text='Logout', font=labelfont, command=logout, width=18)
logout_button.place_forget()

frame.update()
frame.mainloop()
