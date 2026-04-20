from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "chave_secreta"

# Usuário fake (simulação de banco de dados)
usuario = {
    "cpf": "12345678900",
    "senha": "1234"
}

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    cpf = request.form.get('cpf')
    senha = request.form.get('senha')

    if cpf == usuario["cpf"] and senha == usuario["senha"]:
        session['usuario'] = cpf
        return "Login realizado com sucesso!"
    else:
        return "CPF ou senha inválidos"

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)