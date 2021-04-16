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

# python3 -m pip install flask
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

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
        return render_template("result.html",msg = msg)    #         

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
