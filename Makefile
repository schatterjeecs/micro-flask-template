setup-local-env:
	python -m venv py3venv; \
	source py3venv/bin/activate; \
	pip install -U pip; \
	pip install -r requirements.txt; \

run-app-locally:
	set FLASK_APP=app:main; \
	flask run --reload; \
