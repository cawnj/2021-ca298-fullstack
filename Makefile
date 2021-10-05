all: run

.PHONY: all

django-deps:
	cd ca298 && \
	pip install -r requirements.txt

node-deps:
	cd node-app && \
	npm install

.PHONY: django-deps node-deps

django-run:
	cd ca298 && \
	python manage.py runserver &

node-run:
	cd node-app && \
	npm start &

.PHONY: django-run node-run

django-stop:
	pkill -f runserver

node-stop:
	killall node

.PHONY: django-stop node-stop

deps: django-deps node-deps

run: django-run node-run

stop: django-stop node-stop

.PHONY: deps run stop
