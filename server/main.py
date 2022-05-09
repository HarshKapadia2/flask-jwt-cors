from flask import Flask, request, make_response, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, verify_jwt_in_request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import certifi
import os

load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SYMMETRIC_KEY")
jwt = JWTManager(app)

mongoClient = PyMongo(app, uri=os.getenv(
    "MONGODB_URI"), tlsCAFile=certifi.where())
db = mongoClient.db


@app.route("/", methods=["GET", "OPTIONS"])
def home():
    if request.method == "OPTIONS":  # For the CORS Preflight request
        return corsPreflightResponse()
    elif request.method == "GET":
        response = make_response(jsonify({"message": "Success"}), 200)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":  # For the CORS Preflight request
        return corsPreflightResponse()
    elif request.method == "POST":
        data = request.json
        username = data["username"]
        password = data["password"]

        try:
            userData = db.users.find_one(
                {"username": username, "password": password})

            if(not userData):
                response = make_response(
                    jsonify({"message": "Failure. Username or password did not match."}), 401)
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response
        except Exception as ex:
            print("DB error: ", ex)
            response = make_response(
                jsonify({"message": "Failure. Could not retrieve user data."}), 500)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

        additionalClaims = {"name": userData["name"]}

        accessToken = create_access_token(
            identity=username, additional_claims=additionalClaims)

        response = make_response(
            jsonify({"message": "Success", "token": accessToken}), 200)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


@app.route("/signup", methods=["POST", "OPTIONS"])
def signup():
    if request.method == "OPTIONS":  # For the CORS Preflight request
        return corsPreflightResponse()
    elif request.method == "POST":
        data = request.json
        name = data["name"]
        username = data["username"]
        password = data["password"]

        # Not hashing and salting the password because this is a demo
        newUser = {"name": name, "username": username, "password": password}

        # Check for duplicate username
        try:
            if(db.users.find_one({"username": username})):
                response = make_response(
                    jsonify({"message": "Failure. Duplicate username."}), 400)
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response
        except:
            print("DB error: ", ex)
            response = make_response(
                jsonify({"message": "Failure. Could not retrieve user data."}), 500)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

        try:
            db.users.insert_one(newUser)  # Insert user into DB
        except Exception as ex:
            print("DB error: ", ex)
            response = make_response(
                jsonify({"message": "Failure. Could not save user data."}), 500)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

        response = make_response(
            jsonify({"message": "Success"}), 200)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


@app.route("/protected", methods=["GET", "OPTIONS"])
def protected():
    if request.method == "OPTIONS":  # For the CORS Preflight request
        return corsPreflightResponse()
    elif request.method == "GET":
        try:
            username = verify_jwt_in_request()[1]["sub"]
        except:
            response = make_response(
                jsonify({"message": "Unauthorized"}), 401)
            response.headers.add("Access-Control-Allow-Origin",
                                 "http://localhost:3000")
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response

        name = get_jwt()["name"]

        response = make_response(
            jsonify({"message": "Success", "name": name, "username": username}), 200)
        response.headers.add("Access-Control-Allow-Origin",
                             "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response


@app.route("/isAuthorized", methods=["GET", "OPTIONS"])
def isAuthorized():
    if request.method == "OPTIONS":  # For the CORS Preflight request
        return corsPreflightResponse()
    elif request.method == "GET":
        try:
            verify_jwt_in_request()
        except:
            response = make_response(
                jsonify({"message": "Unauthorized"}), 401)
            response.headers.add("Access-Control-Allow-Origin",
                                 "http://localhost:3000")
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response

        response = make_response(
            jsonify({"message": "Success"}), 200)
        response.headers.add("Access-Control-Allow-Origin",
                             "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response


def corsPreflightResponse():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin",
                         "http://localhost:3000")
    response.headers.add("Access-Control-Allow-Headers",
                         "Authorization, Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Max-Age", 3600)
    return response


if __name__ == "__main__":
    app.run(debug=True)
