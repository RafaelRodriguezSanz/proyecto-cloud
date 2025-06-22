variable "app" {
  type = string
}

variable "cpu" {
  type = number
}

variable "memory" {
  type = number
}

variable "repository_url" {
  type = string
}

variable "tag" {
  type = string
}

variable "port" {
  type = number
}

variable "replicas" {
  type = number
}

variable "subnets" {
  type = list(string)
}

variable "security_groups" {
  type = list(string)
}

variable "target_group_arn" {
  type = string
}
