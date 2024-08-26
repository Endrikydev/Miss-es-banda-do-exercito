from flask import Flask, render_template, request, redirect, url_for, abort
import sqlite3

app = Flask(__name__)
#faz a conexão com o banco de dados sqlite
def get_db_connection():
    conn = sqlite3.connect('missoes.db')
    conn.row_factory = sqlite3.Row
    return conn
#cria uma tabela caso ela não exista
def criar_tabela():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='missoes';")
    table_exists = cursor.fetchone()
    if not table_exists:
        cursor.execute('''
        CREATE TABLE missoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            turno TEXT,
            local TEXT,
            missao TEXT,
            banda TEXT
        )
        ''')
        conn.commit()
    conn.close()

criar_tabela()
#cria um id para cada missão(não tenho certeza ainda se é obrigatorio essa parte, mas antes dessa função estava tendo erro ao criar missões)
def create_id(db_name, table_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT MAX(id) FROM {}".format(table_name))
    max_id = c.fetchone()[0]
    if max_id is None:
        new_id = 1
    else:
        new_id = max_id + 1

    # Fechar conexão
    conn.close()

    return new_id
#cria uma nova missão
def nova_missao(data, turno, local, missao, banda):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO missoes (data, turno, local, missao, banda) VALUES (?, ?, ?, ?, ?)',
                   (data, turno, local, missao, banda))
    conn.commit()
    conn.close()
#apresenta as missões ja criadas no banco de dados
def apresentar_missoes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM missoes')
    missoes = cursor.fetchall()
    conn.close()
    return missoes
#retorna apenas uma missão pelo seu id
def retornar_missao(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM missoes WHERE id = ?', (id,))
    missao = cursor.fetchone()
    conn.close()
    return missao
#confere se a missão existe antes de alterar ou excluir 
def existe_missao(id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM missoes WHERE id = ?', (id,))
    missao = cursor.fetchone()
    conn.close()
    return missao is not None
#atualiza uma missão com base nos dados oferecidos pelo usuario
def atualizar_missao(id: int, dados_missao: dict):
    if not existe_missao(id):
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE missoes
        SET data = ?, turno = ?, local = ?, missao = ?, banda = ?
        WHERE id = ?
    ''', (dados_missao['data'], dados_missao['turno'], dados_missao['local'], dados_missao['missao'], dados_missao['banda'], id))
    conn.commit()
    conn.close()
    return True
#exclui uma missão do banco de dados
def remover_missao(id: int):
    if not existe_missao(id):
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM missoes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return True
#rota inicial do app flask
@app.route('/')
def home():
    dicionario = apresentar_missoes()
    return render_template("index.html", missoes=dicionario)
#rota de alteração e exclusão de missões do app flask
@app.route("/missao/<int:id>", methods=['GET', 'POST'])
def editar_missao(id: int):
    conferir_missao = retornar_missao(id)
    if conferir_missao is None:
        abort(404)

    if request.method == "POST":
        if "excluir" in request.form:
            remover_missao(id)
            return redirect(url_for('home'))
        elif "salvar" in request.form:
            missao = {
                'data': request.form["data"],
                'turno': request.form["turno"],
                'local': request.form["local"],
                'missao': request.form["missao"],
                'banda': request.form["banda"]
            }
            atualizar_missao(id, missao)
            return redirect(url_for('home'))
    else:
        missaoeditada = dict(conferir_missao)
        missaoeditada['id'] = id
    return render_template("cadastro_missoes.html", **missaoeditada)
#rota para criar uma nova missão do app flask
@app.route('/criar_missao', methods=['GET', 'POST'])
def criar_missao():
    if request.method == "POST":
        missao = {
            'data': request.form["data"],
            'turno': request.form["turno"],
            'local': request.form["local"],
            'missao': request.form["missao"],
            'banda': request.form["banda"]
        }
        nova_missao(**missao)
        return redirect(url_for('home'))
    else:
        return render_template('cadastro_missoes.html')

if __name__ == '__main__':
    app.run(debug=True)

