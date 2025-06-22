![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Make](https://img.shields.io/badge/Makefile-0779c9?style=for-the-badge&logo=gnu&logoColor=white)
![CodePipeline](https://img.shields.io/badge/AWS%20CodePipeline-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![ECS Fargate](https://img.shields.io/badge/AWS%20Fargate-FF4F00?style=for-the-badge&logo=amazon-ecs&logoColor=white)
 
![GitHub Repo stars](https://img.shields.io/github/stars/RafaelRodriguezSanz/proyecto-cloud?style=social)

# Proyecto Cloud 

## Deploy Automático en AWS con Terraform

Este proyecto es una demo completa que permite desplegar una aplicación en AWS de forma automatizada utilizando **Terraform**, **Docker**, **AWS CLI** y **CodePipeline**. Proporciona tanto ejecución local como dentro de un contenedor.

---

## ✨ ¿Qué hace este proyecto?

- Clona el código fuente desde un repositorio remoto.
- Usa **AWS CodeBuild** para generar una imagen Docker.
- Despliega la aplicación con **AWS CodePipeline** en **Amazon ECS (Fargate)**.
- Crea automáticamente:
    - Red VPC
    - Subnets públicas/privadas
    - Security Groups
    - Load Balancer (ALB)
- Devuelve la URL del Load Balancer donde se puede acceder a la aplicación desplegada.
- Permite **destruir toda la infraestructura** cuando ya no se necesita.

---

## ⚙️ Precondiciones

Antes de ejecutar este proyecto, asegurate de tener instaladas:

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- [Terraform](https://developer.hashicorp.com/terraform/downloads)
- [Python 3](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [Docker](https://www.docker.com/products/docker-desktop)
- [Make](https://www.gnu.org/software/make/)

---

## 🚀 Cómo ejecutar

### ▶️ Ejecución local

```bash
make local
```

> Esto ejecuta la app directamente en tu entorno local.

---

### 🐳 Ejecución en Docker

Debes pasar las variables de entorno necesarias:

```bash
make run AWS_ACCESS_KEY_ID=xxx AWS_SECRET_ACCESS_KEY=yyy AWS_DEFAULT_REGION=us-east-1
```

Internamente, ejecuta:

```bash
docker run -e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
           -e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
           -e AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) \
           -p 8080:80 \
           proyecto-cloud
```

---

## 🧹 Destruir la infraestructura

Puedes eliminar todos los recursos creados con se puede relizar mediante el frontend de la aplicación o ejecutando:

```bash
cd terraform && terraform destroy -auto-approve
```

---

## 📌 Notas

- Este proyecto es solo una demo y no debe usarse tal cual en producción sin revisiones de seguridad.
- Se recomienda eliminar la infraestructura cuando no se use para evitar costos innecesarios.

---

## 🧑‍💻 Autor

Rafael Rodríguez  
GitHub: [@RafaelRodriguezSanz](https://github.com/RafaelRodriguezSanz)
 
Joaquin Cuitiño
