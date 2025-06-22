output "cluster_name" {
  value = aws_ecs_cluster.this.name
}

output "service_name" {
  value = aws_ecs_service.this.name
}

output "execution_role_arn" {
  value = aws_iam_role.ecs_execution_role.arn
}
