# Automated Factorio compatibility maintenance

This repository contains two guarded GitHub Actions workflows.

## 1. Daily compatibility watch

`.github/workflows/factorio-version-watch.yml` runs once per day and checks the public Factorio latest-releases API. It compares the latest stable release's `major.minor` compatibility line with `LargerLamps-2.0/info.json`.

When Factorio moves from a line such as `2.1` to `2.2`, the workflow creates one issue titled **Factorio 2.2 compatibility review**. It will not create duplicate issues for the same compatibility line.

The workflow can also be run manually. The optional `target_version` input creates a clearly marked simulation issue. Simulation issues use a separate internal marker, so they can never suppress a real alert for the same Factorio version later.

## 2. Optional AI compatibility attempt

Nothing sends repository code to OpenAI and nothing modifies code until a maintainer adds the `ai-fix-approved` label to the generated issue.

After approval, `.github/workflows/factorio-ai-maintainer.yml`:

1. Verifies that the person who added the label has write, maintain or admin permission.
2. Reads the repository and asks the OpenAI Responses API to consult official Factorio documentation.
3. Applies only compatibility-related file replacements.
4. Blocks all edits to GitHub workflows and to the maintenance scripts themselves.
5. Normalizes `info.json`, the base dependency, the mod patch version, the changelog and the release validator.
6. Runs `python scripts/build_release.py` and `git diff --check`.
7. Pushes a dedicated `ai/factorio-...` branch and opens or updates a **draft** pull request.
8. Adds `needs-testing` to the issue.

The workflow cannot merge the pull request and cannot publish to the Factorio Mod Portal.

## Required repository secret

Add this Actions repository secret before applying `ai-fix-approved`:

- `OPENAI_API_KEY` — an OpenAI API key with enough project credit for one repository review.

Location in GitHub:

`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

## Optional repository variable

- `OPENAI_MODEL` — model used by the Responses API. The default is `gpt-5.6-sol`.

## Recommended first test

1. Manually run **Factorio compatibility watch**.
2. Enter a simulated future target such as `2.2.0`.
3. Confirm that exactly one compatibility issue is created.
4. Add `ai-fix-approved` only after the API secret is configured.
5. Inspect the resulting draft pull request and download the automatic branch prerelease created by the existing build workflow.
6. Test the mod in Factorio with both a clean game and a copy of an existing save.
7. Close the simulated issue and draft PR without merging when the test is complete.
