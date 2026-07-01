output "aws_region" {
  description = "AWS region used by this stack."
  value       = var.aws_region
}

output "ecr_repository_url" {
  description = "Private ECR repository URL for Docker image pushes."
  value       = aws_ecr_repository.projecto.repository_url
}

output "github_actions_role_arn" {
  description = "IAM role ARN for GitHub Actions OIDC publishing."
  value       = aws_iam_role.github_actions_ecr_publish.arn
}

output "github_oidc_provider_arn" {
  description = "GitHub Actions OIDC provider ARN used by the publish role."
  value       = local.github_oidc_provider_arn
}

output "test_public_ip" {
  description = "Public IP address of the optional EC2 test host."
  value       = var.test_enabled ? aws_instance.test[0].public_ip : null
}

output "test_api_url" {
  description = "HTTP URL of the optional EC2 test API."
  value       = var.test_enabled ? "http://${aws_instance.test[0].public_ip}:8000" : null
}

output "test_instance_id" {
  description = "Instance ID of the optional EC2 test host."
  value       = var.test_enabled ? aws_instance.test[0].id : null
}

output "test_image" {
  description = "ECR image used by the optional EC2 test host."
  value       = var.test_enabled ? "${aws_ecr_repository.projecto.repository_url}:${var.test_image_tag}" : null
}
