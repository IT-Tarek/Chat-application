#library



import re
from flask_login import logout_user

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from flask_socketio import SocketIO, join_room, leave_room, emit

from flask.globals import session
from werkzeug.security import generate_password_hash, check_password_hash

from flask_mysqldb import MySQL




#Contact Database



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





#login ---


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
                    


                    return render_template('admin_sham.html', Messages=data2, students=data)

                else:
                    return render_template('home.html')

            else:
                return render_template('login.html')


        else:
            return render_template('login.html')

    else:
        return render_template('login.html')





#sign

@app.route('/sign', methods=['POST', 'GET'])
def sign():
    
    if   "username" in session:
           return redirect(url_for('home'))

    else:
        return render_template('sign.html')





#content

@app.route('/content', methods=['POST', 'GET'])
def content():
   if  ("username" in session) and( session['username']!='leader_leaders'): 
      
      return render_template('content.html')
   else:
      return redirect(url_for('home'))



   



#insert_user --

@app.route('/insert_user', methods=['POST', 'GET'])
def insert_user():

    if request.method == "POST":

        name = request.form['name']
        xname = "\w*$"
        xuserame = "^[A-Za-z][A-Za-z0-9_]{7,29}$"
        ConditionalName = re.match(xname, name)

        lastname = request.form['lastname']
        ConditionalLastName = re.match(xname, lastname)

        username = request.form['username']
        ConditionalUserName = re.match(xuserame, username)

        password = request.form['password']
        hashed_password = generate_password_hash(password)
        repassword = re.match(xname, password)

        email = request.form['email']
        xemail = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ConditionalEmail = re.match(xemail, email)

        phone = request.form['phone']
        x1 = "^\d\d\d\d\d\d\d\d\d\d$"
        ConditionalPhone = re.match(x1, phone)
        
        formErrors = []

        cur = mysql.connection.cursor()

        results = cur.execute(
            "SELECT *  FROM registration WHERE username=%s", [username])

        if results > 0:

            formErrors = [" لا يمكن تكرار الحساب "]
        if ConditionalName == None:
            formErrors = [" الاسم غير مقبول "]
        elif ConditionalLastName == None:
            formErrors = [" الاسم غير مقبول "]
        elif ConditionalEmail == None:
            formErrors = [" الايميل غير صحيح "]
        elif repassword == None:
            formErrors = ["  كلمة السر غير مقبولة  "]

        elif ((len(username) < 10) or (ConditionalUserName == None)):

            formErrors = ["اسم المستخدم غير مقبول"]

        elif len(password) < 10:
            formErrors = ["كلمة السر قصيرة "]

        elif ConditionalPhone == None:
            formErrors = ["رقم الموبايل غير صحيح" ]

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


 # insert_message



@app.route('/insert_message', methods=['POST', 'GET'])
def insert_message():

    if request.method == "POST":
        textarea = request.form['textarea']
        sender = request.form['Complaint']
        xname = "^\w+( \w+)*$"
        rtextarea = re.match(xname, textarea)



        if ((rtextarea == None) or (rtextarea=="")):

              return redirect(url_for('content'))



        else:

                flash("تمت العملية بنجاح", "success")

                cur = mysql.connection.cursor()

                cur.execute(
                    "INSERT INTO messages_1(message,Complaint) VALUES(%s, %s)", (textarea, sender))

                mysql.connection.commit()

                return render_template('content.html'),{"Refresh": "2; url=http://127.0.0.1:2700/home"}

    else:
      
       return redirect(url_for('login'))
    

#Admin adds user
 

@app.route('/insert', methods=['POST', 'GET'])
def insert():
    if request.method == "POST":
        name = request.form['name']
        xname = "^\w*$"
        ConditionalName = re.match(xname, name)
        lastname = request.form['lastname']
        ConditionalLastName = re.match(xname, lastname)

        username = request.form['username']
        ConditionalUserName = re.match(xname, username)

        password = request.form['password']
        hashed_password = generate_password_hash(password)
        repassword = re.match(xname, password)

        email = request.form['email']
        xemail = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ConditionalEmail = re.match(xemail, email)

        phone = request.form['phone']
        x1 = "^\d\d\d\d\d\d\d\d\d\d$"
        ConditionalPhone = re.match(x1, phone)
        formErrors = []

        cur = mysql.connection.cursor()

        results = cur.execute(
            "SELECT *  FROM registration WHERE username=%s", [username])

        if results > 0:
            formErrors = [" لا يمكن تكرار الحساب "]

        if ConditionalName == None:
            formErrors = [" الاسم غير مقبول "]

        elif ConditionalLastName == None:
            formErrors = [" الاسم غير مقبول "]

        elif ConditionalEmail == None:
            formErrors = [" الايميل غير صحيح "]

        elif repassword == None:
            formErrors = ["  كلمة السر غير مقبولة  "]


        elif  len(username) < 10:
           
         formErrors = ["اسم المستخدم  قصير ", "error"]

        elif ConditionalUserName == None:

         formErrors = ["اسم المستخدم غير مقبول", "error"]


        elif len(password) < 10:
            formErrors = ["كلمة السر قصيرة ", "error"]

        elif ConditionalPhone == None:
            formErrors = ["رقم الموبايل غير صحيح"]

        for x in formErrors:

            flash(x)

            return redirect(url_for('Admin'))

        if not formErrors:
            cur = mysql.connection.cursor()

            cur.execute(
                "INSERT INTO registration (name,last_name,username,password, email, phone) VALUES  (%s, %s, %s,%s, %s, %s)", (name, lastname, username, hashed_password, email, phone))
                      
            mysql.connection.commit()
            flash("تمت العملية بنجاح", "success")

            return redirect(url_for('Admin'))
    else:
        return redirect(url_for('Admin'))

#Delete a complaint

@app.route('/delete/<string:id>', methods=['POST', 'GET'])
def delete(id):

    if   "username" in session and session['username'] =="leader_leaders"  and session['groupid'] == '1000' and session['id'] == 17:

        cur = mysql.connection.cursor()
        results= cur.execute("DELETE FROM messages_1  WHERE id=%s", (id,))
        mysql.connection.commit()
        if results > 0:

               flash("تم حذف الرسالة بنجاح " , "success")
        else:
             return redirect(url_for('Admin'))



        return redirect(url_for('Admin'))
    else:
         return redirect(url_for('Admin'))
    
    
# admin_sham


@app.route('/admin_sham', methods=['POST', 'GET'])
def Admin():
    if  "username" in session and  session['username'] == "leader_leaders"  and session['groupid'] == '1000' and   session['id'] == 17:
          
           
    
        cur = mysql.connection.cursor()
        cur.execute("SELECT  * FROM registration where groupid !=1000")
        data = cur.fetchall()
        cur.close()


        cur2 = mysql.connection.cursor()

        cur2.execute("SELECT  * FROM messages_1")

        data2 = cur2.fetchall()
        cur2.close()
        

 
        return render_template('admin_sham.html',  Messages=data2, students=data)
    else:
        return redirect(url_for('login'))
 


   #home

@app.route('/home', methods=['POST', 'GET'])
def home():
    if "username" in session:

        return render_template('home.html', user=session['username'])

    else:
        return redirect(url_for('login'))



    


 
  
# delete user --


@app.route('/delete1/<string:id>', methods=['POST', 'GET'])
def delete1(id):
    if  "username" in session and  session['username'] == "leader_leaders"  and session['groupid'] == '1000' and   session['id'] == 17:

        cur = mysql.connection.cursor()
        results= cur.execute("DELETE FROM registration  WHERE id=%s", (id,))
        mysql.connection.commit()


        if results > 0:

               flash("تم حذف المستخدم بنجاح " , "success")
        else:
             return redirect(url_for('Admin'))

    else:
        return redirect(url_for('Admin'))



# Deletion of email messages by the user



@app.route('/delete_email/<string:id>', methods=['POST', 'GET'])
def delete_email(id):
    if "username" in session:

        id_session= session['id']

        cur5 = mysql.connection.cursor()
        cur5.execute(
             "SELECT *  FROM send  WHERE id=%s",(id,))     
        myemail = cur5.fetchall()
        cur5.close()

        if len(myemail)>0:

          receiver_username=myemail[0][4]

          cur10 = mysql.connection.cursor()
          cur10.execute(
        
            "SELECT *  FROM registration WHERE username=%s", [receiver_username])
          inf_receiver = cur10.fetchall()
          id_receiver  =inf_receiver[0][0]
          cur10.close()


 
          if  id_receiver ==id_session:

                    cur = mysql.connection.cursor()
                    results= cur.execute("DELETE FROM send  WHERE id=%s", (id,))
                    mysql.connection.commit()

                    if results > 0:

                          flash("تم حذف الرسالة بنجاح " , "success")
                          return redirect(url_for('private'))

                    else:
                          return redirect(url_for('private'))
          else:
                
                 return redirect(url_for('private'))


        else:

                return redirect(url_for('private'))


    else:
                return redirect(url_for('login'))


#  update
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
            formErrors = ["اسم المستخدم قصيرة"]
        elif len(password) < 10:
            formErrors = ["كلمة السر قصيرة "]

        elif len(phone) != 10:
            formErrors = ["رقم الموبايل غير صحيح"]

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
            return redirect(url_for('Admin'))
    else:
        return redirect(url_for('login'))

#law
@app.route('/law', methods=['POST', 'GET'])
def law():

    return render_template("law.html")

#chat
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if(request.method == 'POST'):
      

        room = request.form['room']
        # In this step I will store  the data in session
       
        session['room'] = room
        return render_template('chat.html', session=session)

    else:
        if(session.get('username') is not None):
            return render_template('home.html', session=session)
        else:
            return redirect(url_for('login'))
        
    #join

@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('username') +
         ' has entered the room'}, room=room)

#text
@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    emit('message', {'msg':session.get('username')+
         ' : ' + message['msg']}, room=room)


#left
@socketio.on('left', namespace='/chat')
def left(message):
    myroom = session.get('room')
    username = session.get('username')
    leave_room(myroom)
    session.clear()
    emit('status', {'msg': username +' has left the room.'}, room=myroom) 

 #private   

@app.route('/private', methods=['POST', 'GET'])
def private():
    if "username" in session:
         username = session['username']

         cur0 = mysql.connection.cursor()
         cur0.execute(
            "SELECT id, sender,mymail,receiver  FROM send WHERE receiver=%s", [username])
         mydata = cur0.fetchall()
         cur0.close()

         return render_template('private.html', mysend=mydata) 
    else:

        return redirect(url_for('login'))

#logout
    
@app.route("/logout")
def logout():
    logout_user
    session.clear()

    return redirect(url_for('login'))


   
   
#send
@app.route('/send', methods=['POST', 'GET'])
def send():
    if request.method == "POST": 
        sender = session['username']
        receiver = request.form['receiver']
        mymail = request.form['mymail']
        xname = "^\w+( \w+)*$"

        rtextarea = re.match(xname, mymail)

        if (rtextarea == None):
             return redirect(url_for('home'))
        
        elif (receiver != sender):
            
           
            connect = mysql.connection.cursor()

               
            connect.execute(
               "SELECT *  FROM registration WHERE username=%s", [receiver])
        

            x = connect.fetchall()

            if len(x) >0:
           
         

              user_id=x[0][0]
              mysql.connection.commit() 


              cur1 = mysql.connection.cursor()



              cur1.execute(
                   "INSERT INTO send(mymail,receiver,sender,user_id) VALUES(%s, %s,%s,%s)", (mymail, receiver, sender,user_id))
              mysql.connection.commit()
              flash(" تمت العملية بنجاح", "success")
              return redirect(url_for('private'))       



            else:
                  return redirect(url_for('home'))

        
        else:
          return redirect(url_for('login'))
 
          
    else:
        return redirect(url_for('login'))





if __name__ == '__main__':
    socketio.run(app, port=2700)
