SHELL=/bin/bash

REGISTRY_NAME?=kantale

VERSION=$(shell cat app/views.py | grep "^__version__ =" | cut -d\' -f2)
IMAGE_TAG=$(REGISTRY_NAME)/openbio:$(VERSION)

CHART_DIR=./chart/openbio

.PHONY: all deploy-local undeploy-local develop container container-push release

all: container

deploy-local:
	# Create directory for database
	mkdir -p psql
	helm list -q | grep openbio || \
	helm install openbio $(CHART_DIR) --namespace default \
	--set image="$(IMAGE_TAG)" \
	--set openbio.databaseHostPath="$(PWD)/psql" \
	--set openbio.djangoSecret='!!!!!!!!!!!!!!!thisisasecretkey!!!!!!!!!!!!!!!!' \
	--set openbio.djangoDebug="1" \
	--set openbio.title="OpenBio test" \
	--set openbio.serverURL="http://127.0.0.1:8200" \
	--set openbio.fromEmail="test@example.com" \
	--set openbio.adminEmail="admin@example.com" \
	--set openbio.termsURL="" \
	--set openbio.privacyURL="" \
	--set openbio.showFundingLogos="false" \
	--set openbio.serviceType="LoadBalancer"

undeploy-local:
	helm uninstall openbio --namespace default

develop:
	# Install npm dependencies
	npm install --prefix app/static/app
	npm run get-material-icons --prefix app/static/app
	npm run fix-ace --prefix app/static/app
	# Create the Python environment and prepare the application
	if [[ ! -d venv ]]; then python3 -m venv venv; fi
	if [[ -z "$${VIRTUAL_ENV}" ]]; then \
		source venv/bin/activate; \
		pip install -r requirements.txt; \
		python manage.py migrate --run-syncdb; \
		python manage.py runserver 0.0.0.0:8200; \
	fi
	# python manage.py createsuperuser

container:
	docker build -f Dockerfile --build-arg TARGETARCH=arm64 -t $(IMAGE_TAG) .

container-push:
	docker buildx build --platform linux/amd64,linux/arm64 --push -f Dockerfile -t $(IMAGE_TAG) .

release:
	if git tag -l | grep "^v${VERSION}$$"; then echo "Version ${VERSION} already tagged"; exit 1; fi
	git tag v${VERSION}
	# git push --tags
