from flask import Blueprint, jsonify, request
from sqlalchemy import text
from db.conexao import get_engine

bp = Blueprint("consulta", __name__, url_prefix="/api/consultas")
engine = get_engine()


@bp.route("/", methods=["GET"])
def listar():
    filtro_paciente = request.args.get("paciente", "")
    filtro_status = request.args.get("status", "")

    query = """
        SELECT c.*, u.nome_completo AS paciente
        FROM public."Consulta" c
        LEFT JOIN public."Paciente" p
            ON p.id_usuario = c.id_paciente
        LEFT JOIN public."Usuario" u
            ON u.id = p.id_usuario
        WHERE 1=1
    """

    params = {}

    if filtro_paciente:
        query += """
            AND (
                c.id_paciente ILIKE :paciente
                OR u.nome_completo ILIKE :paciente
            )
        """
        params["paciente"] = f"%{filtro_paciente}%"

    if filtro_status:
        query += " AND c.status ILIKE :status"
        params["status"] = f"%{filtro_status}%"

    query += " ORDER BY c.data_hora DESC"

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
                INSERT INTO public."Consulta"
                (
                    id_paciente,
                    id_profissional,
                    data_hora,
                    modalidade,
                    status,
                    anotacoes
                )
                VALUES
                (
                    :id_paciente,
                    :id_profissional,
                    :data_hora,
                    :modalidade,
                    :status,
                    :anotacoes
                )
                '''
            ),
            data,
        )

    return jsonify({"ok": True}), 201


@bp.route("/<int:id_consulta>", methods=["PUT"])
def atualizar(id_consulta):

    data = request.json
    data["id_consulta"] = id_consulta

    with engine.begin() as conn:

        conn.execute(
            text(
                '''
                UPDATE public."Consulta"
                SET
                    id_paciente=:id_paciente,
                    id_profissional=:id_profissional,
                    data_hora=:data_hora,
                    modalidade=:modalidade,
                    status=:status,
                    anotacoes=:anotacoes
                WHERE id_consulta=:id_consulta
                '''
            ),
            data,
        )

    return jsonify({"ok": True})

@bp.route("/<int:id_consulta>", methods=["DELETE"])
def remover(id_consulta):

    with engine.begin() as conn:

        conn.execute(
            text(
                '''
                DELETE FROM public."Consulta"
                WHERE id_consulta=:id_consulta
                '''
            ),
            {"id_consulta": id_consulta},
        )

    return jsonify({"ok": True})

@bp.route("/relatorio", methods=["GET"])
def relatorio():

    with engine.connect() as conn:

        result = conn.execute(
            text(
                '''
                SELECT
                    status,
                    COUNT(*) AS total
                FROM public."Consulta"
                GROUP BY status
                ORDER BY total DESC
                '''
            )
        )

        return jsonify(
            [dict(r._mapping) for r in result]
        )