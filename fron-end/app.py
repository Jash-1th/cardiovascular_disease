from flask import Flask,render_template, url_for, redirect, request, session
import mysql.connector,os ,re , joblib
import pandas as pd
import os
# Import libraries
import matplotlib.pyplot as plt
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


app = Flask(__name__)
app.secret_key = 'admin'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306",
    database='db'
)

mycursor = mydb.cursor()


def executionquery(query,values):
    mycursor.execute(query,values)
    mydb.commit()
    return

def retrivequery1(query,values):
    mycursor.execute(query,values)
    data = mycursor.fetchall()
    return data

def retrivequery2(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        c_password = request.form['c_password']
        if password == c_password:
            query = "SELECT UPPER(email) FROM users"
            email_data = retrivequery2(query)
            email_data_list = []
            for i in email_data:
                email_data_list.append(i[0])
            if email.upper() not in email_data_list:
                query = "INSERT INTO users (name,email, password) VALUES ( %s, %s, %s)"
                values = (name,email, password)
                executionquery(query, values)
                return render_template('login.html', message="Successfully Registered!")
            return render_template('register.html', message="This email ID is already exists!")
        return render_template('register.html', message="Conform password is not match!")
    return render_template('register.html')

@app.route('/login',methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = []
        for i in email_data:
            email_data_list.append(i[0])

        if email.upper() in email_data_list:
            query = "SELECT UPPER(password) FROM users WHERE email = %s"
            values = (email,)
            password__data = retrivequery1(query, values)
            if password.upper() == password__data[0][0]:
                global user_email
                user_email = email

                return render_template('home.html')
            return render_template('login.html', message= "Invalid Password!!")
        return render_template('login.html', message= "This email ID does not exist!")
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

import numpy as np
@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == "POST":
        try:
            # Get input from form
            gender = int(request.form['gender'])  # Male=1, Female=0 (binary encoding)
            height = int(request.form['height'])
            weight = int(request.form['weight'])
            ap_hi = int(request.form['ap_hi'])  # Systolic BP
            ap_lo = int(request.form['ap_lo'])  # Diastolic BP
            cholesterol = int(request.form['cholesterol'])  # 1: normal, 2: above normal, 3: well above normal
            gluc = int(request.form['gluc'])  # 1: normal, 2: above normal, 3: well above normal
            smoke = int(request.form['smoke'])  # 1: yes, 0: no
            alco = int(request.form['alco'])  # 1: yes, 0: no
            active = int(request.form['active'])  # 1: yes, 0: no

            # Combine input values into an array
            input_data = np.array([[gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active]])
            
            # Load saved model and scaler
            xgb_model = joblib.load('xgboost_model.joblib')  # Load XGBoost model
            scaler = joblib.load('cardio_model.joblib')  # Load MinMaxScaler
            
            # Scale the input data using the same scaler used during training
            input_scaled = scaler.transform(input_data)

            # Make prediction
            prediction = xgb_model.predict(input_scaled)
            print(prediction)

            # Interpret the prediction
            if prediction[0] == 0:
                result = 'No Cardiovascular Disease Detected'
            else:
                result = 'Risk of Cardiovascular Disease'

            # Return the prediction result in the template
            return render_template('prediction.html', result=result)

        except Exception as e:
            # Catch any errors during prediction and return an error message
            print(f"Error: {e}")
            return render_template('prediction.html', result="Error in prediction process. Please try again.")

    # If it's a GET request, show the empty form
    return render_template('prediction.html')



@app.route('/model', methods=['GET', 'POST'])
def model():
    if request.method == 'POST':
        algorithm = request.form["algo"]
        if algorithm == "0":
            msg = 'Please select an algorithm.'
            return render_template('model.html', msg=msg)

        if algorithm == "1":
            accuracy=74
            msg = f'Accuracy for Stacking Classifier is {accuracy}%'
        elif algorithm == "2":
            accuracy=74
            msg = f'Accuracy for XGBoost Classifier is {accuracy}%'
        elif algorithm == "3":
            accuracy=72
            msg = f'Accuracy for Random Forest Classifier is {accuracy}%'
        elif algorithm == "4":
            accuracy=65
            msg = f'Accuracy for Convolutional Neural Network (CNN) is {accuracy}%'
        elif algorithm == "5":
            accuracy=66
            msg = f'Accuracy for Long Short-Term Memory (LSTM) is {accuracy}%'
        elif algorithm == "6":
            accuracy=65
            msg = f'Accuracy for Recurrent Neural Network (RNN) is {accuracy}%'
        elif algorithm == "7":
            accuracy=65
            msg = f'Accuracy for Gated Recurrent Unit (GRU) is {accuracy}%'
        else:
            msg = 'Invalid selection.'
            return render_template('model.html', msg=msg)

        return render_template('model.html', msg=msg, accuracy=accuracy)

    return render_template('model.html')




    
if __name__ == '__main__':
    app.run(debug=True)