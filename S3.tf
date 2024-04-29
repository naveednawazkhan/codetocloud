resource "aws_s3_bucket" "foo-bucket" {
  region        = var.region
  bucket        = local.bucket_name
  force_destroy = true
  acl           = "public-read"
}
