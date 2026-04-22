from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer
import bcrypt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'chave_super_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Modelo
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    cpf = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100), unique=True)
    senha = db.Column(db.LargeBinary)

@app.before_first_request
def criar_banco():
    db.create_all()

# ================= LOGIN =================
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def fazer_login():
    cpf = request.form.get('cpf')
    senha = request.form.get('senha')

    usuario = Usuario.query.filter_by(cpf=cpf).first()

    if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario.senha):
        session['usuario'] = usuario.id
        return "Login realizado com sucesso!"
    else:
        return "Dados inválidos"

# ================= CADASTRO =================
@app.route('/cadastro')
def tela_cadastro():
    return render_template('cadastro.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    email = request.form.get('email')
    senha = request.form.get('senha')

    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

    novo = Usuario(nome=nome, cpf=cpf, email=email, senha=senha_hash)
    db.session.add(novo)
    db.session.commit()

    return redirect(url_for('login'))

# ================= RECUPERAÇÃO =================
@app.route('/recuperar')
def recuperar():
    return render_template('recuperar.html')

@app.route('/enviar_link', methods=['POST'])
def enviar_link():
    email = request.form.get('email')

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        return "E-mail não encontrado"

    token = serializer.dumps(email, salt='recuperacao')

    link = url_for('resetar_senha', token=token, _external=True)

    print(f"Link de recuperação: {link}")

    return "Link enviado! Veja no terminal"

@app.route('/resetar/<token>', methods=['GET', 'POST'])
def resetar_senha(token):
    try:
        email = serializer.loads(token, salt='recuperacao', max_age=1800)
    except:
        return "Token inválido"

    if request.method == 'POST':
        nova = request.form.get('senha')

        usuario = Usuario.query.filter_by(email=email).first()
        usuario.senha = bcrypt.hashpw(nova.encode('utf-8'), bcrypt.gensalt())

        db.session.commit()

        return redirect(url_for('login'))

    return '''
    <form method="POST">
        <input type="password" name="senha" placeholder="Nova senha">
        <button type="submit">Salvar</button>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)