output "application_url" {
  description = "VPCraft dashboard URL. Allow a few minutes for first boot."
  value       = "http://${aws_instance.app.public_ip}"
}

output "instance_id" {
  description = "EC2 instance identifier."
  value       = aws_instance.app.id
}

output "public_ip" {
  description = "Public IPv4 address assigned to the instance."
  value       = aws_instance.app.public_ip
}

output "vpc_id" {
  description = "Dedicated VPC identifier."
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "Public subnet identifier."
  value       = aws_subnet.public.id
}

output "security_group_id" {
  description = "Application security group identifier."
  value       = aws_security_group.app.id
}

output "ssm_session_command" {
  description = "Command to open a shell on the instance without SSH."
  value       = "aws ssm start-session --target ${aws_instance.app.id} --region ${var.aws_region}"
}
