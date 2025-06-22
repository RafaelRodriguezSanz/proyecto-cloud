.PHONY: run build
run: build
	docker run -e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	           -e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	           -e AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) \
	           -p 8080:80 \
	           proyecto-cloud
	open https://localhost:8080

build:
	docker build -t proyecto-cloud .


local:
	pip install -r requirements.txt && python app.py