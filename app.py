from flask import Flask,redirect,request,render_template,session,url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re



app = Flask(__name__,template_folder='pages')

app.secret_key = 'root'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'train_reservation'


mysql = MySQL(app)
                     
@app.route("/")
@app.route('/index', methods = ['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/signup', methods = ['GET','POST'])
def signup():
    return render_template('signup.html')

@app.route('/ad_dash', methods = ['GET','POST'])
def ad_dash():

    return render_template('admin_dash.html',user=session['username'])

@app.route('/dashboard', methods = ['GET','POST'])
def dashboard():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM train WHERE EXISTS (SELECT Username FROM users WHERE users.Username = %s)',[session['username']])
    data=cursor.fetchall()
    return render_template('dashboard.html',data=data,user=session['username'])

@app.route('/login', methods = ['POST'])
def login():
    msg=''
    username,password='',''
    if request.method=='POST' and 'Username' in request.form and 'Password' in request.form and 'utype'in request.form:
        if request.form['utype']=='Admin':
            username=request.form['Username']
            password=request.form['Password']
            cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM admin WHERE a_username=%s AND a_password= %s',(username,password))
            account=cursor.fetchone()
            if account:
                session['username']=account['a_username']
                session['password']=account['a_password']
                print('Session variable set....')
                active_user=username
                cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                return render_template('admin_dash.html',user=active_user)
            
                
            else:
                msg='Invalid Details'
                return render_template('index.html',msg=msg)
        
        elif request.form['utype']=='User':
            username=request.form['Username']
            password=request.form['Password']
            cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE Username=%s AND Password= %s',(username,password))
            account=cursor.fetchone()
            if account:
                session['username']=account['Username']
                session['password']=account['Password']
                print('Session variable set....')
                msg=username
                cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM train WHERE EXISTS (SELECT Username FROM users WHERE users.Username = %s)',[session['username']])
                data=cursor.fetchall()
                return render_template('dashboard.html',data=data,user=session['username'])
            
                
            else:
                msg='Invalid Details'
                return render_template('index.html',msg=msg)
        else:
            msg='Invalid Details'
            return render_template('index.html',msg=msg)
    else:
        msg='Invalid Details'
        return render_template('index.html',msg=msg)

@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method=='POST' and 'Username' in request.form and 'Name' in request.form and 'Email' in request.form and 'Password' in request.form:
        uname=request.form['Username']
        name=request.form['Name']
        email=request.form['Email']
        password=request.form['Password']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        print('Done')
        cursor.execute('SELECT * FROM users WHERE Username=%s',[uname])
        print('done2')
        account=cursor.fetchone()
        if account:
            msg='Account already exists!'
            return render_template('index.html',msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg='Invalid Email'
        elif not re.match(r'[A-Za-z0-9]+',uname):
            msg='Username must contain only charecter and numbers!'
        else:
            print('done3')
            cursor.execute('INSERT INTO users (Username,Name,E_mail,Password) VALUES (% s , % s , % s , % s ) ',(uname,name,email,password))
            mysql.connection.commit()
            msg='You have successfully registeres!'
            return render_template('index.html',msg=msg)
    elif request.method=='POST':
        msg='Please fill all details!'
    return render_template('signup.html',msg=msg)

@app.route('/booking',methods=['GET','POST'])
def booking():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM train WHERE EXISTS (SELECT Username FROM users WHERE users.Username = %s)',[session['username']])
    data=cursor.fetchall()
    return render_template('booking.html',data=data,user=session['username'])

@app.route('/book',methods=['GET','POST'])
def book():
    if request.method =='POST' and 'Trainno' in request.form and 'PassengerNo' in request.form and 'Travel_Date' in request.form:
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        t_no=request.form['Trainno']
        print(t_no)
        cursor.execute('SELECT * FROM train WHERE TrainNo = %s',(t_no,))
        account=cursor.fetchone()
        print('done')
        if account:
            cursor.execute('SELECT Name,ID FROM users WHERE Username=%s',[session['username']])
            uname=cursor.fetchone()
            passenger_name=uname['Name']
            trainno=account['TrainNo']
            tname=account['Name']
            tarive=account['Arrive']
            tdest=account['Destination']
            t_a_time=account['Arrival_Time']
            t_d_time=account['Departure_Time']
            t_fare=account['Fare']
            travel_date=request.form['Travel_Date']
            username=session['username']
            userid=uname['ID']


            no_passenger=request.form['PassengerNo']
            total_cost=t_fare*int(no_passenger)


            cursor.execute('INSERT INTO bookings (TrainNo,T_Name,Username,Passenger_name, Arrive, Destination, Travel_Date, Arrival_Time, Departure_Time, PassengerNo, Total_Fare,userID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(trainno,tname,username,passenger_name,tarive,tdest,travel_date,t_a_time,t_d_time,no_passenger,total_cost,userid))
            mysql.connection.commit()
            cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM train WHERE EXISTS (SELECT Username FROM users WHERE users.Username = %s)',[session['username']])
            data=cursor.fetchall()
            msg = 'Fare amount  is : ' + str(total_cost) + ' for date : ' +str(travel_date) + ' and time is - ' + str(t_a_time) + ' train will departure at ' + str(t_d_time)  
            return render_template('dashboard.html',msg=msg,data=data,user=session['username'])
        else: 
            msg = 'Invalid Date'
            return render_template('booking.html', msg = msg,user=session['username'])  
    else :

        msg = 'Train Service Not Available!'
        return render_template('booking.html', msg=msg,user=session['username'])
    
@app.route('/cancle1',methods=['POST','GET'])
def cancle1():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    print(session['username'])
    cursor.execute('SELECT ID FROM users WHERE Username=%s',[session['username']])
    uname=cursor.fetchone()
    userid=uname['ID']
    print(userid)
    cursor.execute('SELECT * FROM bookings WHERE userID = %s', (userid,))
    data = cursor.fetchall()
    print(data)
    msg='Enter Details'
    return render_template('status.html' ,msg=msg,data=data ,user=session['username'])

@app.route('/cancle',methods=['POST','GET'])
def cancle():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method=='POST' and 'cls_ticketid' in request.form:
        cls_tik_id=request.form['cls_ticketid']
        user=session['username']
        # placeholders = ','.join(['%s'] * len(cls_tik_id))
        # query = "DELETE FROM bookings WHERE Booking_Id IN ({}) AND Username = %s".format(','.join(['%s'] * len(cls_tik_id)))
        
        print(cls_tik_id)
        # params = tuple(cls_tik_id + [user])

        # Execute the query with the parameters
        query = "DELETE FROM bookings WHERE Booking_Id = %s AND Username = %s"
        params = (cls_tik_id,user)
        

        if cursor.execute(query, params):
        # cursor.execute('DELETE FROM bookings WHERE Booking_Id =%s and Username=%s',(cls_tik_id,user)):
            print('deleted')
            mysql.connection.commit()
            cursor.execute('SELECT * FROM bookings WHERE Username = % s', (user,))
            data = cursor.fetchall()
        
            return render_template('status.html',data=data,user=session['username'])
        else:
            cursor.execute('SELECT * FROM bookings WHERE Username = % s', [session['username']])
            data = cursor.fetchall()
            print('not')
            print(data)
            msg='Please enter correct details!!!'
            return render_template('status.html',msg=msg,user=session['username'])
    else:
        print(session['username'])
        cursor.execute('''SELECT * FROM bookings WHERE 'Username' = % s''', [session['username']])
        data = cursor.fetchall()
        print(data)
        msg='Enter Details'
        return render_template('status.html' ,msg=msg,data=data ,user=session['username'])


@app.route('/cancel',methods=['POST','GET'])
def cancel():
    user=session['username']
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    print(cursor.execute('''SELECT * FROM bookings WHERE 'Username' = %s''', (user,)))
    print('done')
    data = cursor.fetchall()
    msg='Enter Details'
    print(session['username'])
    return render_template('status.html' ,data=data,user=session['username'] )

@app.route('/train_details' ,methods=['GET','POST'])
def train_details():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM train')
    data=cursor.fetchall()
    return render_template('train_details.html',data=data,user=session['username'])

@app.route('/update_train_details',methods=['GET','POST'])
def update_train_details():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    print('done')
    if request.method=='POST' and 'oldtrainno' in request.form and 'newtrainno' in request.form and 'tname' in request.form and 'arrive' in request.form and 'destination' in request.form and 'arrival_t' in request.form and 'departure_t' in request.form and 'fare' in request.form:
        old_train_no=request.form['oldtrainno']
        new_train_no=request.form['newtrainno']
        train_name=request.form['tname']
        t_arrive=request.form['arrive']
        destination=request.form['destination']
        arrival_t=request.form['arrival_t']
        departure_t=request.form['departure_t']
        fare=request.form['fare']

        print(old_train_no,new_train_no,train_name,t_arrive,destination,arrival_t,departure_t,fare)

        
        if cursor.execute('UPDATE train SET TrainNo=%s,Name=%s,Arrive=%s,Destination=%s,Arrival_Time=%s,Departure_Time=%s,Fare=%s WHERE TrainNo=%s',(new_train_no,train_name,t_arrive,destination,arrival_t,departure_t,fare,old_train_no)):
            print('Done')
            mysql.connection.commit()
            msg='Record updated of train'+str(new_train_no)
            cursor.execute('SELECT * FROM train')
            data=cursor.fetchall()
            return render_template('train_details.html',msg=msg,data=data,user=session['username'])
        else:
            msg='Invalid Info'
            print('not done')
            cursor.execute('SELECT * FROM train')
            data=cursor.fetchall()
            return render_template('train_details.html',msg=msg,data=data,user=session['username'])
    else:
        msg='Enter all details!!!'
        print('error not fill details')
        cursor.execute('SELECT * FROM train')
        data=cursor.fetchall()
        return render_template('train_details.html',msg=msg,data=data,user=session['username'])
    
@app.route('/add_train',methods=['GET','POST'])
def add_train():
    if request.method=='POST' and  'newtrainno' in request.form and 'tname' in request.form and 'arrive' in request.form and 'destination' in request.form and 'arrival_t' in request.form and 'departure_t' in request.form and 'fare' in request.form:
        new_train_no=request.form['newtrainno']
        train_name=request.form['tname']
        t_arrive=request.form['arrive']
        destination=request.form['destination']
        arrival_t=request.form['arrival_t']
        departure_t=request.form['departure_t']
        fare=request.form['fare']

        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if cursor.execute('INSERT INTO train(TrainNo, Name, Arrive, Destination, Arrival_Time, Departure_Time, Fare) VALUES (%s,%s,%s,%s,%s,%s,%s)',(new_train_no,train_name,t_arrive,destination,arrival_t,departure_t,fare)):
            cursor.connection.commit()
            print('Added')
            msg='New Record Inserted'
            cursor.execute('SELECT * FROM train')
            data=cursor.fetchall()
            return render_template('train_details.html',msg=msg,data=data,user=session['username'])
        else:
            msg='Invalid Details!!!'
            print('Invalid Details')
            cursor.execute('SELECT * FROM train')
            data=cursor.fetchall()
            return render_template('train_details.html',msg=msg,data=data,user=session['username'])
    else:
        msg='Enter all details!!!'
        print('error not fill details')
        cursor.execute('SELECT * FROM train')
        data=cursor.fetchall()
        return render_template('train_details.html',msg=msg,data=data,user=session['username'])

@app.route('/delete_train',methods=['GET','POST'])
def delete_train():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method=='POST' and 'oldtrainno' in request.form :
        old_train_no=request.form['oldtrainno']
        if cursor.execute('DELETE FROM train WHERE TrainNo=%s',(old_train_no,)):
            cursor.connection.commit()
            print('Deleted')
            msg=str(old_train_no)+' Train Removed'
            cursor.execute('SELECT * FROM train')
            data=cursor.fetchall()

            return render_template('train_details.html',msg=msg,data=data,user=session['username'])
        else:
            msg='Invalid Details!!!'
            print('Invalid Details')
            cursor.execute('SELECT * FROM train')
            data=cursor.fetchall()
            return render_template('train_details.html',msg=msg,data=data,user=session['username'])
    else:
        msg='Enter all details!!!'
        print('error not fill details')
        cursor.execute('SELECT * FROM train')
        data=cursor.fetchall()
        return render_template('train_details.html',msg=msg,data=data,user=session['username'])
    
@app.route('/user_details',methods=['GET','POST'])
def user_details():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users')
    data=cursor.fetchall()
    user=session['username']
    return render_template('user_details.html',user=user,data=data)

@app.route('/remove_user',methods=['GET','POST'])
def remove_user():
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method=='POST' and 'user_id' in request.form:
            user_id=request.form['user_id']
            if cursor.execute('DELETE FROM users WHERE ID=%s',(user_id,)):
                cursor.connection.commit()
                print('deleted')
                msg='User account '+str(user_id)+' deleted'
                cursor.execute('SELECT * FROM users')
                data=cursor.fetchall()
                user=session['username']
                return render_template('user_details.html',msg=msg,user=user,data=data)
            else:
                msg='Invalid Details!!!'
                print('Invalid Details')
                cursor.execute('SELECT * FROM users')
                data=cursor.fetchall()
                user=session['username']
                return render_template('train_details.html',msg=msg,data=data,user=session['username'])
        else:
            
            print('error not fill details')
            cursor.execute('SELECT * FROM users')
            data=cursor.fetchall()
            user=session['username']
            return render_template('user_details.html',user=user,data=data)


@app.route('/tickets_info',methods=['GET','POST'])
def tickets_info():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM bookings')
    data=cursor.fetchall()
    user=session['username']
    return render_template('ticket_details.html',user=user,data=data)

@app.route('/delete_ticket',methods=['GET','POST'])
def delete_ticket():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method=='POST' and 'ticket_id' in request.form:
        ticket_id=request.form['ticket_id']
        if cursor.execute('DELETE FROM bookings WHERE Booking_Id=%s',(ticket_id,)):
            cursor.connection.commit()
            print('deleted')
            msg='Ticket '+str(ticket_id)+' deleted'
            cursor.execute('SELECT * FROM bookings')
            data=cursor.fetchall()
            user=session['username']
            return render_template('ticket_details.html',msg=msg,user=user,data=data)
        else:
            msg='Invalid Details!!!'
            print('Invalid Details')
            cursor.execute('SELECT * FROM bookings')
            data=cursor.fetchall()
            user=session['username']
            return render_template('ticket_details.html',msg=msg,user=user,data=data)
    else:
        
        print('error not fill details')
        cursor.execute('SELECT * FROM bookings')
        data=cursor.fetchall()
        user=session['username']
        return render_template('ticket_details.html',user=user,data=data)
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('index'))




        




if __name__ == "__main__":
     app.run(debug=True)

