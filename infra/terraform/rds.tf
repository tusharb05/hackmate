resource "aws_db_subnet_group" "rds_subnets" {
  name       = "${var.project_name}-rds-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  tags = { Name = "${var.project_name}-rds-subnet-group" }
}

# resource "random_password" "rds_password" {
#   count   = var.db_password == "" ? 1 : 0
#   length  = 16
#   special = true
# }

resource "aws_db_instance" "postgres" {
  identifier             = "${var.project_name}-postgres"
  allocated_storage      = var.db_allocated_storage
  engine                 = "postgres"
  instance_class         = var.db_instance_class
  db_name                = "postgres"
  username               = var.db_username
  password               = var.rds_hackmate_password
  parameter_group_name   = "default.postgres17"
  db_subnet_group_name   = aws_db_subnet_group.rds_subnets.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  skip_final_snapshot    = true
  publicly_accessible    = false
  tags = { Name = "${var.project_name}-postgres" }
}

