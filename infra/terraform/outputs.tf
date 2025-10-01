output "ec2_public_ips" {
  description = "Public IPs of EC2 instances"
  value       = [for instance in aws_instance.web : instance.public_ip]
}

output "ec2_private_ips" {
  description = "Private IPs of EC2 instances"
  value       = [for instance in aws_instance.web : instance.private_ip]
}

output "rds_endpoint" {
  description = "RDS endpoint (host)"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_port" {
  description = "RDS port"
  value       = aws_db_instance.postgres.port
}

output "s3_bucket" {
  description = "S3 bucket name"
  value       = data.aws_s3_bucket.profile_photos.bucket
}

# output "api_gateway_endpoint" {
#   description = "API Gateway default endpoint"
#   value       = aws_apigatewayv2_stage.api_stage.invoke_url
# }

# output "api_gateway_endpoint" {
#   description = "API Gateway default endpoint"
#   value       = "https://${aws_api_gateway_rest_api.rest_api.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.api_stage.stage_name}"
# }

output "http_api_gateway_endpoint" {
  value = aws_apigatewayv2_stage.prod.invoke_url
}

output "bastion_public_ip" {
  description = "Public IP of the bastion instance"
  value       = aws_instance.bastion.public_ip
}

output "bastion_private_ip" {
  description = "Private IP of the bastion instance"
  value       = aws_instance.bastion.private_ip
}

output "rds_password" {
  description = "RDS password"
  value = aws_db_instance.postgres.password
  sensitive = true
}

output "rabbitmq_host" {
  description = "Private IP of the RabbitMQ instance"
  value       = aws_instance.web[3].private_ip
}

output "rabbitmq_public_ip" {
  description = "Public IP of the RabbitMQ instance (for testing)"
  value       = aws_instance.web[3].public_ip
}


output "user_service_secret_ip" {
  description = "Private IP of User service"
  value = aws_instance.web[0].private_ip
}

output "team_service_secret_ip" {
  description = "Private IP of Team service"
  value = aws_instance.web[1].private_ip
}