variable "app" {
  description = "Nombre de la aplicación"
  type        = string
}
variable "repository_url" {
  description = "URL del repositorio ECR para CodeBuild"
  type        = string
}
variable "tag" {
  description = "Etiqueta de la imagen del contenedor"
  type        = string
}
variable "s3_bucket_name" {
  description = "Nombre del bucket S3 para almacenar artefactos de CodeBuild"
  type        = string
}