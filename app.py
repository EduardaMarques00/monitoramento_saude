from flask import Flask, send_from_directory
from rotas.paciente import bp as bp_paciente
from rotas.medicao import bp as bp_medicao

app = Flask(__name__)
app.register_blueprint(bp_paciente)
app.register_blueprint(bp_medicao)


@app.route("/")
def index():
    return send_from_directory("paginas", "index.html")


@app.route("/<path:arquivo>")
def pagina(arquivo):
    return send_from_directory("paginas", arquivo)


if __name__ == "__main__":
    app.run(debug=True)