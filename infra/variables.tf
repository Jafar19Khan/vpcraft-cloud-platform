variable "aws_region" {
  description = "AWS region for VPCraft. Mumbai is the default for this learning project."
  type        = string
  default     = "ap-south-1"
}

variable "vpc_cidr" {
  description = "Private IPv4 range for the dedicated VPCraft VPC."
  type        = string
  default     = "10.42.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Public subnet range for the single EC2 host. No NAT Gateway is created."
  type        = string
  default     = "10.42.1.0/24"
}

variable "environment" {
  description = "Deployment environment label."
  type        = string
  default     = "demo"
}

variable "instance_type" {
  description = "EC2 instance type. Confirm account creation date and offer eligibility before apply; older accounts may not receive Free Tier coverage for t3.small."
  type        = string
  default     = "t3.small"
}

variable "allowed_http_cidrs" {
  description = "CIDR ranges allowed to reach HTTP port 80. Restrict to your own IP (x.x.x.x/32) for a private demo."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "github_repo_url" {
  description = "HTTPS URL of the public VPCraft repository used by EC2 user data."
  type        = string
  default     = "https://github.com/Jafar19Khan/vpcraft-cloud-platform.git"
  validation {
    condition     = startswith(var.github_repo_url, "https://github.com/") && !strcontains(var.github_repo_url, "REPLACE_ME")
    error_message = "Set github_repo_url to your actual public GitHub repository URL before planning."
  }
}
