from flask import Blueprint, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from db.conexao import get_engine

bp = Blueprint("prescricao", __name__, url_prefix="/api/prescricoes")
engine = get_engine()


@bp.route("/", methods=["GET"])
def listar():
    filtro_paciente = request.args.get("paciente", "")
    filtro_profissional = request.args.get("profissional", "")
    query = """
        SELECT p.id_prescricao, p.id_paciente, p.id_profissional,
               p.data_emissao, p.observacoes, p.validade,
               u.nome_completo AS nome_paciente,
               up.nome_completo AS nome_profissional
        FROM public."Prescricao" p
        LEFT JOIN public."Paciente" pac ON pac.id_usuario = p.id_paciente
        LEFT JOIN public."Usuario" u ON u.id = pac.id_usuario
        LEFT JOIN public."Profissional_Saude" ps ON ps.id_usuario = p.id_profissional
        LEFT JOIN public."Usuario" up ON up.id = ps.id_usuario
        WHERE 1=1
    """
    params = {}
    if filtro_paciente:
        query += " AND (p.id_paciente ILIKE :paciente OR u.nome_completo ILIKE :paciente)"
        params["paciente"] = f"%{filtro_paciente}%"
    if filtro_profissional:
        query += " AND (p.id_profissional ILIKE :profissional OR up.nome_completo ILIKE :profissional)"
        params["profissional"] = f"%{filtro_profissional}%"
    query += " ORDER BY p.data_emissao DESC"
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        rows = [dict(r._mapping) for r in result]
    for row in rows:
        if row.get("data_emissao"):
            row["data_emissao"] = str(row["data_emissao"])
        if row.get("validade"):
            row["validade"] = str(row["validade"])
    return jsonify(rows)


@bp.route("/<int:id_prescricao>", methods=["GET"])
def buscar(id_prescricao):
    with engine.connect() as conn:
        result = conn.execute(
            text('SELECT * FROM public."Prescricao" WHERE id_prescricao = :id'),
            {"id": id_prescricao},
        )
        row = result.fetchone()
        if row is None:
            return jsonify({"ok": False, "erro": "Prescricao nao encontrada."}), 404
        prescricao = dict(row._mapping)
        if prescricao.get("data_emissao"):
            prescricao["data_emissao"] = str(prescricao["data_emissao"])
        if prescricao.get("validade"):
            prescricao["validade"] = str(prescricao["validade"])
        meds = conn.execute(
            text('SELECT * FROM public."Medicamento_Prescricao" WHERE id_prescricao = :id'),
            {"id": id_prescricao},
        )
        prescricao["medicamentos"] = [dict(m._mapping) for m in meds]
    return jsonify(prescricao)


@bp.route("/", methods=["POST"])
def inserir():
    data = request.json
    campos_obrigatorios = ["id_paciente", "id_profissional", "data_emissao"]
    faltando = [c for c in campos_obrigatorios if not data.get(c)]
    if faltando:
        return jsonify({"ok": False, "erro": f"Campos obrigatorios faltando: {', '.join(faltando)}"}), 400
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text(
                    'INSERT INTO public."Prescricao" '
                    "(id_paciente, id_profissional, data_emissao, observacoes, validade) "
                    "VALUES (:id_paciente, :id_profissional, :data_emissao, :observacoes, :validade) "
                    "RETURNING id_prescricao"
                ),
                {
                    "id_paciente": data["id_paciente"],
                    "id_profissional": data["id_profissional"],
                    "data_emissao": data["data_emissao"],
                    "observacoes": data.get("observacoes") or None,
                    "validade": data.get("validade") or None,
                },
            )
            novo_id = result.fetchone()[0]
            for med in data.get("medicamentos", []):
                conn.execute(
                    text(
                        'INSERT INTO public."Medicamento_Prescricao" '
                        "(id_prescricao, nome, dosagem, frequencia, duracao) "
                        "VALUES (:id_prescricao, :nome, :dosagem, :frequencia, :duracao)"
                    ),
                    {
                        "id_prescricao": novo_id,
                        "nome": med.get("nome"),
                        "dosagem": med.get("dosagem") or None,
                        "frequencia": med.get("frequencia") or None,
                        "duracao": med.get("duracao") or None,
                    },
                )
    except IntegrityError as e:
        return jsonify({"ok": False, "erro": "Erro de integridade ao cadastrar prescricao.", "detalhe": str(e.orig)}), 409
    return jsonify({"ok": True, "id_prescricao": novo_id}), 201


@bp.route("/<int:id_prescricao>", methods=["PUT"])
def atualizar(id_prescricao):
    data = request.json
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    'UPDATE public."Prescricao" SET '
                    "id_paciente=:id_paciente, id_profissional=:id_profissional, "
                    "data_emissao=:data_emissao, observacoes=:observacoes, validade=:validade "
                    "WHERE id_prescricao=:id_prescricao"
                ),
                {
                    "id_prescricao": id_prescricao,
                    "id_paciente": data.get("id_paciente"),
                    "id_profissional": data.get("id_profissional"),
                    "data_emissao": data.get("data_emissao") or None,
                    "observacoes": data.get("observacoes") or None,
                    "validade": data.get("validade") or None,
                },
            )
    except IntegrityError as e:
        return jsonify({"ok": False, "erro": "Erro de integridade ao atualizar prescricao.", "detalhe": str(e.orig)}), 409
    return jsonify({"ok": True})


@bp.route("/<int:id_prescricao>", methods=["DELETE"])
def remover(id_prescricao):
    try:
        with engine.begin() as conn:
            conn.execute(
                text('DELETE FROM public."Medicamento_Prescricao" WHERE id_prescricao = :id'),
                {"id": id_prescricao},
            )
            conn.execute(
                text('DELETE FROM public."Prescricao" WHERE id_prescricao = :id'),
                {"id": id_prescricao},
            )
    except IntegrityError as e:
        return jsonify({"ok": False, "erro": "Nao e possivel remover esta prescricao.", "detalhe": str(e.orig)}), 409
    return jsonify({"ok": True})
