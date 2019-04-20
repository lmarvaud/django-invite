ADMIN_PASSWORD		?= admin
CSV                 ?= ./demo/example.csv
EXTRA_PIP_INSTALL	?= -r requirements-dev.txt
PYTHON_SOURCE		= $(shell find invite/ demo/ -name '*.py')
PYTHON			?= ${VIRTUAL_ENV}/bin/python
PYTHON_VERSION		?= python3.5
VIRTUAL_ENV		?= ./venv

ifneq (,$(wildcard ./.env))
include .env
endif

all: venv database adminuser importguests runserver

.PHONY: coverage-test
coverage-test:
	$(info run tests)
	${VIRTUAL_ENV}/bin/coverage run ./manage.py test -v3

.PHONY: coverage-report
coverage-report:
	$(info report on coverage)
	${VIRTUAL_ENV}/bin/coverage report --show-missing

.PHONY: importguests
importguests:
	$(info import guests from CSV file)
	${PYTHON} ./manage.py importguests --name='${EVENT_NAME}' --date='${EVENT_DATE}' '${CSV}'

.PHONY: adminuser
adminuser:
	$(info create superuser (admin/${ADMIN_PASSWORD}))
	@echo 'from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser("admin", "admin@example.com", "${ADMIN_PASSWORD}")' | ${PYTHON} ./manage.py shell

.PHONY: database
database:
	$(info init database)
	@${PYTHON} ./manage.py migrate

.PHONY: migrations
migrations:
	@${PYTHON} ./manage.py makemigrations

.PHONY: pylint
pylint:
	@${PYTHON} -m pylint ${PYTHON_SOURCE}

.PHONY: reset-database
reset-database:
	$(info reset database)
	@rm -f db.sqlite3

.PHONY: runserver
runserver:
	@${PYTHON} ./manage.py runserver

.PHONY: superuser
superuser:
	@${PYTHON} ./manage.py createsuperuser

.PHONY: test
test: coverage-test coverage-report

.PHONY: venv
venv:
	$(info init virtual env)
ifeq (,$(wildcard $(VIRTUAL_ENV)))
	@'${PYTHON_VERSION}' -m virtualenv -p $(PYTHON_VERSION) $(VIRTUAL_ENV)
endif
	@'${VIRTUAL_ENV}/bin/pip' install . $(EXTRA_PIP_INSTALL)
