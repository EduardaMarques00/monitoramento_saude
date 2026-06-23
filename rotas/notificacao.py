from flask import Blueprint, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from db.conexao import get_engine

bp = Blueprint("notificacao", __name__, url_prefix="/api/notificacoes")
engine = get_engine()


@bp.route("/", methods=["GET"])
def listar():
    filtro_usuario = request.args.get("usuario", "")
    filtro_tipo = request.args.get("tipo", "")
    filtro_lida = request.args.get("lida", "")
    query = """
        SELECT n.*, u.nome_completo
        FROM public."Notificacao" n
        LEFT JOIN public."Usuario" u ON u.id = n.id_usuario
        WHERE 1=1
    """
    params = {}
    if filtro_usuario:
        query += " AND (n.id_usuario ILIKE :usuario OR u.nome_completo ILIKE :usuario)"
        params["usuario"] = f"%{filtro_usuario}%"
    if filtro_tipo:
        query += " AND n.tipo_notificacao ILIKE :tipo"
        params["tipo"] = f"%{filtro_tipo}%"
    if filtro_lida != "":
        query += " AND n.lida = :lida"
        params["lida"] = filtro_lida.lower() == "true"
    query += " ORDER BY n.data_hora_envio DESC"
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        rows = [dict(r._mapping) for r in result]
    for row in rows:
        if row.get("data_hora_envio"):
            row["data_hora_envio"] = str(row["data_hora_envio"])
    return jsonify(rows)


@bp.route("/", methods=["POST"])
def inserir():
    data = request.json
    campos_obrigatorios = ["id_usuario", "tipo_notificacao", "mensagem"]
    faltando = [c for c in campos_obrigatorios if not data.get(c)]
    if faltando:
        return jsonify({"ok": False, "erro": f"Campos obrigatorios faltando: {', '.join(faltando)}"}), 400
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    'INSERT INTO public."Notificacao" '
                    "(id_usuario, tipo_notificacao, mensagem, data_hora_envio, canal, realizada, lida) "
                    "VALUES (:id_usuario, :tipo_notificacao, :mensagem, :data_hora_envio, :canal, :realizada, :lida)"
                ),
                {
                    "id_usuario": data["id_usuario"],
                    "tipo_notificacao": data["tipo_notificacao"],
                    "mensagem": data["mensagem"],
                    "data_hora_envio": data.get("data_hora_envio") or None,
                    "canal": data.get("canal") or None,
                    "realizada": data.get("realizada", False),
                    "lida": data.get("lida", False),
                },
            )
    except IntegrityError as e:
        return jsonify({"ok": False, "erro": "Erro de integridade ao cadastrar notificacao.", "detalhe": str(e.orig)}), 409
    return jsonify({"ok": True}), 201


@bp.route("/<int:id_notificacao>", methods=["PUT"])
def atualizar(id_notificacao):
    data = request.json
    with engine.begin() as conn:
        conn.execute(
            text(
                'UPDATE public."Notificacao" SET '
                "id_usuario=:id_usuario, tipo_notificacao=:tipo_notificacao, "
                "mensagem=:mensagem, data_hora_envio=:data_hora_envio, "
                "canal=:canal, realizada=:realizada, lida=:lida "
                "WHERE id_notificacao=:id_notificacao"
            ),
            {
                "id_notificacao": id_notificacao,
                "id_usuario": data.get("id_usuario"),
                "tipo_notificacao": data.get("tipo_notificacao"),
                "mensagem": data.get("mensagem"),
                "data_hora_envio": data.get("data_hora_envio") or None,
                "canal": data.get("canal") or None,
                "realizada": data.get("realizada", False),
                "lida": data.get("lida", False),
            },
        )
    return jsonify({"ok": True})


@bp.route("/<int:id_notificacao>", methods=["DELETE"])
def remover(id_notificacao):
    with engine.begin() as conn:
        conn.execute(
            text('DELETE FROM public."Notificacao" WHERE id_notificacao = :id_notificacao'),
            {"id_notificacao": id_notificacao},
        )
    return jsonify({"ok": True})
