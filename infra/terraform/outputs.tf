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
output "api_gateway_endpoint" {
  description = "API Gateway default endpoint"
  value       = "https://${aws_api_gateway_rest_api.rest_api.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.api_stage.stage_name}"
}