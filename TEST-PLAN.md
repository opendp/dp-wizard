
**Purpose of the Document**
Use the Test Plan document to describe the testing approach and overall framework that will drive the testing of the project.

***Template Instructions***
*Note that the information in italics is guidelines for documenting testing efforts and activities.  To adopt this template, delete all italicized instructions and modify as appropriate*

# Introduction

## Purpose

*Provide a summary of the test strategy, test approach, execution strategy and test management.*

Automate the end-to-end functionality of the DP-Creator-II application to ensure it meets user requirements and maintains reliability, especially in the context of privacy-preserving data processing.

## Project Overview

*A summary of the project, product, solution being tested.*

# Scope

## In-Scope

*Describes what is being tested, such as all the functions/features of a specific project/product/solution.*

\- User authentication (login, logout, user session management)
\- Data processing workflows (data upload, processing configurations)
\- UI elements related to data privacy settings
 \- Data export functionalities

## Out-of-Scope

*Identify all features and combinations of features which will not be tested and the reasons.*

     \- Performance testing
     \- Non-functional UI aspects not directly related to functionality
     \- External API integrations that are mocked in this environment

# Testing Strategy

## Test Objectives

*Describe the objectives.  Define tasks and responsibilities.*

   \- Ensure reliable execution of user flows across all primary functionalities.
   \- Validate critical data inputs and outputs are consistent with user expectations.
   \- Verify UI responsiveness and behavior on supported devices.
   \- Conduct regression testing to maintain code stability with new updates.

## Test Assumptions

*List the key assumptions of the project and the test plan.*

## Data Approach

 *Describe the approach on the test data maintained in QA environments for functional and user acceptance testing.*

     \- Use static datasets for predictable validation.
     \- Implement data mocks for complex scenarios.
     \- Develop data validation utilities to check outputs.

## Automation Strategy

     \- Smoke Testing: Quick, high-level test cases to ensure critical paths work.
     \- Regression Testing: Re-running existing tests to validate the latest changes.
     \- E2E Testing: Testing all primary workflows from start to finish.

## Test Case Prioritization

     \- High priority for critical features like data processing workflows and privacy configurations.
     \- Moderate priority for UI/UX elements like buttons, forms, and navigation.
     \- Lower priority for non-critical paths or backend validations covered in unit tests.

# Execution Strategy

## Entry Criteria

* *The entry criteria refer to the desirable conditions in order to start test execution*
* *Entry criteria are flexible benchmarks. If they are not met, the test team will assess the risk, identify mitigation actions and provide a recommendation.*

| Entry Criteria | Test Team | Technical Team | Notes |
| ----- | ----- | ----- | ----- |
| *Test environment(s) is available*  |    ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |  |
| *Test data is available* | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |  |
| *Code has been merged successfully* | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |  |
| *Development has completed unit testing* |  | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |
| *Test scripts are completed, reviewed and approved by the Project Team* | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |

## Exit criteria

* *The exit criteria are the desirable conditions that need to be met in order proceed with the implementation.*
* *Exit criteria are flexible benchmarks. If they are not met, the test team will assess the risk, identify mitigation actions and provide a recommendation.*

| Exit Criteria | Test Team | Technical Team | Notes |
| ----- | ----- | ----- | ----- |
| *100% Test Scripts executed* |    ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |  |
| *90% pass rate of Test Scripts* | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |  |
| *No open Critical and High severity defects* | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |
| *All remaining defects are either cancelled or documented as Change Requests for a future release* |  | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |
| *All expected and actual results are captured and documented with the test script* | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |  |
| *All test metrics collected based on reports from daily and Weekly Status reports* | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |  |
| *All defects logged in  Defect Tracker/Spreadsheet* | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |  |
| *Test environment cleanup completed and a new back up of the environment* |  | ![C:\\Users\\arxp\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\7F9Z3IW4\\MC900441310\[1\].png][image1] |  |

## Validation and Defect Management

* *Specify how test cases/test scenarios should be validated*
* *Specify how defect should be managed*
  * *It is expected that the testers execute all the scripts in each of the cycles described above.*
  * *The defects will be tracked through Defect Tracker or Spreadsheet.*
  * *It is the responsibility of the tester to open the defects, retest and close the defect.*

Defects found during the Testing should be categorized as below:

| Severity | Impact |
| ----- | ----- |
| *1 (Critical)* | *Functionality is blocked and no testing can proceed Application/program/feature is unusable in the current state* |
| *2 (High)* | *Functionality is not usable and there is no workaround but testing can proceed* |
| *3 (Medium)* | *Functionality issues but there is workaround for achieving the desired functionality* |
| *4 (Low)* | *Unclear error message or cosmetic error which has minimum impact on product use.* |

# Github Workflow

## Issue Submission and Prioritization**  {#issue-submission-and-prioritization}

Bugs and feature requests are tracked in GitHub, and issues are prioritized based on their impact and urgency. Issues should be categorized into sprint goals for more efficient tracking.

\- Process:
  \- Review the issue backlog in GitHub.
  \- Assign priority based on criticality, risk, and user impact.
  \- Assign issues to the current sprint or defer to future sprints if necessary.

## Pull Request Review and Testing

QA starts with a smoke test on the PR branch. Additional functional and regression testing is done based on the feature or fix included in the PR.
\- PR Testing:
  \- Ensure the feature or fix fully addresses the reported issue.
  \- Use the documentation to create test cases and validate functionality.
  \- Perform boundary testing, testing with incorrect data, and edge cases.
  \- Review server logs for any errors during testing.
  \- Test both the default and alternate configurations for features requiring setup.

## Continuous Integration and Deployment

Continuous integration ensures that tests run automatically with each code change. Dataverse’s Jenkins server should be used to run automated tests, while GitHub Actions provide additional automation for builds and deployments.

\- CI Steps:
  \- Merge PRs only when all tests pass.
  \- Use the Jenkins build process to deploy to a staging environment (\`dataverse-internal.iq.harvard.edu\`).
  \- Validate each PR’s test results through Jenkins' "Test Result" page.
  \- If tests fail, report the issue to the developer immediately for resolution

# Environment Requirements

## Dataverse-Internal Environment

A staging environment (\`dataverse-internal.iq.harvard.edu\`) is used to deploy and test PRs. This environment replicates production but should be limited to QA purposes. AWS instances may also be utilized for additional testing environments.

\- \*\*Setup\*\*:
  \- Deploy the PR build using Jenkins.
  \- Validate deployment success by checking the homepage for the correct build version.
  \- Run smoke tests immediately after deployment.

## AWS-Based Environments

For complex testing scenarios (e.g., multiple concurrent testers or heavy load testing), spinning up EC2 instances with sample data can be useful. Persistent AWS instances may be configured for this purpose.

# Significantly Impacted Division/College/Department

| Business Area | Business Manager | Tester(s) |
| ----- | ----- | ----- |
|  |  |  |
|  |  |  |
|  |  |  |

# Dependencies

*Identify any dependencies on testing, such as test-item availability, testing-resource availability, and deadlines.*

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAE4klEQVR4Xu2We0xTdxTHYeLQkSwtThBfPIKbKI8gOlEY+GAuZC74WHQDZ5jT6KaiMARxRZiy8RIUEFGkgLzkTYH23t7b28eKgC1QC+VRUJyJ25IlS/bXki3L/O7XMhdykzmV8h+f5Jc27Tnne875nXtaO7s55rAxuYy/021DBFpN26yneSgcVYa1SKIWLufb2pz4nuUL7zxKhnw8Gk2DW9A4GIKae/4oueuKfK0T4uWvO/N9bAfs7LsfnUPnaCQRD4PEdACVA6txXeeGXM0CfE3PQ3KjPfhuNoMy7yEt34oG42aIewNRqPJBsWoDMhSvWoVPiu1xpNAen1x65S++74xpHjrc0mLagnrDJlTrg4j4auTSq/BtuxduqqKQ1eXzZ173ehT2hKBYt+mJSO9yjR/jpcnvWbdOMvwu6gY24pYuEGV3fJEj88bFVg+k1C2CciIdreT7xqEw3B7ciDzTijp+jBmhmDhGKg9GRW8ASrVrcFX5Fs7VOyOpWgjGnIK24R1oGApBnXE9bhl8n28GSruj3qvS7/rjhjYQllOi9UWh2hMnKTvH6XaysWO/V+vXQdzthyvsSmRIhEiuEyCjyR8y8340mcJJ1cHkMfTDZeOK3um+z+TeD+LfDD9mk/uMRGmXL4o0K5HDCZAqmYe4hvmfWWy+6fV0rdIFoaxrDfKYN3CxjYjXCPBlpQBS8z7S8lBS9QYi7o+iAfdJvsZ/kqa2czD+lAf941R0PzoF1eRZZDJOON/hgNOV9jh6lUxzuYO00Rj9uIBbjBxKaK08qUqAhHIBanQHUT+4GbXGINwaWIuyPu/na/tTNJPnf2UmYkGRZaJ8EANmYjdkY5Go1L+P2Fx7HMyeOrmUMy5Yqq4VIJFUnSh2Q/vYh6Tlb/8rXHJ3BSwF8TWeCffgqLWFkpEoNAxuR+29UFQPBKOyLwhHihdYxWPz5iGlXoAkS8srBDh9U4Dm4Y/IIavXtJ1sv2CU6ryQNPgS61c5GUcm9wNyhxGoMWxGBRHO17ggW+GMLHopScIRFzp8cOaflp+6QV5vupKh24f20V3kkdtJfHcgR78qkR/7ucnV+YW1Du9FgXYJLqkWIYsh9ywjQ9giQFrTUqQ1eCC+jFQvFlpPneEA6dp+ksBekkAUyvvDfubHfCmy7r55OpNejHSJAF81kpZXE1FStUU8oUxIWi9EgXwb+fH5FNKxGLSPRKNt6OMXG7r/Q9TtHpjW7GZ9xBLEUy2Pt4jfECK+1BnKh/EkgcOQjR5Ch+kQmZWd3/NjzJiU3mX+ZypdcPK6ZeCEOHV9KoGMpgAo7p8AM34cspEv0Dl0nEy9+wK+v834vEiIuGtTCSSULoLmoYjs+mQoxsh/ANNZZHB+kXwfmyKivTqeVi+q8oTmfhpU5jRwI+mQDCQ+4dvPCqJ2D1MCuftr2h34bjwT6rFMKIezUdEVI+HbzhrJ5W5g7qdCa74MzehlqE1XIOr0CODbzRqW9dplLgZtzECLPvmX2z0n+vg2NoWiKEeapt1YlvVjKTZYRbHhCpqOsBxOLt/KddLvqBhVEMMwvmq53FutVi+RSqXC/o6O1/r7++fz470wHMct4yhmt5JWiJRyNk8pV1xV0mwxR7EF5H02+TxdRTNxHM3EsjS7R0EpQlkZ66eUSt0tifDjzTHHdP4GlgIMfS6zn9wAAAAASUVORK5CYII=>
