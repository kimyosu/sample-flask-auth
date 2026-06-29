import uuid
from http.cookiejar import cut_port_re

from flask import Flask, request, jsonify, session

from database import db
from models.user import User
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config["SECRET_KEY"] = "kimy"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, uuid.UUID(user_id))

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password :
        # login
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Login feito"}), 200
    return jsonify({"message": "Credenciais inválidas"}), 400

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout feito"}), 200

@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuario cadastrado com sucesso"}), 200
    return jsonify({"message": "Dados inválidas"}), 400

@app.route("/user/<string:id>", methods=["GET"])
@login_required
def read_user(id):
    id = uuid.UUID(id)
    user = db.session.get(id)

    if user:
        return jsonify({"username": user.username}), 200

    return jsonify({"message": "Usuario não encontrado"}), 404

@app.route("/user/<string:id>", methods=["PUT"])
def update_user(id):
    data = request.json
    user = db.session.get(User, uuid.UUID(id))
    if user and data.get("password"):
        user.password = data.get("password")
        db.session.commit()
        return jsonify({"message": "Usuario atualizado"}), 200

    return jsonify({"message": "Usuario não encontrado"}), 404

@app.route("/user/<string:id>", methods=["DELETE"])
def delete_user(id):
    id = uuid.UUID(id)
    user = db.session.get(User, id)
    if id  == current_user.id:
        return jsonify({"message": "Não é possivel deletar a conta enquanto logado"}), 403
    if user and id != current_user.id:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Usuario excluido"}), 204
    return jsonify({"message": "Usuario não encontrado"}), 404


db.init_app(app)
# configs
if __name__ == "__main__":
    app.run(debug=True)