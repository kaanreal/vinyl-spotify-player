from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # GANZ WICHTIG


@app.route("/motor/start")
def motor_start():
    print("Motor läuft")
    return "Motor läuft"
@app.route("/motor/stop")
def motor_stop():
    print("Motor stop")
    return "Motor stop"

app.run(host="0.0.0.0", port=5000)
