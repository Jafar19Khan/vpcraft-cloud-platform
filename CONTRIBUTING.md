# Contributing to VPCraft

Thanks for helping improve VPCraft. Contributions should be understandable, testable and safe to run in a personal AWS account.

## Before opening a pull request

1. Open an issue for substantial changes.
2. Explain the problem and the proposed approach.
3. Identify any new AWS services, persistent resources or possible costs.
4. Never include credentials, account IDs, private keys, `.env` files or Terraform state.

## Local checks

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
terraform -chdir=infra fmt -check -recursive
terraform -chdir=infra init -backend=false
terraform -chdir=infra validate
```

Build the container with `docker build -t vpcraft:dev .` when Docker is available.

## Pull request expectations

- Keep the README and relevant docs in sync.
- Add tests for changed application behaviour.
- Explain security-group, IAM, network or storage changes.
- Prefer opt-in infrastructure for services that can create ongoing charges.
- Do not claim AWS deployment success unless it was actually tested.
