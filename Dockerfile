FROM python:3.11-slim

EXPOSE 80
ENV TERRAFORM_VERSION=1.5.7
ENV FLASK_APP=app.py
WORKDIR /app

RUN apt-get update && apt-get install -y \
    unzip \
    curl \
    groff \
    less \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip -o terraform.zip \
    && unzip terraform.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform.zip

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws \

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
