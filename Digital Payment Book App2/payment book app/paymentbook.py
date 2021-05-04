from flask import Flask, render_template,request,flash,redirect,url_for,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_bcrypt import Bcrypt

app = Flask(__name__)

#connecting app to database
app.config['MYSQL_HOST'] = "remotemysql.com"
app.config['MYSQL_USER'] = "Gmvi0rRnzg"
app.config['MYSQL_PASSWORD'] = "MBH8SSrAiN"
app.config['MYSQL_DB'] = "Gmvi0rRnzg"

mysql = MySQL(app)
app.secret_key = 'x' 

#password hasing
bcrypt = Bcrypt(app)




@app.route('/')

def home():
    if session['is_retailer'] == 0:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT purchase_id,user_id,item_name, price, amount_paid, purchase_date  FROM Purchase WHERE user_id = % s",[session['user_id']])
        purchase_details = cursor.fetchall()
        print(purchase_details)
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT purchase_id,user_id,item_name, price, amount_paid, purchase_date FROM Purchase")
        purchase_details = cursor.fetchall()
        print(purchase_details)
    
   
    return render_template('home.html',purchase_details=purchase_details,username=session['username'],role=session['is_retailer'])


@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
        x = [username,email,hash_password]
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO Users(username,email,password) VALUES(% s,% s,% s)',(username,email,hash_password))
        mysql.connection.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE email = % s',[email])
        user = cursor.fetchone()
        print(user)
        
        if user and bcrypt.check_password_hash(user[3],password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_retailer'] = user[4]
            return redirect(url_for('home'))
        else:
            flash('Log in Unsuccessful. Please check username and password', 'danger')
        
    
    return render_template("login.html")



@app.route('/logout',methods=['POST','GET'])

def logout():
   session.pop('user_id',None)
   session.pop('username',None)
   return redirect(url_for('login'))
    
  
    




@app.route('/addpurchase',methods=['POST','GET'])

def addpurchase():
    if session['is_retailer'] == 1:
        
        
        if request.method == 'POST':
            customer = request.form['customer']
            item = request.form['item']
            price = request.form['price']
            purchase_date = request.form['purchase_date']
            amount_paid = request.form['amount_paid']
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO Purchase(user_id,item_name,price,purchase_date,amount_paid) VALUES(% s,% s,% s,% s, % s)",[customer,item,price,purchase_date,amount_paid])
            mysql.connection.commit()
            return redirect(url_for('home'))
        
    
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE is_admin = 0")
        customers = cursor.fetchall()
   
        return render_template('addpurchase.html',customers = customers)
    
    return redirect(url_for('home'))


@app.route('/updatepurchase/<int:id>',methods=['POST', 'GET'])
def updatepurchase(id):
    if session['is_retailer'] == 1:
        
        
        if request.method == 'POST':
            
            item = request.form['item']
            price = request.form['price']
            purchase_date = request.form['purchase_date']
            amount_paid = request.form['amount_paid']
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE Purchase SET item_name = %s, price = %s, amount_paid = %s, purchase_date = %s WHERE purchase_id = %s ",[item,price,amount_paid,purchase_date,id])
            mysql.connection.commit()
            return redirect(url_for('home'))
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Purchase WHERE purchase_id = %s",[id])
        purchase = cursor.fetchone()
        
        
        return render_template('updatepurchase.html',purchase=purchase)
    
@app.route('/deletepurchase/<int:id>',methods=['POST','GET'])
def deletepurchase(id):
    if session['is_retailer']==1:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Purchase WHERE purchase_id = %s",[id])
        cursor.execute("DELETE FROM Payments WHERE purchase_id  = %s",[id])
        mysql.connection.commit()
        return redirect(url_for('home'))
    






@app.route('/displaypurchase')
def displaypurchase():
    if session['is_retailer'] == 0:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT purchase_id,user_id,item_name, price, amount_paid, purchase_date  FROM Purchase WHERE user_id = % s",[session['user_id']])
        purchase_details = cursor.fetchall()
        print(purchase_details)
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT purchase_id,user_id,item_name, price, amount_paid, purchase_date FROM Purchase")
        purchase_details = cursor.fetchall()
        print(purchase_details)
    
   
    return render_template('displaypurchase.html',purchase_details=purchase_details,username=session['username'])


@app.route('/addpayment',methods=['POST','GET'])

def addpayment():
    if request.method == 'POST':
        
        purchase_id = request.form['purchase_id']
        amountpaid = request.form['amount_paid']
        
        payment_date = request.form['payment_date']
       
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Payments(purchase_id, amount_paid, payment_date) VALUES(% s,% s,% s)",[purchase_id,amountpaid,payment_date])
        cursor.execute("UPDATE Purchase SET amount_paid=amount_paid + % s WHERE purchase_id = % s",[amountpaid,purchase_id])
        mysql.connection.commit()
        return redirect(url_for('home'))
  
        
    return render_template('addpayment.html') 
    
@app.route('/pendingpayments')

def pendingpayments():
    if session['is_retailer'] == 0:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT purchase_id,user_id,item_name, price, amount_paid, purchase_date FROM Purchase WHERE amount_paid<price AND user_id = % s",[session['user_id']])
        pending_payments = cursor.fetchall()
        print('Pending Payments : ',pending_payments)
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT purchase_id,user_id,item_name, price, amount_paid, purchase_date FROM Purchase WHERE amount_paid<price")
        pending_payments = cursor.fetchall()
        print('Pending Payments : ',pending_payments)
    
    
    return render_template('pending_payments.html',pending_payments=pending_payments,username=session['username'],role=session['is_retailer'])

@app.route('/paymentdetails/')

def paymentdetails():
    if session['is_retailer'] == 0:
     cursor = mysql.connection.cursor()
     cursor.execute("SELECT * FROM Payments WHERE purchase_id IN (SELECT purchase_id FROM Purchase WHERE user_id = % s)",[session['user_id']])
     payment_details = cursor.fetchall()
    else:
      cursor = mysql.connection.cursor()
      cursor.execute("SELECT * FROM Payments")
      payment_details = cursor.fetchall() 
    
    return render_template('paymentdetails.html',payments=payment_details)

@app.route('/contact')

def contact():
    return render_template('contact.html')








if __name__ == '__main__':
    app.run(debug=True)