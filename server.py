import os
import dotenv
import modules
import datetime

from flask_socketio import SocketIO
from flask import Flask, request, jsonify, render_template, abort, redirect, url_for

db = modules.DBCore()

app = Flask(__name__)

Socket = SocketIO(
    app,
    async_mode="eventlet",
    ping_interval=25,
    ping_timeout=60,
    cors_allowed_origins="*"
)

with app.app_context():
    print("> Server initiated successfully!")

type_dict = {
    "BOX": "Caixas",
    "ROL": "Rolos",
    "GAL": "Galões"
}

dotenv_file = dotenv.find_dotenv()

@app.before_request
def firewall():
    data = request.get_data(as_text=True)

    if len(data) > 100_000:
        abort(413)

    # if request.headers.get("X-Device-Token") != MY_PHONE_TOKEN:
    #     abort(403)


@app.route("/environment", methods=["GET"])
def environment():
    return render_template("env.html", **{"env": dotenv.dotenv_values(dotenv.find_dotenv())})


@app.route("/update_env", methods=["POST"])
def update_env():
    data = request.form
    for (var, value) in data.items():
        dotenv.set_key(dotenv_file, var, value)
    return redirect(url_for('environment'))

@app.route("/", methods=["GET", "POST"])
def insert():
    if request.method == "GET":
        values = {}

        for result in db.selectStock("ALMOX"):
            id = result.get("id")

            itemValues = {
                "unityType": type_dict.get(result.get("unityType")),
                "quantity": result.get("quantity")
            }

            if id == 1322:
                values["hig"] = itemValues
            elif id == 1323:
                values["toa"] = itemValues
            elif id == 1324:
                values["sab"] = itemValues

        return render_template("insert.html", **values)
    elif request.method == "POST":
        try:
            data = request.form

            cc = str(data.get("CC")).upper()
            name = data.get("name")

            hig = float(data.get("hig"))
            toa = float(data.get("toa"))
            sab = float(data.get("sab"))

            if hig < 0 or toa < 0 or sab < 0:
                raise Exception("Valores negativos não são permitidos!")

            if not name:
                return jsonify({
                    "message": "Value not passed!"
                }), 400

            date = datetime.datetime.now().strftime("%d/%m/%y")

            if cc.upper() == "UNDERGROUND":
                lastMovement = db.selectMovement(datetime.datetime.now().replace(
                    day=1).strftime("%Y-%m-%d"), datetime.datetime.now().strftime("%Y-%m-%d"))

                if not lastMovement:
                    raise Exception("movements not found!")

                hig1, hig2 = (hig + 1) // 2, hig // 2
                toa1, toa2 = (toa + 1) // 2, toa // 2
                sab1, sab2 = (sab + 1) // 2, sab // 2

                responsible = f"{str(name).title()} | Deposito do Subsolo"

                first_cc = "COMLI" if lastMovement.get(
                    "CC") == "TR1" else "TR1"

                if hig1 > 0 or toa1 > 0 or sab1 > 0:
                    db.insertMovement(date, hig1, toa1, sab1,
                                      responsible, first_cc, 1)

                if hig2 > 0 or toa2 > 0 or sab2 > 0:
                    db.insertMovement(
                        date, hig2, toa2, sab2, responsible, "TR1" if first_cc == "COMLI" else "COMLI", 1)
            elif cc.upper() == "RECEIVE":
                noteId = data.get("noteId")

                if not db.matchShippingNote(noteId, hig, toa, sab):
                    raise Exception(
                        "Nenhuma nota de entrega bate com os valores informados!")
            else:
                db.insertMovement(date, hig, toa, sab,
                                  str(name).title(), cc, 0)

            return jsonify({
                "message": "Registrado com sucesso!"
            }), 200
        except Exception as e:
            return jsonify({
                "message": f"Error: {e}"
            }), 400


if __name__ == "__main__":
    Socket.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False
    )
