output "public_subnet_ids" {
  description = "IDs de las subnets públicas"
  value       = aws_subnet.public[*].id
}

output "alb_security_group_id" {
  description = "Security Group ID del ALB"
  value       = aws_security_group.alb_sg.id
}

output "ecs_security_group_id" {
  description = "Security Group ID para tareas ECS"
  value       = aws_security_group.ecs_sg.id
}

output "internet_gateway_id" {
  description = "ID del Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "vpc_id" {
  description = "ID de la VPC principal"
  value       = aws_vpc.main.id
}

output "lb_tg_arn" {
  description = "ARN del Target Group del ALB"
  value       = aws_lb_target_group.ecs_tg.arn
}

output "alb_dns_name" {
  value = aws_lb.alb.dns_name
}