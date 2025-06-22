terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

module "network" {
  source   = "./modules/network"
  port     = var.port
  app      = var.app
}

module "ecr" {
  source = "./modules/ecr"
  app    = var.app
}

module "s3" {
  source = "./modules/s3"
  repository_url = module.ecr.repository_url
  app    = var.app
  tag = var.tag
}

module "ecs" {
  source             = "./modules/ecs"
  repository_url     = module.ecr.repository_url
  subnets            = module.network.public_subnet_ids
  security_groups    = [module.network.ecs_security_group_id]
  port               = var.port
  cpu                = var.cpu
  replicas           = var.replicas
  memory             = var.memory
  tag                = var.tag
  app                = var.app
  target_group_arn   = module.network.lb_tg_arn
}

module "codebuild" {
  source             = "./modules/codebuild"
  ecr_repository_url = module.ecr.repository_url
  s3_bucket_name     = module.s3.bucket_name
  github_repo_owner  = var.github_repo_owner
  buildspec_path     = var.buildspec_path
  app                = var.app
  tag                = var.tag
}

module "codepipeline" {
  source = "./modules/codepipeline"
  repository_url = module.ecr.repository_url
  s3_bucket_name = module.s3.bucket_name
  app    = var.app
  tag = var.tag
}
