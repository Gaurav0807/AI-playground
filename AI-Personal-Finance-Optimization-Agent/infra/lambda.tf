resource "aws_lambda_function" "test_agent" {
  function_name = "ai-test-agent"

  filename         = data.archive_file.lambda_zip.output_path
  handler          = "handler.handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda_role.arn
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}