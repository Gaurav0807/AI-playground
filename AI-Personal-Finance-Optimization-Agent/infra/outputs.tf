output "api_invoke_url" {
  description = "Base invoke URL of the API Gateway"
  value       = aws_apigatewayv2_stage.agent_stage.invoke_url
}

output "guardrail_id" {
  value = aws_bedrock_guardrail.test_guardrail.guardrail_id
}