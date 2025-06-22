resource "aws_iam_role" "codebuild" {
  name = "terraform-codebuild-role"
  assume_role_policy = data.aws_iam_policy_document.codebuild_assume_role.json
}

data "aws_iam_policy_document" "codebuild_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "codebuild_ecr_access" {
  role       = aws_iam_role.codebuild.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_policy_attachment" "codebuild_logs" {
  name       = "codebuild-logs"
  roles      = [aws_iam_role.codebuild.name]
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

resource "aws_iam_policy_attachment" "codebuild_developer" {
  name       = "codebuild-developer-access"
  roles      = [aws_iam_role.codebuild.name]
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeBuildDeveloperAccess"
}

resource "aws_codebuild_project" "this" {
  name          = format("%s-codebuild", var.app)
  service_role  = aws_iam_role.codebuild.arn

  artifacts {
    type     = "S3"
    location = var.s3_bucket_name
    path     = "imagedefinitions"
    packaging = "ZIP"
    name     = format("%s-%s.zip", var.app, var.tag)
  }

  environment {
    compute_type      = "BUILD_GENERAL1_SMALL"
    image             = "aws/codebuild/standard:6.0"
    type              = "LINUX_CONTAINER"
    privileged_mode   = true
    environment_variable {
      name  = "ECR_REPO"
      value = var.ecr_repository_url
    }
    environment_variable {
      name  = "SERVICE"
      value = format("%s-service", var.app)
    }
    environment_variable {
      name  = "TAG"
      value = var.tag
    }
    environment_variable {
      name  = "GITHUB_REPO_OWNER"
      value = var.github_repo_owner
    }
    environment_variable {
      name  = "APP"
      value = var.app
    }
  }

  source {
    type     = "GITHUB"
    location = format("https://github.com/%s/%s.git", var.github_repo_owner, var.app)
    buildspec = file(var.buildspec_path)
  }

}