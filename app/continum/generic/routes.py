import os

from continum import app, utils
from flask import render_template


@app.route('/v1/healthcheck')
def health_check():
    return {
        "status": "OK"
    }


@app.route('/')
def home():
    print(os.getcwd())
    return render_template('default.html')
