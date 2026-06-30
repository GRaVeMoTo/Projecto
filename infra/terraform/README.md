# Projecto AWS Infrastructure

Terraform creates the AWS resources needed to publish Projecto Docker images to a private
Amazon ECR repository.

## Resources

- Private ECR repository: `projecto`
- ECR lifecycle policy for old untagged and version-tagged images
- GitHub Actions OIDC provider, unless an existing provider ARN is supplied
- IAM role and policy for GitHub Actions to push Docker images to ECR

## Create Infrastructure

Copy the example variables file and set your GitHub repository name:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Example `terraform.tfvars`:

```hcl
github_repository = "OWNER/REPO"
aws_region        = "eu-central-1"
```

Apply the stack:

```bash
terraform init
terraform plan
terraform apply
```

## Configure GitHub Repository Variables

Set these GitHub repository variables from the Terraform outputs:

- `AWS_ROLE_ARN` = `github_actions_role_arn`
- `ECR_REPOSITORY_URL` = `ecr_repository_url`

The publish workflow uses `eu-central-1` directly because this stack is region-specific.

## Publish Images

Images are published by `.github/workflows/docker-publish.yml` in two cases:

- Manually via workflow dispatch with a version like `v1.2.3`
- Automatically when a GitHub release is published; the release tag is used as the image tag

The ECR repository is immutable, so reusing an existing version tag fails by design.
