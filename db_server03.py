#!/usr/bin/python3
"""Author:  Plack
   Date:    4/15/21
   Purpose:  Track local weather, weight, blood sugar, Ketone level, and
   other data using sqliteDB and accessed using Flask APIs.  Source data
   is a combination of user created and public API data.  Based partially
   on code shared by RZFeeser from Alta3 Research."""

# standard library
import sqlite3 as sql
import datetime
import base64
import requests
import io


# python3 -m pip install flask
import json
from flask import Flask
from flask import render_template
from flask import request
import pandas as pd
import numpy as numpy
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PIL import Image


app = Flask(__name__)

# create global dictionary to define an activity's 'profile'.
ACTIVITY_PROFILE_DICT = dict({'go swimming': [25,100], 'go hiking': [10,100], \
        'go to the tide pooltide': [10,100], 'take a scenic drive': [0,100],  \
        'do indoor maintenance chores': [-20,100], 'go to a movie': [0,100],  \
        'go bowling': [0,100], 'play card games': [0,100],                    \
        'do garage maintenance': [0,2]})

def compare_activity_temp(x):
    activity_message = []    
    for key in x:
        if x.get(key)[0] <= 2 and x.get(key)[1] >= 2:
                activity_message.append(key)  
    return(activity_message)
        

def get_high(x):
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.set_xlabel('Day')
    ax.set_ylabel('Temp Celsius')
    ax.plot(x)
    fig.savefig('weather_high.png')
    im = Image.open("weather_high.png")
    data = io.BytesIO()
    im.save(data, "PNG")
    encoded_img_data = base64.b64encode(data.getvalue())
    return render_template("weather.html", img_data=encoded_img_data.decode('utf-8'))

# return home.html (landing page)
@app.route('/')
def home():
    return render_template('home.html')

# return entry_form.html (a way to add a health data to our sqliteDB)
@app.route('/enternew')
def new_weight():
    return render_template('entry_form.html')

# return entry_quote.html (a way to add a health data to our sqliteDB)
@app.route('/enterquote')
def new_quote():
    return render_template('entry_quote.html')

# return entry_csv.html (a way to add a health data to our sqliteDB)
@app.route('/entercsv')
def new_csv():
    return render_template('entry_csv.html')  
 

# if someone uses entry_form.html it will generate a POST
# this post will be sent to /addrec
# where the information will be added to the sqliteDB
@app.route('/addhealth',methods = ['POST'])
def addhealth():
    try:
        now = datetime.datetime.now()       # gets datetime stamp
        weight = request.form['weight']     # manual entry of weight
        blood_sugar = request.form['blood_sugar']
        ketone = request.form['ketone']
        sleep = request.form['sleep']
        activity = request.form['activity']



        # connect to sqliteDB
        with sql.connect("database.db") as con:
            cur = con.cursor()

            # place the info from the form and datetime stamp into sqliteDB
            cur.execute("INSERT INTO weight_table (now_t,weight_t,\
                blood_sugar_t,ketone_t,sleep_t,activity_t) \
                VALUES (?,?,?,?,?,?)",(now,weight,blood_sugar,ketone,sleep,\
                activity) )
            # commit the transaction to our sqliteDB
            con.commit()
        # if we have made it this far, the record was successfully added to the DB
        msg = "Record successfully added"
        
    except:
        con.rollback()  # this is the opposite of a commit()
        msg = "error in insert operation"    # we were NOT successful

    finally:
        con.close()     # successful or not, close the connection to sqliteDB
        return render_template("result.html",msg = msg)   

@app.route('/addquote',methods = ['POST'])
def addquote():
    try:
        now = datetime.datetime.now()       # gets datetime stamp
        name = request.form['name']
        quote = request.form['quote']     # manual entry of weight
        
        # connect to sqliteDB
        with sql.connect("database.db") as con:
            cur = con.cursor()

            # place the info from the form and datetime stamp into sqliteDB
            cur.execute("INSERT INTO quote_table (now_t,name_t,quote_t) \
                VALUES (?,?,?)",(now,name,quote) )
            # commit the transaction to our sqliteDB
            con.commit()
        # if we have made it this far, the record was successfully added to the DB
        msg = "Record successfully added"
        
    except:
        con.rollback()  # this is the opposite of a commit()
        msg = "error in insert operation"    # we were NOT successful

    finally:
        con.close()     # successful or not, close the connection to sqliteDB
        return render_template("result.html",msg = msg) 

@app.route('/addcsv',methods = ['POST'])
def addcsv():
    part_path = request.form['path']
    full_path = f"/Users/paullack/{part_path}"
    new_csv_data = pd.read_csv(full_path)
    try:
        con = sql.connect("database.db")
        # place the info from the csv into sqliteDB
        new_csv_data.to_sql('weight_table', con, if_exists='replace', index=False)
            # commit the transaction to our sqliteDB
        con.commit()
        # if we have made it this far, the record was successfully added to the DB
        msg = "Record successfully added"
        
    except:
        con.rollback()  # this is the opposite of a commit()
        msg = "error in insert operation"    # we were NOT successful

    finally:
        con.close()     # successful or not, close the connection to sqliteDB
        return render_template("result.html",msg = msg)    #                    #         

# return all entries from our sqliteDB as HTML
@app.route('/list')
def show_health():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("SELECT * from weight_table")           # pull all information from the table "weight_table"
    
    rows = cur.fetchall()
    return render_template("list_health.html",rows = rows) # return all of the sqliteDB info as HTML

@app.route('/listquote')
def show_quote():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("SELECT * from quote_table")           # pull all information from the table "weight_table"
    
    rows = cur.fetchall()
    return render_template("list_quote.html",rows = rows) # return all of the sqliteDB info as HTML    

@app.route('/activities',methods = ['GET', 'POST'])
def show_activities():
        #compare_activity_profile(ACTIVITY_PROFILE_DICT) 
    activity_message = compare_activity_temp(ACTIVITY_PROFILE_DICT)  
    msg = activity_message
    return render_template("activities.html",msg = msg)      

@app.route('/weather',methods = ['GET', 'POST'])
def weather():
    # put your api token from you free account to weatherbit.io here.
    api_token = '554f35e912074ab7b2524563f8d3619b'

    # use weatherbit.io documentation to find the correct url base to put 
    # here.  This will probably work for you.
    api_url_base = 'http://api.weatherbit.io/v2.0/'

    # creates a request and assigns it to a variable
    response = requests.get(api_url_base + 'forecast/daily?city=' + 'sedro-woolley' + ',' \
    + 'wa' + '&key=' + api_token) 

    weather_dict = json.loads(response.text)

    # creates the necessary list variables to hold the data from the API
    forecast_high_temp = []
    forecast_low_temp = []
    forecast_clouds = []
    date = []
    visibility = []
    rain = []
    moonset = []
    moonrise = []
    sunset = []
    sunrise = []
    wind_gust_speed = []
    moon_illumination = []

    # uses a for loop to load each of the list variables with 7 consecutive days
    # worth of data.
    for i in range(7):
        forecast_high_temp.append(weather_dict.get('data')[i].get('high_temp'))
        forecast_low_temp.append(weather_dict.get('data')[i].get('low_temp'))   
        forecast_clouds.append(weather_dict.get('data')[i].get('clouds'))   
        date.append(weather_dict.get('data')[i].get('valid_date'))  
        visibility.append(weather_dict.get('data')[i].get('vis'))
        rain.append(weather_dict.get('data')[i].get('precip'))
        moonset.append(weather_dict.get('data')[i].get('moonset_ts'))
        moonrise.append(weather_dict.get('data')[i].get('moonrise_ts')) 
        sunset.append(weather_dict.get('data')[i].get('sunset_ts'))
        sunrise.append(weather_dict.get('data')[i].get('sunrise_ts'))
        wind_gust_speed.append(weather_dict.get('data')[i].get('wind_gust_spd'))
        moon_illumination.append(weather_dict.get('data')[i].get('moon_phase_lunation'))
    return(get_high(forecast_high_temp)) 

if __name__ == '__main__':

    try:
        # ensure the sqliteDB is created
        con = sql.connect('database.db')
        print("Opened database successfully")
        # ensure that the table students is ready to be written to
        con.execute('CREATE TABLE IF NOT EXISTS weight_table (now_t TEXT, \
            weight_t TEXT, blood_sugar_t TEXT, ketone_t TEXT, sleep_t TEXT, \
            activity_t TEXT)')
        con.execute('CREATE TABLE IF NOT EXISTS quote_table (now_t TEXT, \
            name_t TEXT, quote_t TEXT)')
        print("Table created successfully")
        con.close()
        # begin Flask Application 
        app.run(host="0.0.0.0", port=2224, debug = True)
    except:
        print("App failed on boot")
