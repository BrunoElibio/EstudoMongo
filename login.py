from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from bson import ObjectId
import bcrypt

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/loginexample'
mongo = PyMongo(app)

# Configuração secreta para a sessão
app.secret_key = 'your_secret_key'

# Rota para a página de login
@app.route('/')
def index():
    if 'username' in session:
        return 'Você já está logado como ' + session['username']

    return render_template('/login.html')

# Rota para autenticação do usuário
@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'username': request.form['username']})

    if login_user:
        # Verifica a senha usando bcrypt
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Login inválido'

# Rota para a página de logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# Rota para a criação de conta
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})

        if existing_user is None:
            # Hash da senha usando bcrypt
            hashed_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'username': request.form['username'], 'password': hashed_password})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'Nome de usuário já existe! Escolha outro nome.'

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
