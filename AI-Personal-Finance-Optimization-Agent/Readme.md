# AI Personal Finance Optimization Agent on AWS
Using Terraform + AWS Bedrock + Memory + API + Secure Design




![Architecture](/AI-Personal-Finance-Optimization-Agent/Architecture_Diagram.png)





## User uploads bank statement (CSV) → Agent
- Categorizes expenses
- Detects unnecessary subscriptions
- Suggests budget
- Predicts monthly savings
- Stores financial memory

Answers follow-up questions


User (Slack Channel) --> Uploads CSV --> Slack sends event to API Gateway --> API Gateway triggers Lambda --> 
Lambda downloads file from Slack --> Lambda stores CSV in S3 --> Lambda parses transactions --> Lambda calls Bedrock (LLM) --> Lambda responds back to Slack



![Agent Output](/AI-Personal-Finance-Optimization-Agent/ai_agent_output.png)

````
User Input
     │
     ▼
  ┌──────────────────────┐
  │  Content Filters     │──→ Hate/Violence/Sexual/Prompt Attack? → BLOCKED
  │  (input_strength)    │
  └──────────┬───────────┘
             │ Pass
             ▼
  ┌──────────────────────┐
  │  PII Filter           │──→ Credit card found? → BLOCKED
  │  (input scan)         │──→ Email found? → ANONYMIZED (masked)
  └──────────┬───────────┘
             │ Pass
             ▼
  ┌──────────────────────┐
  │  Bedrock Model        │──→ Generates response
  │  (Claude 3 Sonnet)    │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │  Content Filters      │──→ Hate/Violence/Sexual in output? → BLOCKED
  │  (output_strength)    │
  └──────────┬───────────┘
             │ Pass
             ▼
        Response to User
````