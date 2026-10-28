# Troubleshooting

## The public URL does not respond after `terraform apply`

First boot installs Docker, clones the repository and builds the images. Allow 6 to 8 minutes, then read the boot log:

```bash
aws ec2 get-console-output --instance-id $(terraform output -raw instance_id) --region ap-south-1 --latest --output text | tail -n 40
```

| Marker in the log | Meaning |
|---|---|
| `VPCRAFT_BOOTSTRAP_STARTED` | Bootstrap script is running |
| `VPCRAFT_BOOTSTRAP_COMPLETE` | Application answered `/ready`; the URL works |
| `VPCRAFT_BOOTSTRAP_FAILED at line N` | A step failed; read the lines above it |

Console output can lag by a few minutes.

## Common causes

- **Repository not reachable.** `github_repo_url` in `terraform.tfvars` must point to a public repository that contains `compose.yaml` at its root.
- **Port 80 blocked.** Check that `allowed_http_cidrs` includes your current public IP.
- **Instance replaced.** A new instance gets a new public IP; use the `application_url` output.

## Inspect the instance without SSH

Use EC2 Console, Connect, Session Manager (or the `ssm_session_command` output), then:

```bash
sudo tail -n 80 /var/log/vpcraft-bootstrap.log
sudo docker ps -a
cd /opt/vpcraft && sudo docker compose logs --tail 50
```

## Re-run the bootstrap on a fresh instance

```bash
terraform apply -replace=aws_instance.app
```
