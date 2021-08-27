import asyncio

import toml
from elasticsearch import AsyncElasticsearch
from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import HTTPException

from elastic_handler import ElasticHandler

# from flask_restplus import Api, Resource, fields


app = Flask(__name__)
app.config.from_file('../config.toml', toml.load)
# api = Api(app, version='0.0.1', title='flask-app', description='Demo App built using Flask')

print(f"Started app with name: {app.name}")

logger = app.logger
es_async_client = AsyncElasticsearch()
logger.info("Initialization complete!")
data_lst = []
es_handler = ElasticHandler(logger=logger,
                            es=es_async_client,
                            data_lst=data_lst)


@app.errorhandler(HTTPException)
def handle_exception(ex):
    """Return JSON instead of HTML for HTTP errors."""
    response = ex.get_response()
    response.data = jsonify({
        "code": ex.code,
        "name": ex.name,
        "description": ex.description,
    })
    response.content_type = "application/json"
    response.status_code = 500
    return response


@app.errorhandler(Exception)
def handle_exception(ex):
    if isinstance(ex, HTTPException):
        return ex
    return f"Error occurred: {ex}", 500


@app.route('/')
def home():
    try:
        return render_template('default.html')
    except Exception as ex:
        handle_exception(ex)


@app.post('/v1/content/search')
async def content_search():
    input_data = request.json
    resp = await es_handler.get_data(index="full_index")
    return jsonify(
        {
            "input_data": input_data,
            "response": resp,
            "Message": "Submit OK"
        }
    )


@app.post('/v1/content/add')
def content_add():
    input_data = request.json

    resp = es_handler.store_data(
        index="full_index",
        data=str(input_data['content']).lower()
    )
    return jsonify(
        {
            "created": resp
        }
    )


@app.post('/v1/create/index/<name>')
async def create_index(name):
    logger.info(f"Index name: {name}")
    resp = await es_handler.create_index_if_not_exists(index=name)
    if resp.get("created", False):
        return f"Index: {name} has been created", 200
    return f"Index: {name} already exists", 400


if __name__ == "__main__":
    app.run()
