import re

from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
from flask_jwt_extended import create_access_token, verify_jwt_in_request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

import json
import requests
import datetime

from waitress import serve

from waitress import serve

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)
cors = CORS(app)


@app.before_request
def middleware():
    urlAcceso = request.path
    if (urlAcceso == "/login"):
        pass

   # else:
        #verify_jwt_in_request()

    elif verify_jwt_in_request():

        infoUsuario = get_jwt_identity()
        idRol = infoUsuario["rol"]["_id"]
        urlAcceso = transformarUrl(urlAcceso)
        urlValidarPermiso = dataConfig["url-backend-security"] + "/permiso-rol/validar-permiso/rol/" + idRol
        headersValidarPermiso = {"Content-Type": "application/json"}
        bodyValidarPermiso = {
            "url": urlAcceso,
            "metodo": request.method
        }
        respuestaValidarPermiso = requests.get(urlValidarPermiso, json=bodyValidarPermiso,headers=headersValidarPermiso)
        print("Respuesta validar permiso: ", respuestaValidarPermiso)

        if (respuestaValidarPermiso.status_code == 200):
            pass
        else:
            return {"mensaje": "Acceso Denegado"}, 401



def transformarUrl(urlAcceso):
    print("Url antes de transformarla: ", urlAcceso)
    partes = urlAcceso.split("/")
    print("La url dividida es:", partes)
    for palabra in partes:
        if re.search('\\d', palabra):
            urlAcceso = urlAcceso.replace(palabra, "?")

    print("Url después de transformarla:", urlAcceso)
    return urlAcceso
# CODIGO GUIA
# app=Flask(__name__)
# cors = CORS(app)
# from flask_jwt_extended import create_access_token, verify_jwt_in_request
# from flask_jwt_extended import get_jwt_identity
# from flask_jwt_extended import jwt_required
# from flask_jwt_extended import JWTManager
# app.config["JWT_SECRET_KEY"]="super-secret" #Cambiar por el que se conveniente
# jwt = JWTManager(app)
# @app.route("/login", methods=["POST"])
# def create_token():
#     data = request.get_json()
#     headers = {"Content-Type": "application/json; charset=utf-8"}
#     url=dataConfig["url-backend-security"]+'/usuarios/validar'
#     response = requests.post(url, json=data, headers=headers)
#     if response.status_code == 200:
#         user = response.json()
#         expires = datetime.timedelta(seconds=60 * 60*24)
#         access_token = create_access_token(identity=user, expires_delta=expires)
#         return jsonify({"token": access_token, "user_id": user["_id"]})
#     else:
#         return jsonify({"msg": "Bad username or password"}), 401
#
# @app.before_request
# def before_request_callback():
#     endPoint=limpiarURL(request.path)
#     excludedRoutes=["/login"]
#     if excludedRoutes.__contains__(request.path):
#         pass
#     elif verify_jwt_in_request():
#         usuario = get_jwt_identity()
#         if usuario["rol"]is not None:
#             tienePersmiso=validarPermiso(endPoint,request.method,usuario["rol"]["_id"])
#             if not tienePersmiso:
#                 return jsonify({"message": "Permission denied"}), 401
#         else:
#             return jsonify({"message": "Permission denied"}), 401
# def limpiarURL(url):
#     partes = url.split("/")
#     for laParte in partes:
#         if re.search('\\d', laParte):
#             url = url.replace(laParte, "?")
#     return url
# def validarPermiso(endPoint,metodo,idRol):
#     url=dataConfig["url-backend-security"]+"/permisos-roles/validar-permiso/rol/"+str(idRol)
#     tienePermiso=False
#     headers = {"Content-Type": "application/json; charset=utf-8"}
#     body={
#         "url":endPoint,
#         "metodo":metodo
#     }
#     response = requests.get(url,json=body, headers=headers)
#     try:
#         data=response.json()
#         if("_id" in data):
#             tienePermiso=True
#     except:
#         pass
#     return tienePermiso
#


###Usuario###
@app.route("/login", methods=["POST"])
def validarUsuario():
    url = dataConfig["url-backend-security"] + "/usuarios/validar-usuario"
    headers = {"Content-Type": "application/json"}
    bodyRequest = request.get_json()
    response = requests.post(url, json=bodyRequest, headers=headers)

    if (response.status_code == 200):
        print("El usuario se valido correctamente")
        infoUsuario = response.json()

        tiempoToken = datetime.timedelta(seconds=60 * 60 * 24)
        newToken = create_access_token(identity=infoUsuario, expires_delta=tiempoToken)

        return {"token": newToken}
    else:
        return {"mensaje": "Usuario y contraseña incorrectos"}, 401




@app.route("/usuarios", methods=['GET'])
def indexUsuario():
    url = dataConfig["url-backend-security"] + "/usuarios"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/usuarios/<string:id>", methods=['GET'])
def showUsuario(id):
    url = dataConfig["url-backend-security"] + "/usuarios/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/usuarios", methods=['POST'])
def createUsuario():
    url = dataConfig["url-backend-security"] + "/usuarios"
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.post(url, json=body, headers=headers)
    return response.json()


@app.route("/usuarios/<string:id>", methods=['PUT'])
def updateUsuario(id):
    url = dataConfig["url-backend-security"] + "/usuarios/" + id
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.put(url, json=body, headers=headers)
    return response.json()


##no estoy segura de esta funcion
@app.route("/usuarios/<string:idUsuario>/rol/<string:idRol>", methods=['PUT'])
def asignarUsuario(idUsuario, idRol):
    url = dataConfig["url-backend-security"] + "/usuarios/" + idUsuario + "/rol/" + idRol
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.put(url, json=body, headers=headers)
    return response.json()


@app.route("/usuarios/<string:id>", methods=['DELETE'])
def deleteUsuario(id):
    url = dataConfig["url-backend-security"] + "/usuarios/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


####Permiso###
@app.route("/permiso", methods=['GET'])
def indexpermiso():
    url = dataConfig["url-backend-security"] + "/permiso"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/permiso", methods=['POST'])
def createpermiso():
    url = dataConfig["url-backend-security"] + "/permiso"
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.post(url, json=body, headers=headers)
    return response.json()


@app.route("/permiso/<string:id>", methods=['GET'])
def showpermiso(idPermiso):
    url = dataConfig["url-backend-security"] + "/permiso/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/permiso/<string:idPermiso>", methods=['PUT'])
def updatepermiso(idPermiso):
    url = dataConfig["url-backend-security"] + "/permiso/" + idPermiso
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.put(url, json=body, headers=headers)
    return response.json()


@app.route("/permiso/<string:idP>", methods=['DELETE'])
def deletepermiso(idP):
    url = dataConfig["url-backend-security"] + "/permiso/" + idP
    headers = {"Content-Type": "application/json"}
    response = requests.delete(url, headers=headers)
    return response.json()


####Rol####
@app.route("/rol", methods=['GET'])
def indexrol():
    url = dataConfig["url-backend-security"] + "/rol"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/rol", methods=['POST'])
def createrol():
    url = dataConfig["url-backend-security"] + "/rol"
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.post(url, json=body, headers=headers)
    return response.json()


@app.route("/rol/<string:id>", methods=['GET'])
def showrol(id):
    url = dataConfig["url-backend-security"] + "/rol/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/rol/<string:id>", methods=['PUT'])
def updaterol(id):
    url = dataConfig["url-backend-security"] + "/rol/" + id
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.put(url, json=body, headers=headers)
    return response.json()


@app.route("/roles/<string:id>", methods=['DELETE'])
def deleterol(id):
    url = dataConfig["url-backend-security"] + "/rol/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.delete(url, headers=headers)
    return response.json()


####Permiso Rol###


###Rutas Flask###

###Mesa###
@app.route("/Mesa", methods=['POST'])
def crearMesa():
    url = dataConfig["url-backend-academic"] + "/Mesa"
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.post(url, json=body, headers=headers)
    return response.json()


@app.route("/Mesa/<string:id>", methods=['GET'])
def getMesa(id):
    url = dataConfig["url-backend-academic"] + "/Mesa/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/Mesa", methods=['GET'])
def getMesas():
    url = dataConfig["url-backend-academic"] + "/Mesa"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/Mesa/<string:id>", methods=['PUT'])
def modificarMesa(id):
    url = dataConfig["url-backend-academic"] + "/Mesa/" + id
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.put(url, json=body, headers=headers)
    return response.json()


@app.route("/Mesa/<string:id>", methods=['DELETE'])
def eliminarMesa(id):
    url = dataConfig["url-backend-academic"] + "/Mesa/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.delete(url, headers=headers)
    return response.json()


###Partido###

@app.route("/Partido", methods=['POST'])
def crearPartido():
    url = dataConfig["url-backend-academic"] + "/Partido"
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.post(url, json=body, headers=headers)
    return response.json()


@app.route("/Partido/<string:id>", methods=['GET'])
def getPartido(id):
    url = dataConfig["url-backend-academic"] + "/Partido/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/Partido", methods=['GET'])
def getPartidos():
    url = dataConfig["url-backend-academic"] + "/Partido"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/Partido/<string:id>", methods=['PUT'])
def modificarPartido(id):
    url = dataConfig["url-backend-academic"] + "/Partido/" + id
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.put(url, json=body, headers=headers)
    return response.json()


@app.route("/Partido/<string:id>", methods=['DELETE'])
def eliminarPartido(id):
    url = dataConfig["url-backend-academic"] + "/Partido/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.delete(url, headers=headers)
    return response.json()


###Resultado####

@app.route("/Resultado/Mesa/<string:idMesa>/Candidatos/<string:idCandidatos>", methods=['POST'])
def crearResultadoMesaCandidato(idMesa, idCandidatos):
    url = dataConfig["url-backend-academic"] + "/Resultado/" + idMesa + "/Candidatos/" + idCandidatos
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.post(url, json=body, headers=headers)
    return response.json()



@app.route("/Resultado/<string:id>", methods=['GET'])
def getResultadoid(id):
    url = dataConfig["url-backend-academic"] + "/Resultado/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/Resultado", methods=['GET'])
def getResultado():
    url = dataConfig["url-backend-academic"] + "/Resultado"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/Resultado/<string:idR>/Mesa/<string:idM>/Candidatos/<string:idC>", methods=['PUT'])
def modificarResultados(idR, idM, idC):
    url = dataConfig["url-backend-academic"] + "/Resultado/" + idR + "/Mesa/" + idM + "/Candidatos/" + idC
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.put(url, json=body, headers=headers)
    return response.json()


@app.route("/Resultado/<string:id>", methods=['DELETE'])
def eliminarResultado(id):
    url = dataConfig["url-backend-academic"] + "/Resultado/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.delete(url, headers=headers)
    return response.json()




####CANDIDATO###

@app.route("/Candidatos", methods=['POST'])
def crearCandidato():
    url = dataConfig["url-backend-academic"] + "/Candidatos"
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.post(url, json=body, headers=headers)
    return response.json()


@app.route("/Candidatos/<string:id>", methods=['GET'])
def getCandidato(id):
    url = dataConfig["url-backend-academic"] + "/Candidatos/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/Candidatos", methods=['GET'])
def getCandidatos():
    url = dataConfig["url-backend-academic"] + "/Candidatos"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()


@app.route("/Candidatos/<string:id>", methods=['PUT'])
def modificarCandidato(id):
    url = dataConfig["url-backend-academic"] + "/Candidatos/" + id
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    response = requests.put(url, json=body, headers=headers)
    return response.json()


@app.route("/Candidatos/<string:id>", methods=['DELETE'])
def eliminarCandidato(id):
    url = dataConfig["url-backend-academic"] + "/Candidatos/" + id
    headers = {"Content-Type": "application/json"}
    response = requests.delete(url, headers=headers)
    return response.json()



@app.route("/Candidato/<string:idCandidato>/Partido/<string:idPartido>", methods=['PUT'])
def asigPartido(idCandidato, idPartido):
    url = dataConfig["url-backend-academic"] + "/Candidato/" + idCandidato + "/Partido/" + idPartido
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, headers=headers)
    return response.json()


##########################



def loadFileConfig():
    with open('config.json') as propiedades:
        data = json.load(propiedades)
    return data

if __name__ == '__main__':
    dataConfig = loadFileConfig()
    print("Server running: http://" + dataConfig["url-backend"] + ":" + str(dataConfig["port"]))
    serve(app, host=dataConfig["url-backend"], port=dataConfig["port"])