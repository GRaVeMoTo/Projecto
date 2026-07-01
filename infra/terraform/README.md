# Projecto AWS Infrastructure

Terraform creates the AWS resources needed to publish Projecto Docker images to a private
Amazon ECR repository. It can also create an optional short-lived EC2 test host that runs the
published API image together with a PostgreSQL container.

## Resources

- Private ECR repository: `projecto`
- ECR lifecycle policy for old untagged and version-tagged images
- GitHub Actions OIDC provider, unless an existing provider ARN is supplied
- IAM role and policy for GitHub Actions to push Docker images to ECR
- Optional EC2 test host with Docker, the Projecto API container, and a PostgreSQL container

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

## Optional Free-Tier Style Test Host

The test host is disabled by default. Enable it only after an image has already been published to
ECR with the selected version tag.

Example `terraform.tfvars` additions:

```hcl
test_enabled   = true
test_image_tag = "v1.0.0"

# Strongly recommended: restrict the test API to your own IP.
test_http_cidr_blocks = ["203.0.113.10/32"]

# Optional SSH access. Leave unset/empty if you do not need SSH.
# test_key_name        = "your-ec2-key-pair"
# test_ssh_cidr_blocks = ["203.0.113.10/32"]
```

Apply the change:

```bash
terraform plan -out=projecto-test.tfplan
terraform apply projecto-test.tfplan
```

Outputs:

- `test_api_url` - API URL, for example `http://1.2.3.4:8000`
- `test_public_ip` - EC2 public IP address
- `test_instance_id` - EC2 instance id
- `test_image` - ECR image used by the instance

The EC2 user data script:

- installs Docker and AWS CLI
- logs in to ECR with the instance IAM role
- starts `postgres:18.4-alpine`
- runs `alembic upgrade head`
- starts the Projecto API on port `8000`

Bootstrap logs are available on the instance at:

```bash
/var/log/projecto-test-bootstrap.log
```

Destroy the test when you are done to avoid ongoing EC2, EBS, public IPv4, and data-transfer costs:

```bash
terraform destroy
```

If you want to keep ECR/OIDC resources but remove only the test, set:

```hcl
test_enabled = false
```

Then run:

```bash
terraform apply
```
