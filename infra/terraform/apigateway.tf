# resource "aws_apigatewayv2_api" "http_api" {
#   name          = "${var.project_name}-http-api"
#   protocol_type = "HTTP"
# }

# resource "aws_apigatewayv2_integration" "mock" {
#   api_id           = aws_apigatewayv2_api.http_api.id
#   integration_type = "MOCK"
# }

# resource "aws_apigatewayv2_route" "health" {
#   api_id    = aws_apigatewayv2_api.http_api.id
#   route_key = "GET /health"
#   target    = "integrations/${aws_apigatewayv2_integration.mock.id}"
# }

# resource "aws_apigatewayv2_stage" "api_stage" {
#   api_id      = aws_apigatewayv2_api.http_api.id
#   name        = "prod"
#   auto_deploy = true
# }


resource "aws_api_gateway_rest_api" "rest_api" {
  name = "${var.project_name}-rest-api"
}

resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  parent_id   = aws_api_gateway_rest_api.rest_api.root_resource_id
  path_part   = "health"
}

resource "aws_api_gateway_method" "health_get" {
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "mock" {
  rest_api_id             = aws_api_gateway_rest_api.rest_api.id
  resource_id             = aws_api_gateway_resource.health.id
  http_method             = aws_api_gateway_method.health_get.http_method
  integration_http_method = "GET"
  type                    = "MOCK"
}

resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id

  depends_on = [aws_api_gateway_integration.mock]
}

resource "aws_api_gateway_stage" "api_stage" {
  stage_name    = "dev"
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  deployment_id = aws_api_gateway_deployment.api_deployment.id
}






# Construct invoke url output (aws_apigatewayv2_stage provides invoke_url in newer provider versions)

# ---

## terraform.tfvars.example

# Copy this to terraform.tfvars and update values
# aws_region            = "ap-south-1"
# project_name          = "day2-infra"
# my_ip_cidr            = "YOUR_IP/32" # e.g. 1.2.3.4/32
# instance_type         = "t3.micro"
# key_name              = "" # or existing key pair name
# Either provide db_password or leave empty to have Terraform generate one
# db_password         = "supersecurepassword"