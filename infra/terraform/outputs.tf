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
