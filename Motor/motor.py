from flask import Flask

app = Flask(__name__)   # <-- MUSS vor allen @app.route stehen

@app.route("/motor/start")
def motor_start():
    print("Motor läuft")
    return "Motor läuft"

app.run(host="0.0.0.0", port=5000)
