from flask import Flask, send_from_directory
from rotas.paciente import bp as bp_paciente
from rotas.medicao import bp as bp_medicao
from rotas.consulta import bp as bp_consulta
from rotas.alerta import bp as bp_alerta
from rotas.prescricao import bp as bp_prescricao
from rotas.notificacao import bp as bp_notificacao

app = Flask(__name__)
app.register_blueprint(bp_paciente)
app.register_blueprint(bp_medicao)
app.register_blueprint(bp_consulta)
app.register_blueprint(bp_alerta)
app.register_blueprint(bp_prescricao)
app.register_blueprint(bp_notificacao)

@app.route("/")
def index():
    return send_from_directory("paginas", "index.html")

@app.route("/<path:arquivo>")
def pagina(arquivo):
    return send_from_directory("paginas", arquivo)

if __name__ == "__main__":
    app.run(debug=True)
