import os
from flask import Flask, render_template, request, redirect, jsonify, send_from_directory, session
from datetime import *
from mongoengine import *
import pytz
import pandas as pd
import json
from flask_cors import CORS
import xlrd

i=0
logged_in_users = {}
# dict = {
#     'gj':{
#         'password':'123',
#         'last_active':datetime.now()
#     },
#     'MyLiya':{
#         'password':'666',
#         'last_active':datetime.now()
#     }
# }

# connect(host="mongodb://127.0.0.1/mall", username="admin", password="password")
connect(host="mongodb://101.43.190.154/student", username="student", password="student")

class User(Document):
    username = StringField(required=True)
    email = StringField(required=True)
    mobilephone = StringField(required=True)
    password = StringField(required=True)
    last_active = DateTimeField(default=datetime.now())
    create_time = DateTimeField(default=datetime.now())

class Product(Document):
    name = StringField(required=True)
    category = StringField(required=True)
    price = FloatField(required=True)
    description = StringField()
    image = ImageField()
    stock = IntField(required=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()


# Equivalent to previous connection but explicitly states that
# it should use admin as the authentication source database

app = Flask(__name__,
            template_folder='./templates',
            static_folder='./statics',
            static_url_path='')
app.config['SECRET_KEY']='MyLiya'
app.config['TEMPORARY_FILE_DIR']='./temp'
CORS(app, supports_credentials=True)

@app.before_request
def check_login(): 
    # Check if the current user is logged in
    if request.endpoint != 'signin' and request.endpoint != 'signup' and request.endpoint != 'static' and request.endpoint != 'favicon':
        if not is_user_logged_in():
            print('User is not logged in, rederecting to the Login page.')
            return redirect('/signin')
        elif user_login_overdate():
            print('User login overdated, rederecting to the Login page.')
            return redirect('/signin')
        else:
            # Online user
            username = session.get('username')
            user = User.objects(username=username).first()
            user.last_active=session.get('last_active')
            user.save()
            logged_in_users[username]['last_active']=session['last_active']
            logged_in_users[username]['endpoint']=request.endpoint

def is_user_logged_in():
    # Check if the user is logged in based on session or other criteria
    username = session.get('username')
    print('username={} '.format(username))
    print('session.items={} '.format(session.items()))
    print('session.keys={} '.format(session.keys()))
    print('logged in users:{}'.format(logged_in_users.keys()))
    return username in logged_in_users.keys()

def user_login_overdate():
    now = datetime.now(tz=pytz.UTC)
    last_active = session['last_active']
    delta = now - last_active
    session['last_active'] = now
    if delta.seconds > 1000:
        msg='Your session has expired after 1000 seconds, you have been logged out'
        return logout(msg=msg)


@app.after_request
def process_response(response):
    ip = request.remote_addr
    url = request.path
    return response

@app.route('/admin')
def admin():
    goods_data = [{'id':'TJUFE','price':'666'},{'id':'TJUFE','price':'666'},{'id':'TJUFE','price':'666'},{'id':'TJUFE','price':'666'}]
    online_user_data=[]
    for each in logged_in_users.keys():
        user = User.objects(username=each).first()
        print('username:{} password:{}'.format(user.username,user.password))
        data={}
        data['username']=user.username
        data['password']=user.password
        data['last_active']=logged_in_users[each]['last_active']
        data['endpoint']=logged_in_users[each]['endpoint']
        online_user_data.append(data)
    users = User.objects().all()
    return render_template('admin.html',goods_data=goods_data,online_user_data=online_user_data,users=users)

@app.route('/')
def home():
    data = {'title': 'Mall', 'message': 'Welcome'}
    return render_template('home.html', data=data)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    # Render the login page template for GET requests
    if request.method == 'GET':
        return render_template('signin.html')
    # Render the login page template for POST requests
    else:
        # Get the entered username and password from the form
        username = request.form['username']
        password = request.form['password']

        # Validate the credentials (example validation)
        # The administrator
        if username == 'admin' and password == 'password':
            # Successful login, redirect to the home page
            session['username']=username
            session['last_active']=datetime.now(tz=pytz.UTC)
            logged_in_users[username]={}
            logged_in_users[username]['last_active']=session['last_active']
            logged_in_users[username]['endpoint']=request.endpoint
            return redirect('/admin')
        # Check if the user exists in the database
        user = User.objects(username=username).first()
        if user:
            if user.password == password:
                # User exists and password matches, perform login logic
                # Successful login, redirect to the home page
                session['username']=username
                session['last_active']=datetime.now(tz=pytz.UTC)
                logged_in_users[username]={}
                logged_in_users[username]['last_active']=session['last_active']
                logged_in_users[username]['endpoint']=request.endpoint
                return redirect('/')
            else:
                error_message = 'wrong password'
        else:
            error_message = 'none user'

        # Invalid credentials, show an error message
        return render_template('signin.html', error_message=error_message)
      
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Render the registration page template for GET requests
    if request.method == 'GET':
        return render_template('signup.html')
    # Render the registration page template for GET requests
    else:
        # Get the entered username, email, password, and confirm password from the form
        username = request.form['username']
        email = request.form['email']
        mobilephone = request.form['mobilephone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Perform validation checks (example validation)
        if password != confirm_password:
            error_message = 'Passwords do not match'
            return render_template('signup.html', error_message=error_message)

        # Add logic to store the user details in the database or perform further processing
        # connect(host="mongodb://127.0.0.1/mall", username="admin", password="password")
        # connect(host="mongodb://101.43.190.154/student", username="student", password="student")
        user_obj = User(username=username,email=email,mobilephone=mobilephone,password=password,create_time=datetime.now)
        user_obj.save()
        # disconnect()
        # Registration successful, redirect to the login page
        return redirect('/signin')

@app.route('/logout', methods=['POST'])
def logout(msg=""):
    if msg != "":
        print('logout_message:{}'.format(msg))
    # Perform logout actions, such as clearing the session or user data
    logged_in_users.pop(session.get('username'))
    session.clear()
    # Redirect the user to the login page or any other appropriate page
    return redirect('/signin')
     
# @app.route('/add', methods=['POST'])
# def add_user():
#     name = request.form['name']
#     email = request.form['email']
#     user = User(name=name, email=email)
#     user.save()
#     return redirect('/')

# @app.route('/edit/<id>', methods=['GET', 'POST'])
# def edit_user(id):
#     user = User.objects.get(id=id)
#     if request.method == 'POST':
#         user.name = request.form['name']
#         user.email = request.form['email']
#         user.save()
#         return redirect('/')
#     return render_template('edit_user.html', user=user)

@app.route('/delete/<username>')
def delete_user(username):
    user = User.objects(username=username).first()
    user.delete()
    return redirect('/admin')

@app.route('/products')
def products():
    products=Product.objects().all()
    # print('os.getcwd():{}'.format(os.getcwd()))
    # 'C:\Users\MyLiya\Desktop\TJUFEMall'
    for product in products:
        with open(app.config['TEMPORARY_FILE_DIR'] + "/" + str(product.id) + '.jpg', 'wb') as f:
            f.write(product.image.read())
        product.image.filename = str(product.id) + '.jpg'
    
    return render_template( 'products.html',products=products)

@app.route('/serve_image/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['TEMPORARY_FILE_DIR'], filename)

@app.route('/print_test')
def print_test():
    print("I am gonna print something...")
    
    return '<h1>Hello</h1>'


@app.route('/map')
def map():
    return render_template('map.html')

@app.route("/statistics", methods=["GET"])
def statistics():
    return render_template('statistics.html')

@app.route("/statistics/data", methods=["GET"])
def data():
   df=pd.DataFrame(pd.read_excel('./statics/data/data.xls'))
   n = df.shape[0]
   global i
   if i==n :
      i=0
   daily_data=df.get(['trade_date','open','close','low','high'])
   daily_data=daily_data.sort_values("trade_date",ascending=True)
   trade_date=list(daily_data.iloc[i])[0]
   trade_data=list(daily_data.iloc[i])[1:]
   i=i+1
   return json.dumps({
        "trade_date":trade_date,
        "trade_data":trade_data
   })

@app.route('/account', methods=['GET'])
def account():
    user=User.objects(username=session['username']).first()
    return render_template('account.html',user=user)

@app.route('/cart', methods=['GET'])
def cart():
    return render_template('cart.html')


@app.route('/details/<product_id>')
def details(product_id):
    product = Product.objects(id=product_id).first()
    product.image.filename = str(product.id) + '.jpg'
    return render_template('details.html',product=product)




if __name__ == '__main__':
    
    # app.run(host='127.0.0.1',debug=True,port=9090)
    print("app.config:{}".format(app.config))
    app.run(host='0.0.0.0',debug=True,port=9090)
    # app.run(host='1.14.105.91',port=9090)
