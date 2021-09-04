from continum import app, utils


@app.route('/v1/healthcheck')
def health_check():
    return {
        "status": "OK"
    }

