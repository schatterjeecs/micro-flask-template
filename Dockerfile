# FROM python:3.9.6-slim-buster # only required first time
FROM flask-app:latest

RUN python --version
# RUN mkdir -p flask-app
WORKDIR /flask-app
RUN ls -la
COPY requirements.txt requirements.txt
COPY app app/
COPY config.toml .
RUN ls -la
RUN pip3 install -r requirements.txt
WORKDIR /flask-app/app
RUN pwd
RUN ls -la

# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

ENTRYPOINT ["gunicorn"]
#CMD ["-w", "4", "-t", "10000", "-b", "0.0.0.0:5000", "app:app"]
#CMD ["app:app", "-b", "0.0.0.0:5000", "-k", "gevent", "--worker-connections", "1000"]
CMD ["app:app", "-b", "0.0.0.0:5000", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]
# wont work