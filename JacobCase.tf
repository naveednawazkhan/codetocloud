resource "aws_dynamodb_table" "emails_to_process" {
  name = "EmailsToProcess"
  # billing_mode = "PAY_PER_REQUEST"
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "EmailsToProcessID"
  range_key      = "Account"
  attribute {
    name = "EmailsToProcessID"
    type = "S"
  }
  attribute {
    name = "Account"
    type = "S"
  }
  point_in_time_recovery {
    enabled = true
  }
  server_side_encryption {
    enabled = true
  }
}

resource "aws_dynamodb_table" "valid_email_addresses" {
  name = "ValidEmailDestinations"
  # billing_mode = "PAY_PER_REQUEST"
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "ValidEmailDestinationID"
  attribute {
    name = "ValidEmailDestinationID"
    type = "S"
  }
  point_in_time_recovery {
    enabled = true
  }
  server_side_encryption {
    enabled = true
  }
}
