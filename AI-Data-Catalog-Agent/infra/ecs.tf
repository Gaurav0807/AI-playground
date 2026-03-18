
resource "aws_ecs_cluster" "ai_agent_cluster" {
    name="ai-agent-cluster"

    setting { #Monitor Container in amazon cloudwatch
      name = "containerInsights"
      value = "enabled"
    }

    tags = {
      Name="ai-agent-ecs-cluster"
    }
  
}

resource "aws_ecs_task_definition" "ai_agent_task" {
  family                   = "ai-agent-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"] #Run this container using Fargate

  cpu    = "256"
  memory = "512"

  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "ai-agent-container"
      image = "${aws_ecr_repository.ai_agent_repo.repository_url}:latest"

      essential = true
      environment = [
        {
            name  = "AWS_REGION"
            value = "us-east-1"
        },
        {
            name  = "BEDROCK_MODEL"
            value = "anthropic.claude-v2"
        }
    ]

      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/ai-agent"
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}


resource "aws_ecs_service" "ai_agent_service" {
  name            = "ai-agent-service"
  cluster         = aws_ecs_cluster.ai_agent_cluster.id
  task_definition = aws_ecs_task_definition.ai_agent_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets = [
      aws_subnet.public_subnet_1.id,
      aws_subnet.public_subnet_2.id
    ]
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ai_agent_tg.arn
    container_name   = "ai-agent-container"
    container_port   = 8000
  }

  depends_on = [
    aws_lb_listener.ai_agent_listener
  ]
}

