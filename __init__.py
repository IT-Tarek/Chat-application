from tkinter import *
from tkinter import messagebox
import re
from flask_session import Session
from flask_login import logout_user

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from flask_socketio import SocketIO, join_room, leave_room, emit

from flask.globals import session
from werkzeug.security import generate_password_hash, check_password_hash
#from sklearn import svm
#from sklearn.naive_bayes import GaussianNB
from flask_mysqldb import MySQL
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.debug = True

socketio = SocketIO(app, manage_session=False)

app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] ='cham'

mysql = MySQL(app)


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method =='POST':

        username = request.form['username']
        mypassword = request.form['password']

        cur = mysql.connection.cursor()
        results = cur.execute(
            "SELECT *  FROM registration WHERE username=%s", [username])

        if results > 0:

            results = cur.fetchall()

            password = results[0][4]

            if check_password_hash(password, mypassword):

                username = session['username'] = results[0][3]
                session['groupid'] = results[0][7]
                session['id'] = results[0][0]

                password = results[0][4]

                if session['username'] == "leader_leaders" and session['groupid'] == '1000' and session['id'] == 17:

                    cur1 = mysql.connection.cursor()
                    cur1.execute(
                        "SELECT  * FROM registration where groupid !=1000")
                    data = cur1.fetchall()

                    cur1.close()
                    cur2 = mysql.connection.cursor()

                    cur2.execute("SELECT  * FROM messages_1")
                    data2 = cur2.fetchall()
                    cur2.close()


                    return render_template('admin_sham.html', messages_1=data2, students=data)

                else:
                    return render_template('friends.html')

            else:
                return render_template('login.html')


        else:
            return render_template('login.html')

    else:
        return render_template('login.html')



@app.route('/sign', methods=['POST', 'GET'])
def sign():

    return render_template('sign.html')


@app.route('/content', methods=['POST', 'GET'])
def content():
    return render_template('content.html')

    # if request.method == "POST":

   # else:
  #  return redirect(url_for('login'))


@app.route('/admin_sham', methods=['POST', 'GET'])
def Admin():
    if session['username'] == "leader_leaders" and session['groupid'] == '1000'  and session['id'] == 17:




        cur = mysql.connection.cursor()
        cur.execute("SELECT  * FROM registration where groupid !=1000")
        data = cur.fetchall()
        cur.close()


        cur2 = mysql.connection.cursor()

        cur2.execute("SELECT  * FROM messages_1")

        data2 = cur2.fetchall()
        cur2.close()
        
      

        return render_template('admin_sham.html',  message_1=data2, students=data)
    else:
        return redirect(url_for('login'))

@app.route('/friends', methods=['POST', 'GET'])
def friends():
    if "username" in session:

        return render_template('friends.html', user=session['username'])

    else:
        return redirect(url_for('login'))


@app.route('/insert_user', methods=['POST', 'GET'])
def insert_user():

    if request.method == "POST":
        name = request.form['name']
        xname = "^\w*$"
        r4 = re.match(xname, name)
        lastname = request.form['lastname']
        r5 = re.match(xname, lastname)

        username = request.form['username']
        r6 = re.match(xname, username)

        password = request.form['password']
        hashed_password = generate_password_hash(password)
        repassword = re.match(xname, password)

        email = request.form['email']
        xemail = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        re3 = re.match(xemail, email)

        phone = request.form['phone']
        x1 = "^\d\d\d\d\d\d\d\d\d\d$"
        re1 = re.match(x1, phone)
        formErrors = []

        cur = mysql.connection.cursor()

        results = cur.execute(
            "SELECT *  FROM registration WHERE username=%s", [username])

        if results > 0:

            formErrors = [" لا يمكن تكرار الحساب ", "error"]
        if r4 == None:
            formErrors = [" الاسم غير مقبول ", "error"]
        elif r5 == None:
            formErrors = [" الاسم غير مقبول ", "error"]
        elif re3 == None:
            formErrors = [" الايميل غير صحيح ", "error"]
        elif repassword == None:
            formErrors = ["  كلمة السر غير مقبولة  ", "error"]

        elif ((len(username) < 10) or (r6 == None)):

            formErrors = ["اسم المستخدم غير مقبول", "error"]

        elif len(password) < 10:
            formErrors = ["كلمة السر قصيرة ", "error"]

        elif re1 == None:
            formErrors = ["رقم الموبايل غير صحيح" ,"error"]

        for x in formErrors:

            flash(x)
            return redirect(url_for('sign')) 


        if not formErrors:
            cur = mysql.connection.cursor()

            cur.execute(
                "INSERT INTO registration (name,last_name,username,password, email, phone) VALUES (%s, %s, %s,%s, %s, %s)", (name, lastname, username, hashed_password, email, phone))
            mysql.connection.commit()
            flash("تمت العملية بنجاح", "success")

        return render_template('sign.html'), {"Refresh": "2; url=http://127.0.0.1:2700/"}

    else:
        return redirect(url_for('login'))


@app.route('/insert_message', methods=['POST', 'GET'])
def insert_message():

    if request.method == "POST":

        textarea = request.form['textarea']
        Complaint = request.form['Complaint']
        xname = "^\w+( \w+)*$"
        rtextarea = re.match(xname, textarea)

        cur7 = mysql.connection.cursor()

        resu = cur7.execute(
            "SELECT *  FROM registration WHERE username=%s", [Complaint])

        if resu > 0:

            if (rtextarea == None):

                return redirect(url_for('content'))

            else:
                cur = mysql.connection.cursor()

                cur.execute(
                    "INSERT INTO messages_1(message,Complaint) VALUES(%s, %s)", (textarea, Complaint))

                mysql.connection.commit()
                #return redirect(url_for('login'))
                return render_template('content.html'), {"Refresh": "2; url=http://127.0.0.1:2700/friends"}

        else:
            return redirect(url_for('content'))
    else:
        return redirect(url_for('login'))


@app.route('/insert', methods=['POST', 'GET'])
def insert():
    if request.method == "POST":
        name = request.form['name']
        xname = "^\w*$"
        r4 = re.match(xname, name)
        lastname = request.form['lastname']
        r5 = re.match(xname, lastname)

        username = request.form['username']
        r6 = re.match(xname, username)

        password = request.form['password']
        hashed_password = generate_password_hash(password)
        repassword = re.match(xname, password)

        email = request.form['email']
        xemail = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        re3 = re.match(xemail, email)

        phone = request.form['phone']
        x1 = "^\d\d\d\d\d\d\d\d\d\d$"
        re1 = re.match(x1, phone)
        formErrors = []

        cur = mysql.connection.cursor()

        results = cur.execute(
            "SELECT *  FROM registration WHERE username=%s", [username])

        if results > 0:

            formErrors = [" لا يمكن تكرار الحساب ", "error"]
        if r4 == None:
            formErrors = [" الاسم غير مقبول ", "error"]
        elif r5 == None:
            formErrors = [" الاسم غير مقبول ", "error"]
        elif re3 == None:
            formErrors = [" الايميل غير صحيح ", "error"]
        elif repassword == None:
            formErrors = ["  كلمة السر غير مقبولة  ", "error"]

        elif ((len(username) < 10) or (r6 == None)):

            formErrors = ["اسم المستخدم غير مقبول", "error"]

        elif len(password) < 10:
            formErrors = ["كلمة السر قصيرة ", "error"]

        elif re1 == None:
            formErrors = ["رقم الموبايل غير صحيح"]

        for x in formErrors:

            flash(x)
            return redirect(url_for('Admin'))

        if not formErrors:
            cur = mysql.connection.cursor()

            cur.execute(
                "INSERT INTO registration (name,last_name,username,password, email, phone) VALUES (%s, %s, %s,%s, %s, %s)", (name, lastname, username, hashed_password, email, phone))
            mysql.connection.commit()
            flash("تمت العملية بنجاح", "success")

            return redirect(url_for('Admin'))
    else:
        return redirect(url_for('Admin'))

# delete message#


@app.route('/delete/<string:id>', methods=['POST', 'GET'])
def delete(id):
    if session['username'] =="leader_leaders"  and session['groupid'] == '1000' and session['id'] == 17:

        flash("تم حذف المستخدم بنجاح")
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM messages_1  WHERE id=%s", (id,))
        mysql.connection.commit()



        return redirect(url_for('Admin'))
    else:
         return redirect(url_for('Admin'))
    




    

 
  
# delete user#


@app.route('/delete1/<string:id>', methods=['POST', 'GET'])
def delete1(id):
    if session['username'] == "leader_leaders" and session['groupid'] == '1000' and session['id'] == 17:

        flash("تم حذف المستخدم بنجاح")
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM registration  WHERE id=%s", (id,))
        mysql.connection.commit()
        return redirect(url_for('Admin'))
    else:
        return redirect(url_for('Admin'))

#    return render_template('admin_sham.html'), {"Refresh": "7; url=https://google.com"}


# delete_email


@app.route('/delete_email/<string:id>', methods=['POST', 'GET'])
def delete_email(id):
    # if request.form['username'] != 'leader_leaders' and request.form['groupid'] == 0:

    flash("تم حذف المستخدم بنجاح")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM send  WHERE id=%s", (id,))
    mysql.connection.commit()

    return redirect(url_for('private'))
    # else:
    #    return redirect(url_for('login'))


@app.route('/update', methods=['POST', 'GET'])
def update():

    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        email = request.form['email']
        phone = request.form['phone']
        formErrors = []

        if len(username) < 10:
            formErrors = ["اسم المستخدم قصيرة", "error"]
        elif len(password) < 10:
            formErrors = ["كلمة السر قصيرة ", "error"]

        elif len(phone) != 10:
            formErrors = ["رقم الموبايل غير صحيح", "error"]

        for x in formErrors:

            flash(x)

        if not formErrors:
            flash("تم تحديث البيانات بنجاح ", "success")

            cur = mysql.connection.cursor()
            cur.execute("""
               UPDATE registration
               SET name=%s, last_name=%s, username=%s,password=%s, email=%s, phone=%s
               WHERE id=%s
            """, (name, lastname, username, hashed_password, email, phone, id_data))
            mysql.connection.commit()
            return redirect(url_for('Admin'))

        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/law', methods=['POST', 'GET'])
def law():

    return render_template("law.html")


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if(request.method == 'POST'):
        # username = request.form['username']
        username = session['username']

        room = request.form['room']
        # In this step I will store  the data in session
        session['username'] = username
        session['room'] = room
        return render_template('chat.html', session=session, user_username=username)
    else:
        if(session.get('username') is not None):
            return render_template('chat.html', session=session)
        else:
            return redirect(url_for('login'))


@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('username') +
         ' has entered the room'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    emit('message', {'msg': session.get('username') +
         ' : ' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)


@app.route('/private', methods=['POST', 'GET'])
def private():
    if "username" in session:
        username = session['username']
        cur0 = mysql.connection.cursor()

        cur0.execute(
            "SELECT  id,sender,mymail FROM send WHERE receiver=%s", [username])
        mydata = cur0.fetchall()
        cur0.close()
        return render_template('private.html', mysend=mydata)

    else:

        return redirect(url_for('login'))


@app.route("/logout")
def logout():
    logout_user()
    return render_template('login.html')


@app.route('/send', methods=['POST', 'GET'])
def send():
    if session.get('username'):
        sender = session['username']
        mymail = request.form['mymail']

        receiver = request.form['receiver']
        xname = "^\w+( \w+)*$"
        rtextarea = re.match(xname, mymail)
        data = ["يا أحمق", "ياغبي ليش ما نجحت", "متخلف"]

        if (rtextarea == None):
            return redirect(url_for('friends'))

        elif (receiver == sender):
            return redirect(url_for('friends'))

        elif (mymail in data):

            data = [
                "   يمكن أن  تحوي رسالتك على كلمات غير أخلاقية قد تعرضك للملاحقة القانونية   "]
            for x in data:
                flash(x)
                return render_template('Secret.html')

                # if(x1 == 0):
                # flash(" تم الغاء الارسال", "success")

            # myokk = request.form['ok']

            # if(request.form['ok'] != None):
            #myokk = request.form['ok']

            #myok = request.form['ok']

            # if (myok == 'ok'):
            # flash("تمت العملية بنجاح", "success")

            # mysql.connection.commit()

                # else:
                #  flash("تمت العملية بنجاhhح", "success")

                # cur = mysql.connection.cursor()

                # cur.execute(
                #    "INSERT INTO send(mymail,receiver,sender) VALUES(%s, %s,%s)", (mymail, receiver, sender))
                # mysql.connection.commit()

                # return redirect(url_for('private'))

                # return render_template('Secret.html',  email=mymail, receivers=receiver)

            # return mymail, receiver, mymail
            # return redirect(url_for('send2'))

        else:

            flash("تمت العملية بنجاح", "success")

            cur = mysql.connection.cursor()

            cur.execute(
                "INSERT INTO send(mymail,receiver,sender) VALUES(%s, %s,%s)", (mymail, receiver, sender))
            mysql.connection.commit()

            return redirect(url_for('private'))
        # return render_template('private.html'), {"Refresh": "3; url=http://127.0.0.1:2700/friends"}

    else:
        return redirect(url_for('login'))


@app.route('/send2', methods=['POST', 'GET'])
def send2():
    if session.get('username'):
        sender = session['username']
        mymail = request.form['mymail']

        receiver = request.form['receiver']
        xname = "^\w+( \w+)*$"
        rtextarea = re.match(xname, mymail)
        if (rtextarea == None):
            return redirect(url_for('friends'))

        elif (receiver == sender):
            return redirect(url_for('friends'))

        else:

            flash("تمت العملية بنجاح", "success")

            cur = mysql.connection.cursor()

            cur.execute(
                "INSERT INTO send(mymail,receiver,sender) VALUES(%s, %s,%s)", (mymail, receiver, sender))
            mysql.connection.commit()

            return redirect(url_for('private'))
        # return render_template('private.html'), {"Refresh": "3; url=http://127.0.0.1:2700/friends"}

    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    socketio.run(app, port=2700)
