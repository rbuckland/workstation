IMAGE_NAME    := rbuckland/workstation
IMAGE_VERSION := 2.4-$(shell git rev-parse --short HEAD)
build:
	docker build -t ${IMAGE_NAME}:${IMAGE_VERSION} . 
