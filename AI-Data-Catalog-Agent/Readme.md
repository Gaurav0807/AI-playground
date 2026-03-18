# AI Data Catalog Agent

An AI-powered agent that queries AWS Glue Data Catalog using natural language. Built with **LangGraph**, **AWS Bedrock (Claude)**, and **FastAPI**, deployed on **AWS ECS Fargate**.



![Agent-Architecture](/workspaces/AI-playground/AI-Data-Catalog-Agent/Agent-AI-Catalog.png)

## Architecture

```
User Request
     |
     v
ALB (port 80) --> ECS Fargate (port 8000) --> FastAPI
                                                  |
                                                  v
                                            LangGraph Agent
                                             /          \
                                            v            v
                                      AWS Bedrock    AWS Glue
                                      (Claude LLM)  (Data Catalog)
```

### Agent Graph Flow

```
START --> agent_node --> should_continue? --> tools (GlueCatalogTool) --> agent_node --> ... --> END
```

- **agent_node**: Sends messages to Bedrock LLM, gets response
- **should_continue**: If LLM made tool calls, route to tools node; otherwise END
- **tools**: Executes Glue catalog lookup, returns result back to agent

## Project Structure

```
AI-Data-Catalog-Agent/
├── app/
│   ├── main.py              # FastAPI app with /ask and / endpoints
│   ├── agent.py             # LangGraph agent with Bedrock LLM + Glue tool
│   └── tools/
│       └── glue_tool.py     # AWS Glue catalog query function
├── infra/
│   ├── providers.tf         # Terraform AWS provider config
│   ├── vpc.tf               # VPC, subnets, internet gateway, route tables
│   ├── ecr.tf               # ECR repository for Docker images
│   ├── iam.tf               # IAM roles (execution role + task role with Glue/Bedrock)
│   ├── security.tf          # Security groups, ALB, target group, listener
│   └── ecs.tf               # ECS cluster, task definition, service, CloudWatch logs
├── Dockerfile               # Container image definition
├── requirements.txt         # Python dependencies
└── README.md
```

## Prerequisites

- Python 3.10+
- AWS CLI configured with valid credentials
- AWS account with access to Bedrock (Claude) and Glue
- Terraform (for cloud deployment)
- Docker (for cloud deployment)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/ask?q=<query>` | Ask the AI agent a question about the data catalog |

### Example

```
GET /ask?q=what tables are in the catalog

Response:
{
    "query": "what tables are in the catalog",
    "answer": "The catalog contains tables: users, orders..."
}
```

## Run Locally

### 1. Create virtual environment and install dependencies

```bash
cd AI-Data-Catalog-Agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set environment variables

```bash
export AWS_REGION="us-east-1"
export BEDROCK_MODEL="anthropic.claude-3-haiku-20240307-v1:0"
```

Ensure AWS credentials are configured (`~/.aws/credentials`, `AWS_PROFILE`, or environment variables).

### 3. Start the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test

```bash
curl http://localhost:8000/
curl "http://localhost:8000/ask?q=what tables are in the catalog"
```

## Deploy to AWS

### 1. Provision infrastructure with Terraform

```bash
cd infra
terraform init
terraform apply
```

This creates: VPC, subnets, internet gateway, ECR repo, ECS cluster, Fargate service, ALB, IAM roles, security groups, and CloudWatch log group.

### 2. Build and push Docker image

```bash
cd AI-Data-Catalog-Agent

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Build for linux/amd64 (required by Fargate)
docker build --platform linux/amd64 -t ai-agent .

# Tag and push
docker tag ai-agent:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/ai-agent-repo-test:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/ai-agent-repo-test:latest
```

### 3. Deploy to ECS

```bash
aws ecs update-service --cluster ai-agent-cluster --service ai-agent-service --force-new-deployment --region us-east-1
```

### 4. Get the ALB URL

```bash
aws elbv2 describe-load-balancers --names ai-agent-alb --region us-east-1 --query 'LoadBalancers[0].DNSName' --output text
```

Test: `http://<ALB_DNS>/ask?q=what tables are in the catalog`

## Redeploy After Code Changes

Every time code changes, run:

```bash
docker build --platform linux/amd64 -t ai-agent .
docker tag ai-agent:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/ai-agent-repo-test:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/ai-agent-repo-test:latest
aws ecs update-service --cluster ai-agent-cluster --service ai-agent-service --force-new-deployment --region us-east-1
```



```bash
# Delete images from ECR first
aws ecr batch-delete-image --repository-name ai-agent-repo-test --image-ids imageTag=latest --region us-east-1

# Destroy all infrastructure
cd infra
terraform destroy
```
