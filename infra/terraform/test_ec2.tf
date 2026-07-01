locals {
  test_container_name = "projecto-api"
  test_database_url = var.test_enabled ? format(
    "postgresql+psycopg://%s:%s@projecto-db:5432/%s",
    var.test_postgres_user,
    local.test_postgres_password,
    var.test_postgres_db,
  ) : ""
  test_postgres_password = var.test_postgres_password != null ? var.test_postgres_password : try(random_password.test_postgres[0].result, "")
  test_secret_key        = var.test_secret_key != null ? var.test_secret_key : try(random_password.test_secret_key[0].result, "")
}

resource "random_password" "test_postgres" {
  count   = var.test_enabled && var.test_postgres_password == null ? 1 : 0
  length  = 24
  special = false
}

resource "random_password" "test_secret_key" {
  count   = var.test_enabled && var.test_secret_key == null ? 1 : 0
  length  = 48
  special = false
}

data "aws_caller_identity" "current" {}

data "aws_vpc" "default" {
  count   = var.test_enabled && var.test_subnet_id == "" ? 1 : 0
  default = true
}

data "aws_subnets" "default" {
  count = var.test_enabled && var.test_subnet_id == "" ? 1 : 0

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default[0].id]
  }
}

data "aws_subnet" "selected" {
  count = var.test_enabled ? 1 : 0
  id    = var.test_subnet_id != "" ? var.test_subnet_id : data.aws_subnets.default[0].ids[0]
}

data "aws_ami" "amazon_linux" {
  count       = var.test_enabled ? 1 : 0
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_security_group" "test" {
  count       = var.test_enabled ? 1 : 0
  name        = "projecto-test"
  description = "Projecto short-lived test host access"
  vpc_id      = data.aws_subnet.selected[0].vpc_id

  ingress {
    description = "Projecto API"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = var.test_http_cidr_blocks
  }

  dynamic "ingress" {
    for_each = length(var.test_ssh_cidr_blocks) > 0 ? [1] : []

    content {
      description = "SSH"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = var.test_ssh_cidr_blocks
    }
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_iam_policy_document" "test_assume_role" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type = "Service"
      identifiers = [
        "ec2.amazonaws.com",
      ]
    }
  }
}

resource "aws_iam_role" "test" {
  count              = var.test_enabled ? 1 : 0
  name               = "projecto-test-ec2"
  assume_role_policy = data.aws_iam_policy_document.test_assume_role.json
}

data "aws_iam_policy_document" "test_ecr_pull" {
  statement {
    effect = "Allow"

    actions = [
      "ecr:GetAuthorizationToken",
    ]

    resources = ["*"]
  }

  statement {
    effect = "Allow"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
    ]

    resources = [
      aws_ecr_repository.projecto.arn,
    ]
  }
}

resource "aws_iam_policy" "test_ecr_pull" {
  count  = var.test_enabled ? 1 : 0
  name   = "projecto-test-ecr-pull"
  policy = data.aws_iam_policy_document.test_ecr_pull.json
}

resource "aws_iam_role_policy_attachment" "test_ecr_pull" {
  count      = var.test_enabled ? 1 : 0
  role       = aws_iam_role.test[0].name
  policy_arn = aws_iam_policy.test_ecr_pull[0].arn
}

resource "aws_iam_role_policy_attachment" "test_ssm" {
  count      = var.test_enabled ? 1 : 0
  role       = aws_iam_role.test[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "test" {
  count = var.test_enabled ? 1 : 0
  name  = "projecto-test-ec2"
  role  = aws_iam_role.test[0].name
}

resource "aws_instance" "test" {
  count = var.test_enabled ? 1 : 0

  ami                         = data.aws_ami.amazon_linux[0].id
  instance_type               = var.test_instance_type
  subnet_id                   = data.aws_subnet.selected[0].id
  vpc_security_group_ids      = [aws_security_group.test[0].id]
  key_name                    = var.test_key_name
  iam_instance_profile        = aws_iam_instance_profile.test[0].name
  associate_public_ip_address = true
  user_data_replace_on_change = true

  root_block_device {
    volume_size = var.test_root_volume_size
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = templatefile("${path.module}/templates/test-user-data.sh.tftpl", {
    aws_region        = var.aws_region
    aws_account_id    = data.aws_caller_identity.current.account_id
    ecr_repository    = aws_ecr_repository.projecto.name
    ecr_repository_url = aws_ecr_repository.projecto.repository_url
    image_tag         = var.test_image_tag
    postgres_user     = var.test_postgres_user
    postgres_password = local.test_postgres_password
    postgres_db       = var.test_postgres_db
    database_url      = local.test_database_url
    secret_key        = local.test_secret_key
    container_name    = local.test_container_name
  })

  tags = {
    Name = "projecto-test"
  }

  depends_on = [
    aws_iam_role_policy_attachment.test_ecr_pull,
    aws_iam_role_policy_attachment.test_ssm,
  ]
}
