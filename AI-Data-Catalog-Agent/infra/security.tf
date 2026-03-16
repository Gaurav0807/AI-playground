
resource "aws_security_group" "alb_sg" {
  name        = "ai-agent-alb-sg"
  description = "Allow HTTP traffic"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" #Allow all outgoing traffic
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ai-agent-alb-sg"
  }
}


resource "aws_lb" "ai_agent_alb" {
  name               = "ai-agent-alb"
  internal           = false
  load_balancer_type = "application"

  security_groups = [
    aws_security_group.alb_sg.id
  ]

  subnets = [
    aws_subnet.public_subnet_1.id,
    aws_subnet.public_subnet_2.id
  ]

  tags = {
    Name = "ai-agent-alb"
  }
}


# Target Group tells the Load Balancer where to send the traffic.
resource "aws_lb_target_group" "ai_agent_tg" {
  name        = "ai-agent-tg"
  port        = 8000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.main_vpc.id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name = "ai-agent-target-group"
  }
}


resource "aws_lb_listener" "ai_agent_listener" {
  load_balancer_arn = aws_lb.ai_agent_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ai_agent_tg.arn
  }
}
