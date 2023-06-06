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
  access_key = "AKIA2CGV7GJJNH6L3XOP"
  secret_key = "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"
  
}

variable "kevin-test-bucket" {
  type = string
  default = "kevin-test-bucket-377028479240"
}

locals {
  default_tags = {
    Team_Contact = "security@tripactions.com"
    Owner_Contact = "ktruong@tripactions.com"
    Support_Conact = "SOC"
    Environment = "DEV"
    Cost_Center = "cloudsec"
    auto-remediation = "false"
  }
}

locals {
  security_tags = {
    auto-remediation = "true"
  }
}


variable "kevin-log-bucket" {
  type = string
  default = "kevin-log-bucket-377028479240"
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

# -------------------------------------------------------
# ...
# -------------------------------------------------------
resource "aws_s3_bucket_logging" "kevin-bucket" {
  bucket = aws_s3_bucket.kevin-bucket.id
  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = var.kevin-test-bucket
}
