import sys
import psutil
import modules
import datetime

from flask_socketio import SocketIO
from flask import Flask, request, jsonify, render_template

current_pid = sys.argv[0]
for process in psutil.process_iter(['pid', 'cmdline']):
    if process.info['cmdline'] and current_pid in process.info['cmdline'] and process.info['pid'] != psutil.Process().pid:
        try:
            process.terminate()
            process.wait(timeout=5)
        except psutil.NoSuchProcess:
            pass
        except psutil.TimeoutExpired:
            process.kill()
            
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
                lastMovement = db.selectMovement("toUnderground", 1)
                
                if not lastMovement:
                    raise Exception("movements not found!")
                
                hig1, hig2 = (hig + 1) // 2, hig // 2
                toa1, toa2 = (toa + 1) // 2, toa // 2
                sab1, sab2 = (sab + 1) // 2, sab // 2

                responsible = f"{str(name).title()} | Deposito do Subsolo"
                
                first_cc = "COMLI" if lastMovement.get("CC") == "TR1" else "TR1"
                
                if hig1 > 0 or toa1 > 0 or sab1 > 0:
                    db.insertMovement(date, hig1, toa1, sab1, responsible, first_cc, 1)
                    
                if hig2 > 0 or toa2 > 0 or sab2 > 0:
                    db.insertMovement(date, hig2, toa2, sab2, responsible, "TR1" if first_cc == "COMLI" else "COMLI", 1)
            elif cc.upper() == "RECEIVE":
                noteId = data.get("noteId")
                
                if not db.matchShippingNote(noteId, hig, toa, sab):
                    raise Exception("A nenhuma nota de entraga bate com os valores informados!")
            else:
                db.insertMovement(date, hig, toa, sab, str(name).title(), cc, 0)
                
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
        host="127.0.0.1",
        port=5000,
        debug=False
    )