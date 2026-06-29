import uuid

import bcrypt
from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from database import db
from models.user import User

app = Flask(__name__)
app.config["SECRET_KEY"] = "kimy"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://andrew:andrew@127.0.0.1:3306/flask-crud"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, uuid.UUID(user_id))


@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())

        user = User(username=username, password=hashed_password, role="user")
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuario cadastrado com sucesso"}), 200
    return jsonify({"message": "Dados inválidas"}), 400


@app.route("/user/<string:id>", methods=["GET"])
@login_required
def read_user(id):
    id = uuid.UUID(id)
    user = db.session.get(User, id)

    if user:
        return jsonify({"username": user.username}), 200

    return jsonify({"message": "Usuario não encontrado"}), 404


@app.route("/user/<string:id>", methods=["PUT"])
@login_required
def update_user(id):
    data = request.json
    user = db.session.get(User, uuid.UUID(id))

    # caso o id que tenha sido passado seja diferente do id atual e a role seja user
    if id != current_user.id and current_user.role == "user":
        return jsonify({"message": "Operação não permitida"}), 403

    if user and data.get("password"):
        user.password = data.get("password")
        db.session.commit()
        return jsonify({"message": "Usuario atualizado"}), 200

    return jsonify({"message": "Usuario não encontrado"}), 404


@app.route("/user/<string:id>", methods=["DELETE"])
@login_required
def delete_user(id):
    id = uuid.UUID(id)
    user = db.session.get(User, id)
    if current_user.role != "admin":
        return jsonify(({"message": "Operação não permitida"})), 403
    if id == current_user.id:
        return jsonify({"message": "Não é possivel deletar a conta enquanto logado"}), 403
    if user and id != current_user.id:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Usuario excluido"}), 204
    return jsonify({"message": "Usuario não encontrado"}), 404


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        # login
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Login feito"}), 200
    return jsonify({"message": "Credenciais inválidas"}), 400


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout feito"}), 200


db.init_app(app)
# configs
if __name__ == "__main__":
    app.run(debug=True)
