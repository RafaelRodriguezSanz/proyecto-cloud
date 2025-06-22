resource "aws_iam_role" "ecs_execution_role" {
  name = "ecsExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_cluster" "this" {
  name = format("%s-cluster", var.app)
}

resource "aws_ecs_task_definition" "this" {
  family                   = format("%s-task", var.app)
  cpu                      = var.cpu
  memory                   = var.memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = format("%s-container", var.app)
      image = format("%s:%s", var.repository_url, var.tag)
      essential = true
      portMappings = [{
        containerPort = var.port
        hostPort      = var.port
        protocol      = "tcp"
      }]
    }
  ])
}

resource "aws_ecs_service" "this" {
  name            = format("%s-service", var.app)
  cluster         = aws_ecs_cluster.this.id
  launch_type     = "FARGATE"
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.replicas

  network_configuration {
    subnets         = var.subnets
    security_groups = var.security_groups
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = format("%s-container", var.app)
    container_port   = var.port
  }

  deployment_controller {
    type = "ECS"
  }
}
