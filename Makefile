install: environment requirements

server:
	env/bin/python manage.py runserver 0.0.0.0:8000

environment:
	test -d "env" || virtualenv --no-site-packages env

requirements:
	env/bin/pip install -r requirements.txt
