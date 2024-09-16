terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.36.1"
    }
  }
}

provider "aws" {

  # Configuration options
  region = "us-west-1"
  access_key = "AKIA2CGV******6L3XOP"
  secret_key = "xysiry7VD5rNDpt9LUaMCJj*********URiCPxtZ"
  
}

# -------------------------------------------------------
# Create S3 Bucket
# -------------------------------------------------------
resource "aws_s3_bucket" "kevin-bucket" {
bucket = var.kevin-test-bucket
tags = local.default_tags
}




# -------------------------------------------------------
# Enable S3 access logging
# -------------------------------------------------------
resource "aws_s3_bucket" "log_bucket" {
bucket = var.kevin-log-bucket
force_destroy = true
}




resource "aws_s3_bucket_logging" "kevin-bucket" {
bucket = aws_s3_bucket.kevin-bucket.id

target_bucket = aws_s3_bucket.log_bucket.id
target_prefix = data.aws_caller_identity.current.account_id
}
