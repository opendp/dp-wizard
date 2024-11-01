# Introduction

## Purpose

Automate the end-to-end testing of the application to ensure it meets user requirements and maintains reliability, especially in the context of privacy-preserving data processing.

## Project Overview

# Scope

## In-Scope

- Starting the application with and without `--demo` and other CLI flags.
- Form filling and navigation between tabs.
- Conditionally disabled controls (for example, controls late in the flow when inputs have not been provided, and controls early in the flow after the release has been made).
- Report export.
- Runnability of any generated code.

## Out-of-Scope

- Performance testing: Test timeouts may incidentally identify components which are slow ([issue](https://github.com/opendp/dp-creator-ii/issues/116)), but it's not the focus of automated testing.
- Rendering of preview charts: Might [add results table](https://github.com/opendp/dp-creator-ii/issues/122) to complement graphs, but we're not going to try to make any assertions against images.
- Testing exact values: The outputs is randomized, so we can not test for any particular value in the output.
- Design and usability.
- Correctness of DP calculations.

# Testing Strategy

## Test Objectives

- Ensure reliable execution of user flows across all primary functionalities.
- Validate critical data inputs and outputs are consistent with user expectations.
- Verify UI responsiveness and behavior on supported devices and browsers.
- Conduct regression testing to maintain code stability with new updates.

## Test Assumptions

- OpenDP will correctly perform the required calculations.
- Users are able to successfully install the software.

## Data Approach

- Any CSVs used for testing will be checked in to the fixtures directory.
- Outputs will be checked for structure, but we will not expect any particular values.

## Automation Strategy

- Doc tests: For simple functions, use doctests so the developer can just work with one file.
- For more complex functions and operations, use pytest unit tests.
- Run linting and type checking tools as part of tests.
- Use Playwright for end-to-end tests.
- Use test matrix on Github CI if we think there will be any senstivity to versions or browsers.

## Test Case Prioritization

- There's just one test suite, which is run on every PR, so there's nothing that needs to be ordered.

# Execution Strategy

## Entry Criteria

N/A: Tests are run automatically on every PR.

## Exit criteria

N/A: Tests are run automatically on every PR.

## Validation and Defect Management

N/A: PRs should not be merged with failing tests.

# Github Workflow

## Issue Submission and Prioritization

[See README](https://github.com/opendp/dp-creator-ii/#conventions).

## Pull Request Review and Testing

- Reviewers should read and understand code.
- Reviewers are not expected to checkout or manually test code.

## Continuous Integration and Deployment

Github CI will run tests on each PR. We require tests to pass before merge.

We do not require branches to be up to date with main: There is a small chance that one PR may break because of changes in a separate before, but that can be addressed after the fact.

# Environment Requirements

## Dataverse-Internal Environment

N/A

## AWS-Based Environments

N/A

# Significantly Impacted Division/College/Department

N/A

# Dependencies

N/A
