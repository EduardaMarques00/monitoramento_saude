from flask import Blueprint, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from db.conexao import get_engine

bp = Blueprint("paciente", __name__, url_prefix="/api/pacientes")
engine = get_engine()


def gerar_proximo_id(conn):
    """Gera o próximo id_usuario disponível no formato USRxxx (ex: USR031)."""
    result = conn.execute(
        text(
            "SELECT id FROM public.\"Usuario\" "
            "WHERE id ~ '^USR[0-9]+$' "
            "ORDER BY CAST(SUBSTRING(id FROM 4) AS INTEGER) DESC "
            "LIMIT 1"
        )
    )
    row = result.fetchone()
    if row is None:
        return "USR001"
    ultimo_num = int(row[0][3:])
    novo_num = ultimo_num + 1
    return f"USR{novo_num:03d}"


@bp.route("/", methods=["GET"])
def listar():
    """Lista pacientes (join com Usuario para trazer nome, email, etc.)."""
    filtro = request.args.get("filtro", "")
    query = '''
        SELECT u.id AS id_usuario, u.nome_completo, u.cpf, u.data_nascimento,
               u.email, u.rua, u.numero, u.bairro, u.cidade, u.estado, u.cep,
               p.tipo_sanguineo, p.altura_cm, p.peso_inicial_kg
        FROM public."Paciente" p
        JOIN public."Usuario" u ON u.id = p.id_usuario
    '''
    params = {}
    if filtro:
        query += " WHERE u.id ILIKE :filtro OR u.nome_completo ILIKE :filtro"
        params["filtro"] = f"%{filtro}%"
    query += " ORDER BY u.id"
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        rows = [dict(r._mapping) for r in result]
    return jsonify(rows)


@bp.route("/", methods=["POST"])
def inserir():
    """Cadastra um novo paciente: cria Usuario + Paciente em uma única transação.

    O id_usuario (PK) é gerado automaticamente (próximo USRxxx).
    """
    data = request.json

    campos_obrigatorios = ["nome_completo", "cpf", "email", "senha"]
    faltando = [c for c in campos_obrigatorios if not data.get(c)]
    if faltando:
        return jsonify({"ok": False, "erro": f"Campos obrigatórios faltando: {', '.join(faltando)}"}), 400

    try:
        with engine.begin() as conn:
            novo_id = gerar_proximo_id(conn)
            conn.execute(
                text(
                    'INSERT INTO public."Usuario" '
                    "(id, nome_completo, cpf, data_nascimento, email, senha, "
                    "rua, numero, bairro, cidade, estado, cep) "
                    "VALUES (:id, :nome_completo, :cpf, :data_nascimento, :email, :senha, "
                    ":rua, :numero, :bairro, :cidade, :estado, :cep)"
                ),
                {
                    "id": novo_id,
                    "nome_completo": data["nome_completo"],
                    "cpf": data["cpf"],
                    "data_nascimento": data.get("data_nascimento") or None,
                    "email": data["email"],
                    "senha": data["senha"],
                    "rua": data.get("rua") or None,
                    "numero": data.get("numero") or None,
                    "bairro": data.get("bairro") or None,
                    "cidade": data.get("cidade") or None,
                    "estado": data.get("estado") or None,
                    "cep": data.get("cep") or None,
                },
            )

            conn.execute(
                text(
                    'INSERT INTO public."Paciente" '
                    "(id_usuario, tipo_sanguineo, altura_cm, peso_inicial_kg) "
                    "VALUES (:id_usuario, :tipo_sanguineo, :altura_cm, :peso_inicial_kg)"
                ),
                {
                    "id_usuario": novo_id,
                    "tipo_sanguineo": data.get("tipo_sanguineo") or None,
                    "altura_cm": data.get("altura_cm") or None,
                    "peso_inicial_kg": data.get("peso_inicial_kg") or None,
                },
            )
    except IntegrityError as e:
        msg = str(e.orig)
        if "cpf" in msg:
            return jsonify({"ok": False, "erro": "Já existe um usuário com esse CPF."}), 409
        if "email" in msg:
            return jsonify({"ok": False, "erro": "Já existe um usuário com esse email."}), 409
        return jsonify({"ok": False, "erro": "Erro de integridade ao cadastrar paciente."}), 409

    return jsonify({"ok": True, "id_usuario": novo_id}), 201


@bp.route("/<id_usuario>", methods=["PUT"])
def atualizar(id_usuario):
    """Atualiza dados de Usuario e Paciente (id_usuario não muda, é a PK)."""
    data = request.json
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    'UPDATE public."Usuario" SET '
                    "nome_completo=:nome_completo, cpf=:cpf, data_nascimento=:data_nascimento, "
                    "email=:email, rua=:rua, numero=:numero, bairro=:bairro, "
                    "cidade=:cidade, estado=:estado, cep=:cep "
                    "WHERE id=:id"
                ),
                {
                    "id": id_usuario,
                    "nome_completo": data.get("nome_completo"),
                    "cpf": data.get("cpf"),
                    "data_nascimento": data.get("data_nascimento") or None,
                    "email": data.get("email"),
                    "rua": data.get("rua") or None,
                    "numero": data.get("numero") or None,
                    "bairro": data.get("bairro") or None,
                    "cidade": data.get("cidade") or None,
                    "estado": data.get("estado") or None,
                    "cep": data.get("cep") or None,
                },
            )
            conn.execute(
                text(
                    'UPDATE public."Paciente" SET '
                    "tipo_sanguineo=:tipo_sanguineo, altura_cm=:altura_cm, "
                    "peso_inicial_kg=:peso_inicial_kg "
                    "WHERE id_usuario=:id_usuario"
                ),
                {
                    "id_usuario": id_usuario,
                    "tipo_sanguineo": data.get("tipo_sanguineo") or None,
                    "altura_cm": data.get("altura_cm") or None,
                    "peso_inicial_kg": data.get("peso_inicial_kg") or None,
                },
            )
    except IntegrityError as e:
        msg = str(e.orig)
        if "cpf" in msg:
            return jsonify({"ok": False, "erro": "Já existe um usuário com esse CPF."}), 409
        if "email" in msg:
            return jsonify({"ok": False, "erro": "Já existe um usuário com esse email."}), 409
        return jsonify({"ok": False, "erro": "Erro de integridade ao atualizar paciente."}), 409

    return jsonify({"ok": True})


@bp.route("/<id_usuario>", methods=["DELETE"])
def remover(id_usuario):
    """Remove o paciente.

    Remove a linha de Paciente e também a de Usuario (CASCADE manual),
    pois Paciente.id_usuario referencia Usuario.id.
    Bloqueia se houver dependências em outras tabelas (alergias, consultas etc.)
    """
    try:
        with engine.begin() as conn:
            conn.execute(
                text('DELETE FROM public."Paciente" WHERE id_usuario = :id_usuario'),
                {"id_usuario": id_usuario},
            )
            conn.execute(
                text('DELETE FROM public."Usuario" WHERE id = :id_usuario'),
                {"id_usuario": id_usuario},
            )
    except IntegrityError as e:
        return jsonify({
            "ok": False,
            "erro": (
                "Não é possível remover este paciente: existem registros "
                "vinculados a ele (alergias, condições crônicas, consultas, "
                "medições, etc.). Remova esses registros primeiro."
            ),
            "detalhe": str(e.orig),
        }), 409

    return jsonify({"ok": True})