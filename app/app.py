import asyncio
import os
import toml
from elasticsearch import AsyncElasticsearch
from aioflask import Flask, render_template, request, json
from werkzeug.exceptions import HTTPException
from functools import lru_cache
import pandas as pd


# from asgiref.wsgi import WsgiToAsgi

from elastic_handler import ElasticHandler

# from flask_restplus import Api, Resource, fields


app = Flask(__name__)
# asgi_app = WsgiToAsgi(app) # does not work

app.config.from_file('../config.toml', toml.load)
# api = Api(app, version='0.0.1', title='flask-app', description='Demo App built using Flask')
logger = app.logger
logger.info(f"Started app with name: {app.name}")

# fix required for running Flask with async on Windows
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

es_async_client = AsyncElasticsearch([
    {'host': 'localhost'},
    {'host': 'es01',
     'port': 9200
     },
])
logger.info("Initialization complete!")
data_lst = []
cache_hashtags = []
es_handler = ElasticHandler(logger=logger,
                            es=es_async_client,
                            data_lst=data_lst)


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


@app.errorhandler(Exception)
def handle_exception(ex):
    if isinstance(ex, HTTPException):
        return ex
    return f"Error occurred: {ex}", 500


@app.route('/v1/healthcheck')
def health_check():
    return {
        "status": "OK"
    }


@app.route('/')
def home():
    try:
        return render_template('default.html')
    except Exception as ex:
        handle_exception(ex)


@app.get('/v1/content/search/<index_name>/<page_from>/<page_size>')
async def content_search(index_name, page_from, page_size):
    resp = await es_handler.get_data(index=index_name,
                                     page_from=page_from,
                                     page_size=page_size)
    return resp


@app.post('/v1/content/load/<index_name>')
async def content_add(index_name):
    input_data = request.json

    resp = await es_handler.store_data(
        index=index_name,
        hashtags=input_data['hashtags']
    )
    return resp


@app.post('/v1/create/index/<index_name>')
async def create_index(index_name):
    logger.info(f"Index name: {index_name}")
    resp = await es_handler.create_index_if_not_exists(index=index_name)
    if resp.get("created", False):
        return f"Index: {index_name} has been created", 200
    return f"Index: {index_name} already exists", 400


@app.get('/v1/unique/hashtags')
async def get_uniq_htags():
    data = await es_handler.get_unique_hashtags()
    return data


@lru_cache(maxsize=16)
async def get_unique_hashtags():
    # return await es_handler.get_unique_hashtags(cache_hashtags)
    body = {
        "size": 0,
        "aggs": {
            "distinct_tags": {
                "terms": {
                    "field": "content.keyword",
                    "size": 1000
                }
            }
        }
    }
    resp = await es_async_client.search(index="digi_hashtags", body=body)
    conv_data = pd.DataFrame(resp['aggregations']['distinct_tags']['buckets']).get("key").values.tolist()
    return conv_data


if __name__ == "__main__":
    app.run()
