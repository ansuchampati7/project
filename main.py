from logging import debug
from os import name
from flask import Flask , redirect , url_for
from flask import request , session
from flask.templating import render_template
from flask.helpers import make_response
import pymysql as sql
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from getpass import getpass



app = Flask(__name__)

name,em,pas = "","",""

def database():
    db = sql.connect(host= "localhost" , port = 3306 , user = "root" , password = "" , database = "project")
    cursor = db.cursor()
    return db , cursor


@app.route("/")
def fpage():
    if request.cookies.get("islogin"):
        return render_template("afterlogin.html")
    return render_template("frontpage.html")

@app.route("/signin/")
def lpage():
    if request.cookies.get("islogin"):
        return render_template("afterlogin.html")
    return render_template("signin.html")


@app.route("/signin/aftersignin/", methods = ['GET', 'POST'] )
def apage():
    global name,em,pas

    if request.method == 'GET' :
        return redirect(url_for("signin.html"))
    else :
        em = request.form.get("email")
        pas = request.form.get("password")
        name = request.form.get("username")
        db , cursor = database()
        cmd = f"select email from flaskproject where email='{em}' "
        cursor.execute(cmd)
        data = cursor.fetchone()
        if data:
            msg = "you have already registered please go to login page"
            return render_template("signin.html", msg = msg)
        else:
            msg = MIMEMultipart()
            msg['from'] = "www.ansuman666@gmail.com"
            msg['to'] = em
            msg['subject'] = "verification link"

            plain = """
            <html>
            <body>
            <h1> hello ...... plz click on the link bellow for verification </h1> 
            <a href = "localhost/verification/"> Click Here </a>
            <img src = 'https://www.wallpaperbetter.com/wallpaper/519/942/401/good-morning-coffee-cup-720P-wallpaper.jpg'>
            </body>
            </html>

            """
            
            p = MIMEText(plain , "html")
            msg.attach(p)

            host = "smtp.gmail.com"
            port = 465
            try:
                with smtplib.SMTP_SSL(host,port, context = ssl.create_default_context()) as server:
                    passwd = getpass("password nigga--->")
                    server.login(msg['from'], passwd)
                    server.sendmail(msg['from'],msg['to'], msg.as_string())
            except Exception as error :
                msg = "There is an error plz try again"
                return render_template("signin.html", msg = msg)
            else :
                msg="msg has been sent plz check ur email"
                return render_template("signin.html", msg = msg)


@app.route("/verification/")
def verify():
    global name,em,pas
    db , cursor = database()
    cmd = f"insert into flaskproject values('{name}' , '{em}' , '{pas}')"
    cursor.execute(cmd)
    db.commit()
    msg = 'you have registed successfully plz close this tab and go to the login page '    
    return render_template("signin.html", msg = msg)


@app.route("/login/")
def spage():
    return render_template("login.html")

@app.route("/afterlogin/" , methods = ['GET', 'POST'] )
def alpage():
    if request.method == "GET" :
        return render_template('login.html')
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        db , cursor = database()
        cmd = f"select * from flaskproject where email='{email}' and password= '{password}' "
        cursor.execute(cmd)
        data = cursor.fetchone()
        if data:
            resp = make_response(render_template("afterlogin.html"))
            resp.set_cookie('email',email)
            resp.set_cookie('islogin','true')
            return resp
        else :
            msg = "invalid user id or password"
            return render_template("login.html" , msg=msg )

@app.route("/logout/" , methods = ['GET', 'POST'] )
def logout():
    resp = make_response(render_template("login.html"))
    resp.delete_cookie("email")
    resp.delete_cookie("islogin")
    return resp

@app.route("/content/" , methods = ['GET', 'POST'] )
def content():
    return render_template("content.html")

@app.route("/weather/" , methods = ['GET', 'POST'] )
def weather():
    return render_template("weather.html")

@app.route("/afterweather/" , methods = ['GET', 'POST'] )
def afterweather():
    if request.method == "GET" :
        return render_template("weather.html")
    else:
        city = request.form.get("city")
        
        key = "dca0e1371924c82e8619e55d4b32a339"
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}"
        resp = requests.get(url)
        if resp.status_code==200:
            data=resp.json()
            description=data['weather'][0]['description']
            temp = data['main']['temp']
            min_temp=data['main']['temp_min']
            max_temp=data['main']['temp_max']
            pressure=data['main']['pressure']
            humidity=data['main']['humidity']
            speed=data['wind']['speed']
            val=[description,temp,min_temp,max_temp,pressure,humidity,speed]
            var=["description","temperature","minimum_temperature","maximum_temperature","pressure","humidity","speed"]
            d =  dict(zip(var,val))
            z = data['weather'][0]['icon']
            return render_template("afterweather.html" , z=z ,d = d)
        else :
            msg="servers are fucked up"
            return render_template("afterweather.html" , msg)

@app.route("/corona/" , methods = ['GET', 'POST'])
def corona():
    return render_template("corona.html")

@app.route("/aftercorona/" , methods = ['GET', 'POST'])
def aftercorona():
    if request.method == "GET" :
        return render_template("corona.html")
    else :
        Coronacity  = request.form.get("Coronacity").capitalize()
        url = "https://covid-19-coronavirus-statistics.p.rapidapi.com/v1/total"
        querystring = {"country":Coronacity}
        headers = {
            'x-rapidapi-host': "covid-19-coronavirus-statistics.p.rapidapi.com",
            'x-rapidapi-key': "ca49099f4cmshb472e84bfa9d490p175d79jsnf61fee55d4e9"
            }
        response = requests.request("GET", url, headers=headers, params=querystring)
        x = response.json()

        url = "https://vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com/api/news/get-coronavirus-news/0"

        headers = {
            'x-rapidapi-host': "vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com",
            'x-rapidapi-key': "ca49099f4cmshb472e84bfa9d490p175d79jsnf61fee55d4e9"
            }
        response = requests.request("GET", url, headers=headers)
        e = response.json()

        title=e['news'][0]['title']
        content= e['news'][0]['content']
        pubDate = e['news'][0]['pubDate'] 
        link = e['news'][0]['link']
        e = e['news'][0]['urlToImage']

        if x['statusCode'] == 200:
            return render_template("aftercorona.html", x=x , e=e , title = title , content= content, pubDate=pubDate, link=link )
        else :
            return render_template("corona.html" )




app.run(port=80 , debug= True)