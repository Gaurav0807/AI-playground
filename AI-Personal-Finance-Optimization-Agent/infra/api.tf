
resource "aws_apigatewayv2_api" "agent_api" {
  name          = "agent-api"
  protocol_type = "HTTP"
}
#This creates an API Gateway HTTP API.

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.agent_api.id
  integration_type       = "AWS_PROXY" # API Gateway forwards request directly to Lambda
  integration_uri        = aws_lambda_function.test_agent.invoke_arn
  payload_format_version = "2.0" #modern HTTP API format
}
# Connects API Gateway → Lambda

#Aws_proxy :- Send Request Directly to Lambda
#invoke arn :- Lambda Execution link

resource "aws_apigatewayv2_route" "agent_route" {
  api_id    = aws_apigatewayv2_api.agent_api.id
  route_key = "POST /analyze"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}" # Send this route to the Lambda integration
}
#Send this route to the Lambda integration

resource "aws_apigatewayv2_stage" "agent_stage" {
  api_id      = aws_apigatewayv2_api.agent_api.id
  name        = "$default"
  auto_deploy = true #Automatically deploy API when changes happen.
}
# Without default stage:
# https://api-id.execute-api.region.amazonaws.com/dev/analyze

# With $default:
# https://api-id.execute-api.region.amazonaws.com/analyze

resource "aws_lambda_permission" "api_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.test_agent.function_name
  principal     = "apigateway.amazonaws.com"
}