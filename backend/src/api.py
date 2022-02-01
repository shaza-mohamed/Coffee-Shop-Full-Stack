import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def all_drinks():
    try:
        drinks=Drink.query.all()
        drinks= [drink.short() for drink in drinks]
        return json.dumps({"success": True, "drinks": drinks}),200
    except:
        return jsonify({"success": False, "error": "not found"}),401


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def read_drinks_detail(jwt):
    try:
        drinks=Drink.query.all()
        drinks= [drink.long() for drink in drinks]
        return json.dumps({"success": True, "drinks": drinks}),200
    except:
        return json.dumps({"success": False, "error": "Unauthorized"}),401

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(jwt):
    try:
        data = request.get_json()
        new_title = data.get('title')
        new_recipe = json.dumps(data.get('recipe'))
        if ((new_recipe is None) or (new_title is None)):
            abort(422) 
        drink = Drink(
            title=new_title,
            recipe=new_recipe)
        drink.insert()
        return json.dumps({"success": True, "drinks": drink.long()}),200
    except:
        return json.dumps({"success": False, "error": "not Unauthorized"}),401

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def change_drink(jwt, id):
    try:
        data = request.get_json()
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if not drink:
            return json.dumps({"success": False, "error": "not found"}), 404
        else:
            drink.title = data.get('title') if data.get('title') else drink.title
            drink.recipe = json.dumps(data.get('recipe')) if data.get('recipe') else drink.recipe
            drink.update()
            return json.dumps({'success': True, 'drinks': drink.long()}), 200            
    except:
        return json.dumps({"success": False, "error": "not Unauthorized"}),401

    
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink (jwt, id):

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink:
            drink.delete()
            return json.dumps({'success': True, 'delete': id}), 200  
        else:
            return json.dumps({"success": False, "error": "not found"}), 404      
    except:
        return json.dumps({"success": False, "error": "not Unauthorized"}),401



## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
    "success": False, 
    "error": 404,
    "message": "resource not found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
    "success": False,
    "error": 400,
    "message": "bad request"
    }), 400

@app.errorhandler(401)
def Unauthorized(error):
    return jsonify({
    "success": False,
    "error": 401,
    "message": "Unauthorized"
    }), 401
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response