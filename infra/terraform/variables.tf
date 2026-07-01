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

variable "test_enabled" {
  description = "Whether to create a short-lived EC2 test host running the app and Postgres containers."
  type        = bool
  default     = false
}

variable "test_image_tag" {
  description = "Version tag of the ECR image to run on the test host, for example v1.2.3."
  type        = string
  default     = "v1.0.0"
}

variable "test_instance_type" {
  description = "EC2 instance type for the test host. t3.micro is usually free-tier eligible for new accounts."
  type        = string
  default     = "t3.micro"
}

variable "test_http_cidr_blocks" {
  description = "CIDR blocks allowed to reach the test API on port 8000. Restrict this for non-public tests."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "test_ssh_cidr_blocks" {
  description = "CIDR blocks allowed to SSH to the test host. Empty list disables SSH ingress."
  type        = list(string)
  default     = []
}

variable "test_key_name" {
  description = "Optional EC2 key pair name for SSH access to the test host."
  type        = string
  default     = null
}

variable "test_subnet_id" {
  description = "Optional subnet id for the test host. Leave empty to use the first default VPC subnet."
  type        = string
  default     = ""
}

variable "test_root_volume_size" {
  description = "Root EBS volume size in GiB for the test host."
  type        = number
  default     = 8
}

variable "test_postgres_db" {
  description = "PostgreSQL database name for the test container."
  type        = string
  default     = "projectodb"
}

variable "test_postgres_user" {
  description = "PostgreSQL username for the test container."
  type        = string
  default     = "postgres"
}

variable "test_postgres_password" {
  description = "Optional PostgreSQL password for the test. If unset, Terraform generates one."
  type        = string
  default     = null
  sensitive   = true
}

variable "test_secret_key" {
  description = "Optional application SECRET_KEY for the test. If unset, Terraform generates one."
  type        = string
  default     = null
  sensitive   = true
}
