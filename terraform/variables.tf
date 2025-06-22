variable "github_repo_owner" {
  description = "Owner del repositorio Git para CodeBuild"
  type        = string
}
variable "buildspec_path" {
    description = "Ruta al archivo buildspec.yml para CodeBuild"
    type        = string
}
variable "tag" {
  description = "Etiqueta de la imagen del contenedor"
  type        = string
}
variable "app" {
  type = string
}
variable "cpu" {
  type = number
}
variable "memory" {
  type = number
}
variable "replicas" {
  type = number
}
variable "port" {
  description = "Puerto del contenedor"
  type        = number
}