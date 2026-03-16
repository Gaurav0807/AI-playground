
resource "aws_ecr_repository" "ai_agent_repo" {
  name ="ai-agent-repo-test" #This will be actual name visible in aws

  image_scanning_configuration {
    scan_on_push = true
  }

  image_tag_mutability = "MUTABLE"

  tags = {
    Name = "ai-agent-ecr"
  }
}