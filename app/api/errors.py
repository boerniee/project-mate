from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
    payload = {
        'error': message if message else HTTP_STATUS_CODES.get(status_code, 'Unknown error'),
        'code': status_code
        }
    response = jsonify(payload)
    response.status_code = status_code
    return response
