from __future__ import print_function

import datetime
import json
import sqlite3
import webbrowser

import jsonify
import pytz
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from xlsxwriter.workbook import Workbook
app = Flask(__name__)

@app.route("/")
def Hello():
    return render_template("login.html")

@app.route("/log")
def file():
    return render_template("file.html")

@app.route("/lo")
def admin_f():
    return render_template("admin_file.html")

@app.route("/download")
def excel():
    return render_template("file.html")

@app.route("/scan",methods=['POST'])
def scanner():
    return render_template("index.html")

@app.route("/function_route", methods=["POST"])
def my_function():
    #global data1
    rf = request.form
    print(rf)
    for key in rf.keys():
        data1 = key
    data_dic = json.loads(data1)
    print(data_dic.keys())
    global qr,loc_lat,loc_long
    qr = data_dic['qr']
    loc_lat = data_dic['loc_lat']
    loc_long = data_dic['loc_long']

    print(qr,loc_lat,loc_long)

    query1 = (
        '''SELECT DISTINCT first_name,last_name,Branch,year,GR,mail FROM student WHERE mail = (?) and Password = (?)''')
    con = sqlite3.connect('test.sqlite')
    cur = con.cursor()
    cur.execute(query1, [uname, upwd])
    result = cur.fetchall()
    print(result)
    res= result[0]
    print(res[0],res[1],res[2])
    con.commit()
    cur.close()
    x = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    print(x)

    con = sqlite3.connect('Report.sqlite')
    cur = con.cursor()

    #cur.execute('DROP TABLE IF EXISTS attendance')
    cur.execute('''CREATE TABLE IF NOT EXISTS attendance (event text,loc_lat text,loc_long text,first_name text,last_name text,Branch text,year text,
        GR text, mail text,date DATETIME)''')
    cur.execute(
        '''INSERT INTO attendance (event,loc_lat,loc_long,first_name,last_name,Branch,year,GR,mail,date) VALUES (?,?,?,?,?,?,?,?,?,?)'''
        , (qr,loc_lat,loc_long, res[0],res[1],res[2],res[3],res[4],res[5],x))

    con.commit()
    cur.close()

    resp_dic = {'title': 'Sum performed'}
    resp = jsonify(resp_dic)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route("/report",methods=["GET","post"])
def report():
    global branch,event,year,start_date,end_date
    branch = request.form['branch']
    event = request.form['event']
    year = request.form['year']
    start_date= request.form['start']
    print(start_date)
    end_date = request.form['end']
    print(end_date)


    workbook = Workbook('output.xlsx')
    worksheet = workbook.add_worksheet()

    #conn = sqlite3.connect('test.sqlite')
    #c = conn.cursor()
    #c.execute("select * from abc")
    #mysel = c.execute("select * from abc ")

    query = ('''SELECT DISTINCT event,loc_lat,loc_long,first_name,last_name,Branch,year,GR,mail,date FROM attendance where Branch=(?) AND event=(?) AND year=(?) AND date between (?) AND (?)''')
    con = sqlite3.connect('Report.sqlite')
    cur = con.cursor()
    cur.execute(query, [branch,event,year,start_date,end_date])
    #mysel = cur.execute(query, [branch,event,year,start_date,end_date])

    result = cur.fetchall()
    print(result)


    con.commit()
    cur.close()

    con = sqlite3.connect('Report.sqlite')
    cur = con.cursor()
    cur.execute(query, [branch, event, year, start_date, end_date])
    mysel = cur.execute(query, [branch,event,year,start_date,end_date])

    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, value)
    workbook.close()
    con.commit()
    cur.close()

    return render_template('example.html', value=result)


@app.route("/predict",methods=["POST","GET"])
def predict():
    query = (
        '''SELECT distinct event FROM attendance ''')
    con = sqlite3.connect('Report.sqlite')
    cur = con.cursor()
    cur.execute(query)

    result = cur.fetchall()
    print(result)
    con.commit()
    cur.close()
    return render_template('admin_file.html', pred= result)



@app.route("/login",methods=["POST"])

def log():
    if request.form['pr'] == 'admin' and request.form['uname'] == 'Piyush' and request.form["upwd"] == '@Piyush':
        return redirect(url_for("admin_f"))
    elif request.form['pr'] == 'stud':
        global uname,upwd
        uname =request.form['uname']
        print(uname)
        upwd = request.form['upwd']
        print(upwd)
        query = ('''SELECT DISTINCT Password FROM student WHERE mail = (?) ''')
        con = sqlite3.connect('test.sqlite')
        cur = con.cursor()
        cur.execute(query, [uname])
        res = cur.fetchone()
        print(res)
        con.commit()
        cur.close()
        print(res[0])
        if  res[0]==upwd:
            return redirect(url_for('file'))
        else:
            flash('''Please check again !!''')
            return redirect(url_for('Hello'))
    else:
        flash("You have not sign in please register or enter correct credentials!!")
        return redirect(url_for('Hello'))


@app.route("/profile",methods=["post"])
def profile():
    print(uname)
    print(upwd)
    query = ('''SELECT DISTINCT first_name,last_name,Branch,year,cgpa,dead,live,dob,GR,mail FROM student WHERE mail = (?) and Password = (?)''')
    con = sqlite3.connect('test.sqlite')
    cur = con.cursor()
    cur.execute(query, [uname,upwd])
    result = cur.fetchall()
    print(result)
    con.commit()
    cur.close()
    return render_template('profile.html', list = [x for x in result[0]])




@app.route("/add", methods=["POST","GET"])
def getvalue():
    fname = request.form['fname']
    lname = request.form['lname']
    branch = request.form['branch']
    year = request.form['year']
    company = request.form['company']
    cgpa = request.form['cgpa']
    dead = request.form['dead']
    live = request.form['live']
    dob = request.form['dob']
    mail = request.form['mail']
    gr = request.form['gr']
    pwd = request.form['pwd']


    con = sqlite3.connect('test.sqlite')
    cur = con.cursor()
    #cur.execute('DROP TABLE IF EXISTS student')
    cur.execute('''CREATE TABLE IF NOT EXISTS student (first_name text,last_name text,Branch text,year text,company text,cgpa text,dead Int16,
    live Int16,dob text, GR text, mail text , Password varchar)''')
    cur.execute('''INSERT INTO student (first_name,last_name,Branch,year,company,cgpa,dead,live,dob,GR,mail,Password) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)'''
                ,(fname,lname,branch,year,company,cgpa,dead,live,dob,gr,mail,pwd))



    con.commit()
    cur.close()
    done = "Submitted"

    return redirect(url_for('Hello'))

@app.route("/data/",methods=["post"])
def getdata():

    ab = [x for x in request.form.values()]

    query = ('''SELECT * FROM student WHERE Branch IN (?) AND year in (?) ''')
    con = sqlite3.connect('test.sqlite')
    cur = con.cursor()
    cur.execute(query,[ab[0],ab[1]])
    result = cur.fetchall()

    con.commit()
    cur.close()
    return render_template('example2.html',value=result)

if __name__ == "__main__":
    app.secret_key="Piyush"
    app.run(host='127.0.0.1', debug=True)