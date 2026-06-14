from flask import Blueprint, jsonify, request
from sqlalchemy import text
from db.conexao import get_engine

bp = Blueprint("medicao", __name__, url_prefix="/api/medicoes")
engine = get_engine()


@bp.route("/", methods=["GET"])
def listar():
    filtro_paciente = request.args.get("paciente", "")
    filtro_tipo = request.args.get("tipo", "")
    query = """
        SELECT m.*, u.nome_completo
        FROM public."Medicao" m
        LEFT JOIN public."Paciente" p ON p.id_usuario = m.id_paciente
        LEFT JOIN public."Usuario" u ON u.id = p.id_usuario
        WHERE 1=1
    """
    params = {}
    if filtro_paciente:
        query += " AND (m.id_paciente ILIKE :paciente OR u.nome_completo ILIKE :paciente)"
        params["paciente"] = f"%{filtro_paciente}%"
    if filtro_tipo:
        query += " AND m.tipo_medicao ILIKE :tipo"
        params["tipo"] = f"%{filtro_tipo}%"
    query += " ORDER BY m.data_hora DESC"
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        rows = [dict(r._mapping) for r in result]
    for row in rows:
        if row.get("data_hora"):
            row["data_hora"] = str(row["data_hora"])
    return jsonify(rows)


@bp.route("/", methods=["POST"])
def inserir():
    data = request.json
    with engine.begin() as conn:
        conn.execute(
            text(
                'INSERT INTO public."Medicao" '
                "(id_paciente, data_hora, tipo_medicao, valor, unidade) "
                "VALUES (:id_paciente, :data_hora, :tipo_medicao, :valor, :unidade)"
            ),
            data,
        )
    return jsonify({"ok": True}), 201


@bp.route("/<int:id_medicao>", methods=["PUT"])
def atualizar(id_medicao):
    data = request.json
    data["id_medicao"] = id_medicao
    with engine.begin() as conn:
        conn.execute(
            text(
                'UPDATE public."Medicao" SET '
                "id_paciente=:id_paciente, data_hora=:data_hora, "
                "tipo_medicao=:tipo_medicao, valor=:valor, unidade=:unidade "
                "WHERE id_medicao=:id_medicao"
            ),
            data,
        )
    return jsonify({"ok": True})


@bp.route("/<int:id_medicao>", methods=["DELETE"])
def remover(id_medicao):
    with engine.begin() as conn:
        conn.execute(
            text('DELETE FROM public."Medicao" WHERE id_medicao = :id_medicao'),
            {"id_medicao": id_medicao},
        )
    return jsonify({"ok": True})


@bp.route("/relatorio", methods=["GET"])
def relatorio():
    with engine.connect() as conn:
        total = conn.execute(
            text(
                'SELECT tipo_medicao, COUNT(*) AS total FROM public."Medicao" '
                "GROUP BY tipo_medicao ORDER BY total DESC"
            )
        )
        media = conn.execute(
            text(
                "SELECT tipo_medicao, ROUND(AVG(valor)::numeric, 2) AS media_valor "
                'FROM public."Medicao" GROUP BY tipo_medicao ORDER BY media_valor DESC'
            )
        )
        mensal = conn.execute(
            text(
                "SELECT TO_CHAR(data_hora, 'YYYY-MM') AS mes, COUNT(*) AS total "
                'FROM public."Medicao" GROUP BY mes ORDER BY mes'
            )
        )
        return jsonify(
            {
                "total_por_tipo": [dict(r._mapping) for r in total],
                "media_por_tipo": [dict(r._mapping) for r in media],
                "por_mes": [dict(r._mapping) for r in mensal],
            }
        )
