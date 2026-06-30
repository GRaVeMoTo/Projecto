variable "aws_region" {
  description = "AWS region where Projecto infrastructure is created."
  type        = string
  default     = "eu-central-1"
}

variable "ecr_repository_name" {
  description = "Private ECR repository name for the Projecto application image."
  type        = string
  default     = "projecto"
}

variable "github_repository" {
  description = "GitHub repository allowed to assume the publish role, in owner/repo format."
  type        = string
}

variable "github_oidc_provider_arn" {
  description = "Existing GitHub OIDC provider ARN. Leave empty to create one."
  type        = string
  default     = ""
}

variable "image_retention_count" {
  description = "Number of tagged ECR images to keep."
  type        = number
  default     = 30
}
