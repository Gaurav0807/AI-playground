
resource "aws_apigatewayv2_api" "agent_api" {
  name          = "agent-api"
  protocol_type = "HTTP"
}


resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.agent_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.test_agent.invoke_arn
  payload_format_version = "2.0"
}

#Aws_proxy :- Send Request Directly to Lambda
#invoke arn :- Lambda Execution link

resource "aws_apigatewayv2_route" "agent_route" {
  api_id    = aws_apigatewayv2_api.agent_api.id
  route_key = "POST /analyze"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "agent_stage" {
  api_id      = aws_apigatewayv2_api.agent_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.test_agent.function_name
  principal     = "apigateway.amazonaws.com"
}