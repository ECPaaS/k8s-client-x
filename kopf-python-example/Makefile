REPO?=sq/kopf
TAG:=latest
CONTAINER_CLI?=docker

build:
	$(CONTAINER_CLI) build . --file docker/Dockerfile --tag $(REPO):$(TAG)

#push:
#	$(CONTAINER_CLI) push $(REPO):$(TAG)
#all: build push
