SHELL=/bin/bash

REGISTRY_NAME?=kantale

VERSION=$(shell cat app/views.py | grep "^__version__ =" | cut -d\' -f2)
IMAGE_TAG=$(REGISTRY_NAME)/openbio:$(VERSION)

.PHONY: all develop container container-push release

all: container

develop:
	# Create the Python environment and prepare the application
	if [[ ! -d venv ]]; then python3 -m venv venv; fi
	if [[ -z "$${VIRTUAL_ENV}" ]]; then \
		source venv/bin/activate; \
		pip install -r requirements.txt; \
		python manage.py migrate --run-syncdb \
		python manage.py runserver 0.0.0.0:8200 \
	fi

container:
	docker build -f Dockerfile -t $(IMAGE_TAG) .

container-push:
	docker buildx build --platform linux/amd64,linux/arm64 --push -f Dockerfile -t $(IMAGE_TAG) .

release:
	if git tag -l | grep "^v${VERSION}$$"; then echo "Version ${VERSION} already tagged"; exit 1; fi
	git tag ${VERSION}
	# git push --tags
