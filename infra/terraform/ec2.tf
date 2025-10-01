resource "tls_private_key" "rsa" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated" {
  count      = var.key_name == "" ? 1 : 0
  key_name   = "${var.project_name}-key"
  public_key = tls_private_key.rsa.public_key_openssh
}

resource "local_file" "ssh_private_key" {
  content         = tls_private_key.rsa.private_key_pem
  filename        = "${path.module}/ssh-key.pem"
  file_permission = "0400"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}


resource "aws_instance" "web" {
  count                       = 4
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public[0].id
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.ec2_sg.id]
  key_name                    = var.key_name != "" ? var.key_name : aws_key_pair.generated[0].key_name

  tags = {
    Name = "${var.project_name}-web-${count.index + 1}"
  }
}

resource "aws_instance" "bastion" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public[0].id
  associate_public_ip_address = true
  key_name                    = var.key_name != "" ? var.key_name : aws_key_pair.generated[0].key_name
  vpc_security_group_ids      = [aws_security_group.bastion_sg.id]

  tags = {
    Name = "${var.project_name}-bastion"
  }
}


# resource "tls_private_key" "rsa" {
#   algorithm = "RSA"
#   rsa_bits  = 4096
# }

# resource "aws_key_pair" "generated" {
#   count      = var.key_name == "" ? 1 : 0
#   key_name   = "${var.project_name}-key"
#   public_key = tls_private_key.rsa.public_key_openssh
# }

# resource "local_file" "ssh_private_key" {
#   content  = tls_private_key.rsa.private_key_pem
#   filename = "${path.module}/ssh-key.pem"
#   file_permission = "0400"
# }

# data "aws_ami" "ubuntu" {
#   most_recent = true
#   owners      = ["099720109477"] # Canonical

#   filter {
#     name   = "name"
#     values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
#   }
# }

# resource "aws_instance" "web" {
#   ami                         = data.aws_ami.ubuntu.id
#   instance_type               = var.instance_type
#   subnet_id                   = aws_subnet.public[0].id
#   associate_public_ip_address = true
#   vpc_security_group_ids      = [aws_security_group.ec2_sg.id]
#   key_name                    = var.key_name != "" ? var.key_name : aws_key_pair.generated[0].key_name

#   tags = {
#     Name = "${var.project_name}-web"
#   }

#   # User data for Ubuntu
#   user_data = <<-EOF
#               #!/bin/bash
#               apt-get update -y
#               apt-get install -y postgresql-client
#               EOF
# }


