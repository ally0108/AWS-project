from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date
import datetime
import pymysql
import os
import smtplib
from email.message import EmailMessage
import sys

conn = pymysql.connect(
        host= '127.0.0.1', 
        port = 3306,
        user = 'root', 
        password = '01234567',
        db = 'sys'
    )

cur=conn.cursor()



app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # 加密用金鑰

@app.route("/index", methods = ['GET', 'POST'])
def index():
    return render_template('login.html')

@app.route("/login", methods = ['POST'])
def login():
    account = request.values.get('account')
    password = request.values.get('password')

    sql = "SELECT mid, password, name FROM `member` WHERE mid=(%s)"
    
    cur.execute(sql,(account))
    conn.commit()
    result = cur.fetchone()

    if result != None:
        if password == result[1]:
            flash('登入成功！')
            session['name'] = result[2]
            session['mid'] = result[0]
            return redirect(url_for('main'))
        else :
            flash('帳密輸入錯誤')
            print('')
            return redirect(url_for('index'))
    else:
        flash('login error!')
        return redirect(url_for('index'))

@app.route("/add", methods = ['GET', 'POST'])
def add():
    return render_template('add_machine.html')

@app.route("/detail", methods = ['GET', 'POST'])
def detail():
    return render_template('detail_machine.html')

@app.route("/edit", methods = ['GET', 'POST'])
def edit():
    return render_template('edit_machine.html')

@app.route("/info", methods = ['GET', 'POST'])
def info():
    return render_template('info.html')

@app.route("/machine", methods = ['GET', 'POST'])
def machine():
    """
    machine_id（機台編號）
    type (type A/ type B/ type C)
    status（良好/待維修）
    repair_time (是上次維修的時間)
    """

    sql = "SELECT * FROM `machine` "
    
    cur.execute(sql)
    conn.commit()
    result = cur.fetchall()
    data = []

    for r in result:
        temp = {}
        temp['machine_id'] = r[0]
        temp['type'] = r[1]
        temp['status'] = r[2]
        temp['repair_time'] = r[3]

        data.append(temp)

    return render_template('machine.html', data=data, name=session['name'])

@app.route("/main", methods = ['GET', 'POST'])
def main():
    return render_template('mainpage.html')

@app.route("/repair", methods = ['GET', 'POST'])
def repair():
    """
    rid
    mid(員工編號)
    machine_id
    datetime
    """
    sql = "SELECT * FROM `repair` "
    
    cur.execute(sql)
    conn.commit()
    result = cur.fetchall()
    data = []

    for r in result:
        temp = {}
        temp['rid'] = r[0]
        temp['mid'] = r[1]
        temp['machine_id'] = r[2]
        temp['datetime'] = r[3]

        data.append(temp)

    return render_template('repairpage.html', data=data)

    # return render_template('repairpage.html')



if __name__ == '__main__':
    app.run(host='127.0.0.1', port='4444', debug = True)