#!/usr/bin/python3
"""Author:  Plack
   Date:    4/15/21
   Purpose:  Track local weather, weight, blood sugar, Ketone level, and
   other data using sqliteDB and accessed using Flask APIs.  Source data
   is a combination of user created and public API data.  Based partially
   on code shared by RZFeeser from Alta3 Research."""

# standard library
import sqlite3 as sql

# python3 -m pip install flask
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

# return home.html (landing page)
@app.route('/')
def home():
    return render_template('home.html')

# return entry_form.html (a way to add a my daily data to the sqliteDB)
@app.route('/enternew')
def new_data():
    return render_template('entry_form.html')

# if someone uses entry_form.html it will generate a POST
# this post will be sent to /addrec
# where the information will be added to the sqliteDB
@app.route('/addrec',methods = ['POST'])
def addrec():
    try:
        nm = request.form['nm']     # weight

        # connect to sqliteDB
        with sql.connect("database.db") as con:
            cur = con.cursor()

            # place the info from our form into the sqliteDB
            cur.execute("INSERT INTO weight_tbl (name) VALUES (?)",(nm) )
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

@app.route('/list')
def list_weight():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("SELECT * from weight_tbl")           # pull all information from the table "students"
    
    rows = cur.fetchall()
    return render_template("list.html",rows = rows) # return all of the sqliteDB info as HTML


if __name__ == '__main__':
    try:
        # ensure the sqliteDB is created
        con = sql.connect('database.db')
        print("Opened database successfully")
        # ensure that the table weight_tbl is ready to be written to
        con.execute('CREATE TABLE IF NOT EXISTS weight_tbl (name TEXT)')
        print("Table created successfully")
        con.close()
        # begin Flask Application 
        app.run(host="0.0.0.0", port=2224, debug = True)
    except:
        print("App failed on boot")
