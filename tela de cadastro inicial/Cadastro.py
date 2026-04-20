from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)


@app.before_first_request
def criar_banco():
    db.create_all()

# Rota de cadastro
@app.route('/')
def cadastro():
    return render_template('cadastro.html')

# Receber dados do formulário
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    email = request.form.get('email')
    senha = request.form.get('senha')

    # Verificar se usuário já existe
    usuario_existente = Usuario.query.filter(
        (Usuario.email == email) | (Usuario.cpf == cpf)
    ).first()

    if usuario_existente:
        return "Usuário já cadastrado!"

    # Criar novo usuário
    novo_usuario = Usuario(
        nome=nome,
        cpf=cpf,
        email=email,
        senha=senha  # ⚠️ depois vamos criptografar
    )

    db.session.add(novo_usuario)
    db.session.commit()

    return "Cadastro realizado com sucesso!"

if __name__ == '__main__':
    app.run(debug=True)
