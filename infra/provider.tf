provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "VPCraft"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}
