from continum import app, es_client, utils, logger
from aioflask import request
from continum.contents.models import in_model
from werkzeug.exceptions import BadRequest
from continum.contents.services.elastic_handler import ElasticHandler

cache_hashtags = []
es_handler = ElasticHandler(logger=logger,
                            es=es_client)


@app.get('/v1/content/search/<index_name>/<page_from>/<page_size>')
async def content_search(index_name, page_from, page_size):
    return await es_handler.get_data(index=index_name,
                                     page_from=page_from,
                                     page_size=page_size)


@app.post('/v1/content/load/<index_name>')
async def content_add(index_name):
    errors = in_model.InputModel().validate(request.json)
    if errors:
        return utils.handle_exception(BadRequest, str(errors))

    input_data = request.json
    resp = await es_handler.load_data(
        index=index_name,
        hashtags=input_data['hashtags']
    )
    return f"Created Ids: {resp}"


@app.post('/v1/content/create/index/<index_name>')
async def create_index(index_name):
    logger.debug(f"Index name: {index_name}")
    resp = await es_handler.create_index_if_not_exists(index=index_name)
    if resp.get("created", False):
        return f"Index: {index_name} has been created", 200
    return f"Index: {index_name} already exists", 400


@app.get('/v1/content/unique/hashtags')
async def get_uniq_htags():
    return await es_handler.get_unique_hashtags()