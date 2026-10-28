# Portfolio evidence checklist

Capture screenshots from your own successful run. Save them in `screenshots/` with the exact names below.

| # | File name | What to capture | What it proves |
|---|---|---|---|
| 01 | `01-github-repo.png` | GitHub repository home page (README, folders, topics) | Professional repository |
| 02 | `02-github-actions-green.png` | Actions tab: all 3 jobs green (tests, container smoke test, Terraform validation) | CI quality gates pass |
| 03 | `03-local-dashboard.png` | Dashboard at `http://localhost:8080` | Application works locally |
| 04 | `04-docker-compose-ps.png` | Terminal: `docker compose ps` showing healthy | Containers healthy |
| 05 | `05-terraform-validate.png` | Terminal: `terraform fmt -check` and `terraform validate` | Infrastructure code quality |
| 06 | `06-terraform-plan.png` | Terminal: `terraform plan` summary (resources to add) | Exact infra planned before creation |
| 07 | `07-terraform-apply.png` | Terminal: `terraform apply` complete with outputs | Successful provisioning |
| 08 | `08-ec2-instance.png` | EC2 console: instance running, type, region ap-south-1 | Compute created |
| 09 | `09-vpc-subnet-routes.png` | VPC console: VPC, public subnet, route table with IGW route | Custom networking |
| 10 | `10-security-group.png` | Security Group inbound rules: only HTTP 80, no SSH | Least-privilege network |
| 11 | `11-ssm-managed-node.png` | Systems Manager → Fleet Manager: instance online | SSH-less administration |
| 12 | `12-aws-dashboard.png` | Dashboard at `http://<public-ip>` with live metrics and instance details | Live deployment |
| 13 | `13-health-endpoints.png` | Browser/terminal: `/health`, `/ready`, `/api/status` JSON | Runtime health checks |
| 14 | `14-bootstrap-log.png` | SSM session: `sudo tail -n 40 /var/log/vpcraft-bootstrap.log` | Automated bootstrap |
| 15 | `15-billing-free-tier.png` | Billing → Free Tier usage (hide account ID) | Cost awareness |
| 16 | `16-terraform-destroy.png` | Terminal: `terraform destroy` complete + empty EC2 list | Responsible teardown |

Best 4 for the README: 12, 02, 09 and 10.

## Screenshot hygiene

- Hide account IDs, email addresses, access keys, tokens and personal browser tabs.
- Never capture `.env`, private keys, Terraform state or credentials.
- Take 12 and 13 **before** running `terraform destroy`.

## README snippet (paste after capturing)

```markdown
## Screenshots

| Live dashboard on AWS | CI pipeline |
|---|---|
| ![Dashboard](screenshots/12-aws-dashboard.png) | ![CI](screenshots/02-github-actions-green.png) |

| VPC and routing | Security group |
|---|---|
| ![VPC](screenshots/09-vpc-subnet-routes.png) | ![Security group](screenshots/10-security-group.png) |
```
