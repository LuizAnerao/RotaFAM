from flask import Flask, render_template, request, redirect, url_for
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
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.LargeBinary, nullable=False)

@app.before_first_request
def criar_banco():
    db.create_all()

# Tela recuperação
@app.route('/recuperar')
def recuperar():
    return render_template('recuperar.html')

# Enviar link
@app.route('/enviar_link', methods=['POST'])
def enviar_link():
    email = request.form.get('email')

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        return "E-mail não encontrado"

    # Geração do token
    token = serializer.dumps(email, salt='recuperacao-senha')

    link = url_for('resetar_senha', token=token, _external=True)

    # CORRIGIDO (sem erro de f-string)
    print(f"Link de recuperação: {link}")

    return "Link de recuperação enviado! (verifique o terminal)"

# Resetar senha
@app.route('/resetar/<token>', methods=['GET', 'POST'])
def resetar_senha(token):
    try:
        email = serializer.loads(
            token,
            salt='recuperacao-senha',
            max_age=1800
        )
    except Exception:
        return "Token inválido ou expirado"

    if request.method == 'POST':
        nova_senha = request.form.get('senha')

        senha_hash = bcrypt.hashpw(
            nova_senha.encode('utf-8'),
            bcrypt.gensalt()
        )

        usuario = Usuario.query.filter_by(email=email).first()
        usuario.senha = senha_hash

        db.session.commit()

        return "Senha redefinida com sucesso!"

    return '''
        <form method="POST">
            <input type="password" name="senha" placeholder="Nova senha" required>
            <button type="submit">Redefinir senha</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)