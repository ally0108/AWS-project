from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date
import datetime
import pymysql
import os
import smtplib
from email.message import EmailMessage
import sys
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
import datetime

"""
conn = pymysql.connect(
        host= '127.0.0.1', 
        port = 3306,
        user = 'root', 
        password = '01234567',
        db = 'sys'
    )
"""


conn = pymysql.connect(
        host= 'awseb-e-32j973mnvh-stack-awsebrdsdatabase-jrmfhy9qlvny.cofit1itheku.us-east-1.rds.amazonaws.com', 
        port = 3306,
        user = 'admin', 
        password = '01234567',
        db = 'sys'
    )

cur=conn.cursor()



application = Flask(__name__)
application.config['SECRET_KEY'] = b'\xcc\x1e4\xc5\x8e\x80\xb5\xd9\xedd\xbe-\xd7\xf9\x8e\xd0\xccSG\xfe;\xa3Bh' # 加密用金鑰
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)

@application.route("/", methods = ['GET', 'POST'])
def home():
    return render_template('login.html')


@application.route("/login", methods = ['GET', 'POST'])
def login():
    return render_template('login.html')

@application.route("/login_u", methods = ['POST'])
def login_u():
    account = request.values.get('mid')
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
            return redirect(url_for('login'))
    else:
        flash('login error!')
        return redirect(url_for('login'))

@application.route("/add", methods = ['GET', 'POST'])
def add():
    return render_template('add_machine.html')

@application.route("/detail/<machine_id>", methods = ['GET', 'POST'])
def detail(machine_id):
    sql = "SELECT * FROM `machine` where machine_id = %s"
    
    cur.execute(sql,(machine_id))
    conn.commit()
    result = cur.fetchone()
    data = {}

    data['machine_id'] = result[0]
    data['type'] = result[1]
    data['status'] = result[2]
    data['repair_time'] = result[3]
    data['period'] = result[4]

    return render_template('detail_machine.html', data=data, username=session.get('name'))

@application.route("/edit/<machine_id>", methods = ['GET', 'POST'])
def edit(machine_id):
    sql = "SELECT * FROM `machine` where machine_id = %s"
    
    cur.execute(sql,(machine_id))
    conn.commit()
    result = cur.fetchone()
    data = {}

    data['machine_id'] = result[0]
    data['type'] = result[1]
    data['status'] = result[2]
    data['repair_time'] = result[3]

    return render_template('edit_machine.html', data=data)

@application.route("/edit_submit", methods = ['GET', 'POST'])
def edit_submit():
    type = request.values.get('machine_type')
    machine_id = request.values.get('machine_id')
    status = request.values.get('status')

    sql = "UPDATE `machine` SET `type` = %s, `status` = %s where machine_id = %s"
    
    cur.execute(sql,(type, status, machine_id))
    conn.commit()
    send_email(machine_id)

    return redirect(url_for('machine'))

@application.route("/info", methods = ['GET', 'POST'])
def info():
    """
    mid(員工編號)
    password
    machine_id
    name
    email
    """
    mid = session.get('mid')
    sql = """SELECT `password`, `name`, `email` FROM `member` where `mid` = %s"""
    
    cur.execute(sql,(mid))
    conn.commit()
    result = cur.fetchone()

    
    data = {}

    data['password'] = result[0]
    data['name'] = result[1]
    data['email'] = result[2]

    return render_template('info.html', data=data)

@application.route("/update_info", methods = ['GET', 'POST'])
def update_info():
    name = request.values.get('name')
    password = request.values.get('password')
    email = request.values.get('email')
    mid = session.get('mid')

    sql = "UPDATE `member` SET `name` = %s, `password` = %s, `email` = %s WHERE `mid` = %s"
    
    cur.execute(sql,(name, password, email, mid))
    conn.commit()

    return redirect(url_for('info'))

@application.route("/machine", methods = ['GET', 'POST'])
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

    return render_template('machine.html', data=data, username=session.get('name'))

@application.route("/main", methods = ['GET', 'POST'])
def main():
    return render_template('mainpage.html')

@application.route("/repair", methods = ['GET', 'POST'])
def repair():
    """
    rid
    mid(員工編號)
    machine_id
    datetime
    """
    sql = "SELECT repair.*, member.name FROM `repair` JOIN `member` where repair.mid = member.mid"
    
    cur.execute(sql)
    conn.commit()
    result = cur.fetchall()
    data = []

    for r in result:
        temp = {}
        temp['rid'] = r[0]
        # temp['mid'] = r[1]
        temp['machine_id'] = r[2]
        temp['datetime'] = r[3]
        temp['name'] = r[4]

        data.append(temp)

    return render_template('repairpage.html', data=data)

@application.route("/update_machine/<machine_id>", methods = ['GET', 'POST'])
def update_machine(machine_id):
    """
    rid
    mid(員工編號)
    machine_id
    datetime
    """
    today = datetime.date.today()
    time = datetime.datetime.today()

    sql = "UPDATE `machine` SET `status` = 'good', `repair_time`= %s where machine_id = (%s)"
    cur.execute(sql,(time,machine_id))
    conn.commit()

    mid = session.get('mid')
    sql = "INSERT INTO `repair` (mid, machine_id, datetime) VALUES (%s, %s, %s)"
    cur.execute(sql,(mid, machine_id, today))
    conn.commit()


    return redirect(url_for('machine'))

@application.route("/add_machine", methods = ['GET', 'POST'])
def add_machine():
    """
    machine_id（機台編號）
    type (type A/ type B/ type C)
    status（良好/待維修）
    repair_time (是上次維修的時間)
    """
    machine_id = request.values.get('machine_id')
    type = request.values.get('machine_type')
    status = request.values.get('machine_status')
    period = request.values.get('machine_period')


    sql = "INSERT INTO `machine` (`machine_id`, `type`, `status`, `period`) VALUES (%s, %s, %s, %s)"
    cur.execute(sql,(machine_id, type, status, period))
    conn.commit()
    # result = cur.fetchone()

    return redirect(url_for('machine'))

@application.route("/delete/<machine_id>", methods = ['GET', 'POST'])
def delete(machine_id):
    sql = "DELETE FROM `machine` WHERE `machine_id` = %s"
    cur.execute(sql,(machine_id))
    conn.commit()

    return redirect(url_for('machine'))


def send_email(machine_id):
    send_user = 'clouddemodb@gmail.com'
    password = 'hjbxozbnvtbgpfbo'
    mid = session.get('mid')

    sql = "SELECT `email` FROM `member` WHERE `machine_id` = %s"
    cur.execute(sql,(machine_id))
    conn.commit()
    result = cur.fetchone()
    user = result[0]



    msg = EmailMessage()
    msg['Subject'] = 'Machine Update Notification'
    msg['From'] = send_user
    msg['To'] = user
    msg.set_content('您的機台資訊已被更新')

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465) # 設定SMTP伺服器
        server.ehlo() # 驗證SMTP伺服器
        server.login(send_user, password)
        server.send_message(msg)
        server.close()

        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)


if __name__ == '__main__':
    application.run( debug = True)