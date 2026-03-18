resource "aws_vpc" "main_vpc" {
    cidr_block = "10.0.0.0/16"
    tags = {
      Name = "ai-agent-test"
    }
}

resource "aws_subnet" "public_subnet_1" {
    vpc_id = aws_vpc.main_vpc.id
    cidr_block = "10.0.1.0/24"
    availability_zone = "us-east-1a"

    map_public_ip_on_launch = true

    tags = {
        Name = "ai-agent-public-subnet-1"
    }
}

resource "aws_subnet" "public_subnet_2" {
    vpc_id = aws_vpc.main_vpc.id
    cidr_block = "10.0.2.0/24"
    availability_zone = "us-east-1b"

    map_public_ip_on_launch = true

    tags = {
        Name = "ai-agent-public-subnet-2"
    }
}

#Internet Gateway to access Outside internet request
resource "aws_internet_gateway" "igw" {
    vpc_id = aws_vpc.main_vpc.id
    
    tags = {
        Name = "ai-agent-igw"
    }
}

resource "aws_route_table" "public_route_table" {
    vpc_id = aws_vpc.main_vpc.id
    
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.igw.id
    }

    tags = {
        Name = "ai-agent-public-route-table"
    }
  
}

resource "aws_route_table_association" "subnet1_association" {
    subnet_id = aws_subnet.public_subnet_1.id
    route_table_id = aws_route_table.public_route_table.id
  
}

resource "aws_route_table_association" "subnet2_association" {
    subnet_id = aws_subnet.public_subnet_2.id
    route_table_id = aws_route_table.public_route_table.id
  
}

