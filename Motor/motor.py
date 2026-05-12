from flask import Flask

app = Flask(__name__)   

@app.route("/motor/start")
def motor_start():
    print("Motor läuft")
    return "Motor läuft"
@app.route("/motor/stop")
def motor_stop():
    print("Motor stop")
    return "Motor stop"

app.run(host="0.0.0.0", port=5000)
