import pickle
from datetime import datetime
from threading import Thread

import cv2
import imutils
from flask import Flask, Response, redirect, render_template, request
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy

from facial_req import recognition
from headshots import take_photo

#from motion import function_name
app = Flask(__name__)

camera=cv2.VideoCapture(0)
app.config['SECRET'] = 'secret!'
socketio = SocketIO(app,cors_allowed_origins="*")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends'
#initialize the database
db = SQLAlchemy(app)
app.app_context().push()
#creating Db model
class Friends(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    date_created = db.Column(db.DateTime,default=datetime.utcnow)
    def __repr__(self):
        return '<Name %r>' % self.id

class Logs(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    date_created = db.Column(db.DateTime,default=datetime.utcnow)
    def __repr__(self):
        return '<Name %r>' % self.id


detect=True


    

def register_log(names):
    global app
    app.app_context().push()
    #query = db.session.query(Friends).filter(Friends.name==names).first()
    if names=="Unknown" :
        print("Unauthorized Access")
        socketio.send("!")
    else:
        socketio.send("#")
        #led.HIGH
    global db
    new_register = Logs(name = names)
    db.session.add(new_register)
    db.session.commit()


def generate_frames():
    global detect
    print("A client Connected For video ")
    while True:
        
        
        
        
        #if function_name():
            #detect=True
        
        
        
        
        
        ## read the camera frame
        success,frame=camera.read()
        
        #socket.send("Humidity = "+h)
        #socket.send("Temp = "+t)
        if not success:
            break
        else:
            if detect:
                frame,names = recognition(frame)
                if names:
                    register_log(names[0])
                    
                    t = datetime.now()
                    tt = t.strftime("%H:%M:%S")
                    socketio.send("${name} {time}".format(name=names[0],time=tt))
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

            yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# When a Client Connected
@socketio.on('connect')
def on_connect():
    print('A client connected')

#When a Client Disconnected
@socketio.on('disconnect')
def on_disconnect():
    print('A client disconnected')

#Messageing 
@socketio.on('message')
def on_message(message):
    print('Received message: ' + message)
    if message=="R":
        print("Robot Move Right")
    if message=="O":
        global detect
        detect = False
        print("Detection Off")
    if message=="D":
        detect = True
        print("Detection On")

    send(message)


    


#default Index.html page shows.
@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/register', methods=["POST","GET"])
def register():
    if request.method=='POST':
        name = request.form['email']
        new_register = Friends(name = name)
        take_photo(name,camera)
        socketio.send("Photo taking Done")
        
        try:
            db.session.add(new_register)
            db.session.commit()
            return redirect('/register_done')
        except:
            return redirect('/register_done')
    else:
        return render_template('./register.html')

@app.route('/user')
def user():
    fnd = Friends.query.order_by(Friends.date_created)
    return render_template('./user.html',data = fnd)

@app.route('/logs')
def user_():
    fnd = Logs.query.order_by(Logs.date_created)
    return render_template('./logs.html',data = fnd)


@app.route('/register_done')
def register_done():

    return render_template('./close.html')

@app.route('/del_logs/<int:fnd>',methods=['GET','POST'])
def del_logs(fnd):
    if request.method=='POST':
        friend = Logs.query.get_or_404(fnd)
        db.session.delete(friend)
        db.session.commit()
        return redirect("/logs")
    else:
        return redirect("/")

@app.route('/del_fnds/<int:fnd>',methods=['GET','POST'])
def del_fnds(fnd):
    if request.method=='POST':
        friend = Friends.query.get_or_404(fnd)
        db.session.delete(friend)
        db.session.commit()
        return redirect("/user")
    else:
        return redirect("/")


@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    socketio.run(app,host="0.0.0.0")
