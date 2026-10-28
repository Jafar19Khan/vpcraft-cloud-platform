# AWS account and cost guardrails

VPCraft is designed to keep the default footprint small. It is **not a promise of zero cost**. Free Tier eligibility depends on the account's creation date, selected account plan, region, service, usage and current offer terms.

## EC2 instance eligibility: read this before deployment

This project defaults to **`t3.small` in `ap-south-1` (Mumbai)**. Whether it is covered by an AWS Free Tier offer depends on when the AWS account was created:

- Accounts created **on or after 15 July 2025**: AWS currently lists `t3.small` among eligible EC2 instance types under the newer credit-based offer, subject to the account plan, offer duration/credits, region and usage limits.
- Accounts created **before 15 July 2025**: the legacy EC2 offer lists `t2.micro` or `t3.micro` (where `t2.micro` is unavailable), not `t3.small`. A `t3.small` instance can therefore incur normal charges for these accounts.

Before `terraform apply`, verify the offer in **Billing → Free Tier** and confirm the instance type in the EC2 launch wizard for `ap-south-1`. Do not assume the word “Free Tier” means every account gets `t3.small` at no cost.

## Default footprint

| Resource | Default | Cost note |
|---|---|---|
| EC2 | One configurable instance; default `t3.small` | The default is `t3.small` in `ap-south-1`; it is eligible under the newer offer for qualifying accounts, but not covered by the legacy micro-instance offer. Verify your own account first. |
| EBS | 8 GiB encrypted gp3 root volume | Storage and snapshots may be billable outside allowances. |
| Public IPv4 | One automatically assigned address | Public IPv4 usage can be billable; check current Free Tier allowance and pricing. |
| VPC / Subnet / Internet Gateway / Route Table | One dedicated VPC and one public subnet | No NAT Gateway or VPC endpoints are created. These network primitives have no hourly charge, but public IPv4 and data transfer can incur costs. |
| IAM role / instance profile | EC2 role with Systems Manager core permissions | IAM itself has no EC2-style hourly runtime charge. Session logging to paid destinations is not enabled by this project. |
| Security Group | One minimal group | No separate hourly charge. |
| Database | SQLite on the EC2 volume | No separate RDS instance. |
| Load balancer | None | Avoids hourly and capacity-unit charges. |
| Kubernetes | None in default path | Avoids EKS cluster and worker-node costs. |

## Before deployment

1. Check your account creation date, account plan, credit balance, expiry and EC2 eligibility in AWS Billing / Free Tier.
2. Check the selected EC2 instance type is marked eligible in your account and region.
3. Create a small AWS Budget and billing alerts if your account supports them.
4. Set `aws_region` and `instance_type` deliberately. Do not assume a tutorial's eligibility applies to your account.
5. Run `terraform plan` and review every resource before `terraform apply`.

## Cleanup

Run `terraform destroy` from `infra/` after collecting evidence. Confirm the EC2 instance is terminated and inspect EC2 Volumes, Snapshots, Elastic IPs, Load Balancers, NAT Gateways and RDS in the region. VPCraft does not intentionally create the latter four, but check for resources left by other experiments.

Stopping an instance is not the same as deleting all billable storage or network resources. Never leave resources running just to preserve a screenshot; capture evidence, then destroy the stack.
