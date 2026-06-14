# Sistema de Monitoramento de Saúde

## Estrutura do projeto

```
monitoramento_saude/
├── app.py               # Ponto de entrada — servidor Flask
├── requirements.txt
├── db/
│   └── conexao.py       # Configuração da conexão com o banco (SQLAlchemy)
├── rotas/
│   ├── paciente.py      # API REST — /api/pacientes/
│   └── medicao.py       # API REST — /api/medicoes/
└── paginas/
    ├── index.html        # Menu principal
    ├── paciente.html     # CRUD de Pacientes
    ├── medicao.html      # CRUD de Medições
    └── relatorio.html    # Relatório gráfico de Medições
```

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração do banco

Edite `db/conexao.py` e ajuste as variáveis:

```python
DB_USER     = "postgres"
DB_PASSWORD = "postgres"
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "monitoramento_saude"
```

## Executar

```bash
python app.py
```

Acesse em: **http://localhost:5000**

## Endpoints da API

### Pacientes — `/api/pacientes/`

| Método | Rota                    | Descrição                        |
|--------|-------------------------|----------------------------------|
| GET    | `/api/pacientes/`       | Lista pacientes (filtro por nome/CPF via `?filtro=`) |
| POST   | `/api/pacientes/`       | Cadastra novo paciente (gera ID automaticamente) |
| PUT    | `/api/pacientes/<id>`   | Atualiza dados do paciente       |
| DELETE | `/api/pacientes/<id>`   | Remove paciente                  |

### Medições — `/api/medicoes/`

| Método | Rota                      | Descrição                        |
|--------|---------------------------|----------------------------------|
| GET    | `/api/medicoes/`          | Lista medições (filtro por `?paciente=` e `?tipo=`) |
| POST   | `/api/medicoes/`          | Registra nova medição            |
| PUT    | `/api/medicoes/<id>`      | Atualiza medição                 |
| DELETE | `/api/medicoes/<id>`      | Remove medição                   |
| GET    | `/api/medicoes/relatorio` | Dados agregados para os gráficos |

## Adicionando telas de outros membros

1. Crie o arquivo de rotas em `rotas/nome_tabela.py` seguindo o padrão de `paciente.py` ou `medicao.py`.
2. Registre o blueprint em `app.py`:
   ```python
   from rotas.nome_tabela import bp as bp_nome
   app.register_blueprint(bp_nome)
   ```
3. Crie a página HTML em `paginas/nome_tabela.html` seguindo o padrão de `paciente.html`.
4. Adicione o link no menu em `paginas/index.html`.
