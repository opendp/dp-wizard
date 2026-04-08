# Team processes

## Privs

Privs should be assigned on a group basis, rather than granted to indivuals.

## Conventions

Branch names should be of the form `NNNN-short-description`, where `NNNN` is the issue number being addressed.

Add developer-only dependencies in `requirements-dev.in`; Add other dependencies in `requirements.in`. After an edit to either file run `scripts/requirements.py` to install the new dependency locally and update `pyproject.toml`.

## Review

"Draft" can be used to indicate that a PR isn't quite ready for review.
If it's not "draft" a reviewer should be assigned.

If the situation calls for it, PRs can be stacked, but we'll try to keep things simple.

## Release

### PyPI

- Make sure you're up to date, and have the git-ignored credentials file `.pypirc`.
- Make one last feature branch with the new version number in the name:
  - Run `scripts/changelog.py` to update the `CHANGELOG.md`.
  - Review the updates and pull a couple highlights to the top.
  - Bump `dp_wizard/VERSION`, and add the new number at the top of the `CHANGELOG.md`.
  - Commit your changes, make a PR, and merge this branch to main.
- Update `main` with the latest changes: `git checkout main; git pull`
- Publish: `flit publish --pypirc .pypirc`

This project is configured so there are two different install possibilities from pypi:
- `pip install 'dp_wizard[pins]'` pins all dependencies, and is the best route for most users.
- Without `[pins]`, dependencies are not pinned. This is best if you're using `dp_wizard` as a library in a larger project.

### Posit Cloud

The cloud deployment is [configured](https://connect.posit.cloud/mccalluc/content/01966942-7eab-da99-0887-a7c483756aa8/edit) to update on pushes to the `cloud-deployment` branch.
If you are on `main`, with no local changes, run `scripts/deploy.sh`.

### Docker Hub

Run `scripts/docker.sh`: This will build and start a new image.
Confirm that it works, and then follow the instructions in the output to push to Docker Hub.
