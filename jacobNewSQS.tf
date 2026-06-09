resource "aws_sqs_queue" "q" {
  name = "examplequeue"
}

data "aws_iam_policy_document" "test" {
  statement {
    sid    = "First"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.q.arn]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.example.arn]
    }
  }
}

resource "aws_sqs_queue_policy" "test" {
  queue_url = aws_sqs_queue.q.id
  policy    = data.aws_iam_policy_document.test.json
}
