resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "codebuild_bucket" {
  bucket = "s3-codebuild-${random_id.bucket_suffix.hex}"
  force_destroy = true
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_s3_bucket_versioning" "codebuild_bucket_versioning" {
  bucket = aws_s3_bucket.codebuild_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

data "archive_file" "imagedefinitions_zip" {
  type        = "zip"
  output_path = "${path.module}/imagedefinitions.zip"

  source {
    content  = jsonencode([
      {
        name     = "${var.app}-container"
        imageUri = "${var.repository_url}:${var.tag}"
      }
    ])
    filename = "imagedefinitions.json"
  }
}

resource "aws_s3_object" "imagedefinitions_zip" {
  bucket       = aws_s3_bucket.codebuild_bucket.id
  key = format("imagedefinitions/%s-%s.zip", var.app, var.tag)
  source       = data.archive_file.imagedefinitions_zip.output_path
  content_type = "application/zip"
}
