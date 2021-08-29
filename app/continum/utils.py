from continum import app
from aioflask import json
from werkzeug.exceptions import HTTPException
from multipledispatch import dispatch


@dispatch(HTTPException)
@app.errorhandler(HTTPException)
def handle_exception(ex):
    """Return JSON instead of HTML for HTTP errors."""
    response = ex.get_response()
    response.data = json.dumps({
        "code": ex.code,
        "name": ex.name,
        "description": ex.description,
    })
    response.content_type = "application/json"
    return response


@dispatch(Exception)
@app.errorhandler(Exception)
def handle_exception(ex):
    if isinstance(ex, HTTPException):
        return ex
    return f"Error occurred: {ex}", 500


@dispatch(type, str)
def handle_exception(ex, er_msg: str):
    return f"Error: {er_msg}", 400
