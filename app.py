# importing Flask and other modules
import warnings
from flask import Flask, request, render_template, Response, session, redirect
import phonenumbers
import cv2
import os
import json
import mysql.connector
from mysql.connector import Error
from truecallerpy import search_phonenumber
import urllib.request  # to download image
from phonenumbers import carrier
#db pass
dbpassword = 'Demaan@123'
api = "a1i0H--a7irLDkCFyUdgq3_j6_hWe3XA5k6kGRFdl4JrQzU6_ZcaWPUxd6TgSu57"

# assigning Global Variable
global capture
capture = 0
global xyz
xyz = 0
global numb
numb = 'hello' 

warnings.filterwarnings('ignore')
# instatiate flask app
app = Flask(__name__)
# you can set any secret key but remember it should be secret
app.secret_key = 'ItShouldBeAnythingButSecret'
# user = {"username": "abc", "password": "xyz"}

# make shots directory to save pics
try:
    os.mkdir('static/captures')
except OSError as error:
    pass

# Load pretrained face detection model
net = cv2.dnn.readNetFromCaffe(
    'static/deploy.prototxt.txt',
    'static/res10_300x300_ssd_iter_140000.caffemodel')
# capture live camera
camera = cv2.VideoCapture(0)


# generate frame by frame from camera
def gen_frames():
    global capture
    while True:
        success, frame = camera.read()
        if success:
            if (capture):
                capture = 0
                path = "static/captures/suspect.png"
                cv2.imwrite(path, frame)
                camera.release()
                cv2.destroyAllWindows()
                inp = 3
                if inp == 3:
                    num = ''
                    mailid = ''
                    info(num, mailid, inp)
            try:
                success, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass


# *********************************************************** Some Functions ***********************************************************
def true(num):
    id = api
    # print(num)
    df = search_phonenumber(num, "IN", id)
    try:
        name = df['data'][0]['name']
    except:
        name = ' '
        # print(name)
    try:
        mail = df['data'][0]['internetAddresses'][0]['id']
    except:
        mail = ' '
    # print(mail)
    try:
        add = df['data'][0]['addresses'][0]['city'] + ", " + df['data'][0][
            'addresses'][0]['address']
    except:
        add = ' '
    # print(add)
    try:
        link = df['data'][0]['image']
    except:
        link = 'https://icon-library.com/images/unknown-person-icon/unknown-person-icon-10.jpg'
    try:
        age = df['data'][0]['birthday']
    except:
        age = ' '
    f = open('static/imgs/user_img.png', 'wb')
    f.write(urllib.request.urlopen(link).read())
    f.close()
    carr = df['data'][0]['phones'][0]['carrier']
    # image = Image.open("static/imgs/user_img.png")
    show(name, num, mail, age, add, carr)


# Convert binary data to proper format and write it on Hard Disk
def write_file(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)


# function for print output


def show(name, number, mail, age, address, carr):
    dict1 = {
        'data': {
            'Name': name,
            'Number': number,
            'MailId': mail,
            'DOB': age,
            'Address': address,
            'Carrier': carr
        }
    }
    out_file = open("static/userData.json", "w")
    json.dump(dict1, out_file)
    out_file.close()
    return dict1


# ***********************************************************error handling function for database connection***********************************************************
def info(num, mailid, inp):
    def output(query):
        cursor.execute(query)
        myresult = cursor.fetchall()
        result = myresult[0]
        # print(result)
        # print output of our search
        
        # assigning data to var
        name = result[1]
        number = result[2]
        mail = result[3]
        age = result[4]
        address = result[5]
        pic = result[6]
        # print(type(number))
        if number !='9999999999':
            if len(number) == 10:
                number = "+91" + number
            elif len(number) == 12:
                number = "+" + number
            else:
                number = number
            service_provider = phonenumbers.parse(number)
            carr = carrier.name_for_number(service_provider, 'en')
        
        write_file(pic, 'static/imgs/user_img.png')
        # print(name, number, mail, age, address,carr)
        # image = Image.open("static/imgs/user_img.png")
        show(name, number, mail, age, address, carr)
    try:
        # make connection with database
        connection = mysql.connector.connect(host='localhost',
                                             database='engineers',
                                             user='root',
                                             password=dbpassword)

        if connection.is_connected():
            # db_Info = connection.get_server_info()
            #print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            if inp == 1 or inp == 2:
                try:
                    # conditions for our chhose query
                    if mailid != 'xyz@gmail.com':
                        # print(mailid)
                        # query = f"SELECT * FROM peoples WHERE mail LIKE '%{mailid}%'"
                        query = f"SELECT * FROM peoples WHERE mail LIKE '{mailid}'"
                        # print(query)
                        output(query)
                    elif mailid == 'xyz@gmail.com' and num != '9999999999':
                        # exception due to country region
                        try:
                            if num[:3] == '+91':
                                query = f"SELECT * FROM peoples WHERE number LIKE '%{num[3:]}%'"
                                output(query)
                            elif len(num) == 10:
                                query = f"SELECT * FROM peoples WHERE number LIKE '%{num}%'"
                                output(query)
                        except:
                            query = f"SELECT * FROM peoples WHERE number LIKE '%{num[3:]}%'"
                            output(query)
                    elif num != '9999999999' and mailid != 'xyz@gmail.com':
                        query = f"SELECT * FROM peoples WHERE number LIKE '%{num}%'"
                        output(query)
                except:
                    xyz = 1
                    if xyz == 1:
                        # import loading
                        true(num[3:])
            elif inp == 3:
                from deepface import DeepFace
                try:
                    id = 1
                    while True:
                        query = f"SELECT * FROM peoples WHERE id LIKE '%{id}%'"
                        # to run query
                        cursor.execute(query)
                        myresult = cursor.fetchall()
                        result = myresult[0]
                        img = result[6]
                        write_file(img, 'static/imgs/user_img.png')
                        im1 = cv2.imread("static/imgs/user_img.png")
                        im2 = cv2.imread("static/captures/suspect.png")
                        results_img = DeepFace.verify(im1, im2)
                        # print(results_img['verified'])
                        # print(id)
                        if results_img['verified'] == [True]:
                            query = f"SELECT * FROM peoples WHERE id LIKE '%{id}%'"
                            # print("Sucesss")
                            # output(query)
                            break
                        else:
                            id = id + 1
                    # output(query)
                except:
                    numb = "suspect not available in database"
                    return redirect('/error')
    except Error as e:
        numb = ("Error while connecting to MySQL", e)
        return redirect('/error')
    finally:
        # colse our server
        if connection.is_connected():
            cursor.close()
            connection.close()


# ***********************************************************  ***********************************************************
def output(input, inp):
    if inp == 1:
        mailid = 'xyz@gmail.com'
        # getting input number or mail id
        try:
            # enter number with region codes
            num2 = str(input)
            #num = "+918963002842"
            # Parsing String to Phone number
            if len(num2) == 10:
                num = "+91" + num2
            elif len(num2) == 12:
                num = "+" + num2
            else:
                num = num2
            # number = num
            # print(num)
            phone_number = phonenumbers.parse(str(num))
            valid = phonenumbers.is_valid_number(phone_number)
            if valid == True:
                #num = '+918963002842'
                if len(num2) >= 13:
                    num = num2[:12]
            else:
                numb = "Mobile Number is not Valid"
                # print(numb)
        except:
            num = '9999999999'
            mailid = 'xyz@gmail.com'
    if inp == 2:
        mailid = str(input)
        num = '9999999999'
        #mailid = ''
        if mailid == '':
            mailid = 'xyz@gmail.com'
    info(num, mailid, inp)


with open('static/pass.json', 'r') as c:
    user = json.load(c)["pass"]
# A decorator used to tell the application
# which URL is associated function


@app.route('/home', methods=["GET", "POST"])
# @app.route('/home', methods =["GET", "POST"])
def IN():
    if ('user' in session and session['user'] == user['username']):
        if request.method == "POST":
            global num
            # getting input with name = fname in HTML form
            num = request.form.get("mnumber")
            # getting input with name = lname in HTML form
            email = request.form.get("Email")
            # print('num is:', num)
            # print('mail is:', email)
            if len(num) != 0:
                # print(email)
                inp = 1
                num = str(num)
                # print(num)
                output(num, inp)
            elif len(email) != 0:
                inp = 2
                # print(email)
                # print(inp)
                output(email, inp)
            return redirect('/result')
        return render_template("index.html")


@app.route('/face')
def cam():
    return render_template('cam.html')


@app.route('/video')
def video():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/requests', methods=['POST', 'GET'])
def tasks():
    global camera
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture = 1
    with open('static/userData.json', 'r') as c:
        data = json.load(c)["data"]
    return render_template("output.html", data=data)


@app.route('/result')
def out():
    with open('static/userData.json', 'r') as c:
        data = json.load(c)["data"]
    return render_template("output.html", data=data)



@app.route('/error', methods=['POST', 'GET'])
def error():
    with open('static/error.json', 'r') as c:
        error = json.load(c)["error"]
    return render_template('error.html',error=error)

@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def login():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        if username == user['username'] and password == user['password']:

            session['user'] = username
            return redirect('/home')

        # if the username or password does not matches
        return "<h1>Wrong username or password</h1>"

    return render_template("login.html")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
