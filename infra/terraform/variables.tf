variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name prefix for resources"
  type        = string
  default     = "day2-infra"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "List of public subnet CIDRs (2 expected)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "List of private subnet CIDRs (2 expected)"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "my_ip_cidr" {
  description = "Your current IP in CIDR form to allow SSH (e.g. 1.2.3.4/32)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "key_name" {
  description = "Existing EC2 key pair name (set empty to use local public key file)"
  type        = string
  default     = ""
}

variable "db_username" {
  description = "Master DB username"
  type        = string
  default     = "db_user"
}

variable "db_password" {
  description = "Master DB password (sensitive)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage (GB)"
  type        = number
  default     = 20
}

variable "rds_hackmate_password" {
  description = "The master password for the RDS instance"
  type        = string
  sensitive   = true
}
