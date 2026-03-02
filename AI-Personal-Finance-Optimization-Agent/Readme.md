# AI Personal Finance Optimization Agent on AWS
Using Terraform + AWS Bedrock + Memory + API + Secure Design

## User uploads bank statement (CSV) → Agent
- Categorizes expenses
- Detects unnecessary subscriptions
- Suggests budget
- Predicts monthly savings
- Stores financial memory

Answers follow-up questions


User (Slack Channel) --> Uploads CSV --> Slack sends event to API Gateway --> API Gateway triggers Lambda --> 
Lambda downloads file from Slack --> Lambda stores CSV in S3 --> Lambda parses transactions --> Lambda calls Bedrock (LLM) --> Lambda responds back to Slack

