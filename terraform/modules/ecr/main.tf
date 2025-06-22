resource "aws_ecr_repository" "this" {
  name = format("%s-repository", var.app)
  force_delete = true
}