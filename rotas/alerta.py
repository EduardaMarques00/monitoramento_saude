from flask import Blueprint, jsonify, request
from sqlalchemy import text
from db.conexao import get_engine

bp = Blueprint("alerta", __name__, url_prefix="/api/alertas")
engine = get_engine()

@bp.route("/", methods=["GET"])
def listar():

    filtro_tipo = request.args.get("tipo", "")
    filtro_nivel = request.args.get("nivel", "")

    query = """
        SELECT *
        FROM public."Alerta"
        WHERE 1=1
    """

    params = {}

    if filtro_tipo:
        query += " AND tipo_alerta ILIKE :tipo"
        params["tipo"] = f"%{filtro_tipo}%"

    if filtro_nivel:
        query += " AND nivel_critico ILIKE :nivel"
        params["nivel"] = f"%{filtro_nivel}%"

    query += " ORDER BY data_hora DESC"

    with engine.connect() as conn:

        result = conn.execute(text(query), params)

        rows = [dict(r._mapping) for r in result]

    return jsonify(rows)

@bp.route("/", methods=["POST"])
def inserir():

    data = request.json

    with engine.begin() as conn:

        conn.execute(
            text(
                '''
                INSERT INTO public."Alerta"
                (
                    id_medicao,
                    tipo_alerta,
                    data_hora,
                    nivel_critico
                )
                VALUES
                (
                    :id_medicao,
                    :tipo_alerta,
                    :data_hora,
                    :nivel_critico
                )
                '''
            ),
            data,
        )

    return jsonify({"ok": True}), 201

@bp.route("/<int:id_alerta>", methods=["PUT"])
def atualizar(id_alerta):

    data = request.json
    data["id_alerta"] = id_alerta

    with engine.begin() as conn:

        conn.execute(
            text(
                '''
                UPDATE public."Alerta"
                SET
                    id_medicao=:id_medicao,
                    tipo_alerta=:tipo_alerta,
                    data_hora=:data_hora,
                    nivel_critico=:nivel_critico
                WHERE id_alerta=:id_alerta
                '''
            ),
            data,
        )

    return jsonify({"ok": True})

@bp.route("/<int:id_alerta>", methods=["DELETE"])
def remover(id_alerta):

    with engine.begin() as conn:

        conn.execute(
            text(
                '''
                DELETE FROM public."Alerta"
                WHERE id_alerta=:id_alerta
                '''
            ),
            {"id_alerta": id_alerta},
        )

    return jsonify({"ok": True})

@bp.route("/relatorio", methods=["GET"])
def relatorio():

    with engine.connect() as conn:

        result = conn.execute(
            text(
                '''
                SELECT
                    nivel_critico,
                    COUNT(*) AS total
                FROM public."Alerta"
                GROUP BY nivel_critico
                ORDER BY total DESC
                '''
            )
        )

        return jsonify(
            [dict(r._mapping) for r in result]
        )