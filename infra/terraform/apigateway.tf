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


# resource "aws_api_gateway_rest_api" "rest_api" {
#   name = "${var.project_name}-rest-api"
# }

# resource "aws_api_gateway_resource" "health" {
#   rest_api_id = aws_api_gateway_rest_api.rest_api.id
#   parent_id   = aws_api_gateway_rest_api.rest_api.root_resource_id
#   path_part   = "health"
# }

# resource "aws_api_gateway_method" "health_get" {
#   rest_api_id   = aws_api_gateway_rest_api.rest_api.id
#   resource_id   = aws_api_gateway_resource.health.id
#   http_method   = "GET"
#   authorization = "NONE"
# }

# resource "aws_api_gateway_integration" "mock" {
#   rest_api_id             = aws_api_gateway_rest_api.rest_api.id
#   resource_id             = aws_api_gateway_resource.health.id
#   http_method             = aws_api_gateway_method.health_get.http_method
#   integration_http_method = "GET"
#   type                    = "MOCK"
# }

# resource "aws_api_gateway_deployment" "api_deployment" {
#   rest_api_id = aws_api_gateway_rest_api.rest_api.id

#   depends_on = [aws_api_gateway_integration.mock]
# }

# resource "aws_api_gateway_stage" "api_stage" {
#   stage_name    = "dev"
#   rest_api_id   = aws_api_gateway_rest_api.rest_api.id
#   deployment_id = aws_api_gateway_deployment.api_deployment.id
# }



# --- HTTP API ---
resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.project_name}-http-api"
  protocol_type = "HTTP"
}

# --- Integrations ---
resource "aws_apigatewayv2_integration" "user_service" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "HTTP_PROXY"
  integration_uri        = "http://${aws_instance.web[0].public_ip}:8001/api/{proxy}"
  integration_method     = "ANY"       
  payload_format_version = "1.0"
}

resource "aws_apigatewayv2_integration" "team_service" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "HTTP_PROXY"
  integration_uri        = "http://${aws_instance.web[1].public_ip}:8002/api/{proxy}"
  integration_method     = "ANY"       
  payload_format_version = "1.0"
}

resource "aws_apigatewayv2_integration" "notification_service" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "HTTP_PROXY"
  integration_uri        = "http://${aws_instance.web[2].public_ip}:8003/api/{proxy}"
  integration_method     = "ANY"        
  payload_format_version = "1.0"
}


# --- Routes ---
resource "aws_apigatewayv2_route" "user_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /user/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.user_service.id}"
}

resource "aws_apigatewayv2_route" "team_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /team/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.team_service.id}"
}

resource "aws_apigatewayv2_route" "notification_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /notification/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.notification_service.id}"
}

# --- Stage ---
resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "prod"
  auto_deploy = true
}

# --- WAF Web ACL for IP-based throttling ---
resource "aws_wafv2_web_acl" "api_acl" {
  name        = "${var.project_name}-waf"
  scope       = "REGIONAL"
  description = "Rate limit per IP"
  default_action {
    allow {}
  }
  visibility_config {
    cloudwatch_metrics_enabled = false
    metric_name                = "${var.project_name}-waf"
    sampled_requests_enabled   = false
  }

  rule {
    name     = "RateLimitPerIP"
    priority = 1
    action {
      block {}  
    }

    statement {
      rate_based_statement {
        limit              = 10       # max reqs per 5 minutes per IP
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      sampled_requests_enabled   = false
      cloudwatch_metrics_enabled = false
      metric_name                = "RateLimitPerIP"
    }
  }
}

# --- Associate WAF with API Gateway Stage ---
# resource "aws_wafv2_web_acl_association" "api_assoc" {
#   resource_arn = format(
#     "arn:aws:apigateway:%s::/apis/%s/stages/%s",
#     var.aws_region,
#     aws_apigatewayv2_api.http_api.id,
#     aws_apigatewayv2_stage.prod.name
#   )
#   web_acl_arn = aws_wafv2_web_acl.api_acl.arn
# }



