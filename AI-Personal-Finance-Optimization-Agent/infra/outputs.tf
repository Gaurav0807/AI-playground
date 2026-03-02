output "api_invoke_url" {
  description = "Base invoke URL of the API Gateway"
  value       = aws_apigatewayv2_stage.agent_stage.invoke_url
}