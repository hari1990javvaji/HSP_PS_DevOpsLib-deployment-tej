#Guidelines

##Introduction
This is a test suite project that covers all features and test cases related to the platform service . 

The core framework used to build the feature and test cases are Karate and Cucumber. 
Karate framework is an efficient REST API testing framework that is built on top of Cucumber.
This follows all conventions of behavior driven development (BDD) and it can act as a
live document for IAM platform.  

The suite package structure shall be maintained as follows:
* `reusable` 
    
    This package will manage all reusable scripts that cuts across at service level.This 
    package can cover all direct and indirect APIs available in platform. Direct API
    file name will start with one `_` and indirect API file name will start with two `__`.   

* `json`
    
    This package will have API request body template of all APIs provided by the platform. 
    
##Naming Conventions
###Java File
Java files can be created under any package. Java file name and class name MUST follow
java coding guidelines. 
- The file name and class name **MUST** be camelcase starting with capital letter. 
    Examples: `FIAMSuite.java, RoleRunner.java`
- **DO NOT** end the file name with `Test`. Only one filename is allowed to end the filename 
  with `Test` (FIAMSuiteParallelTest.java). This is because Junit will pick every file 
  ending with `Test` and run it independently when `mvn clean install` is executed.
  
###Feature file
Feature files can be created under `suite` package or its child packages only. 
- The file name **MUST** follow snake case.
    Examples: `_create_identity.feature`
- All functional user story feature files **MUST** start with a user story number.
    Examples: `401401_device_create.feature`
- The test setup and cleanup files for a particular user story will follow below pattern.
    
    Setup file name: `1234_test_setup.feature`    
    Cleanup file name: `1234_test_cleanup.feature`
    
  **NOTE:** Make sure the setup, cleanup and reusable feature scripts are marked as `@ignore`
  in order NOT to run during test suite execution.  
    
##Tags
Tagging is a way to filter out the test cases and it greatly helps selected test cases.
Tags can be defined at Feature level or Scenario level. Following are the defined tags
that can be used for IAM test cases:

| Tag Name      | Description                                   | Usage Level           |
| :---:         | :---:                                         | :---:                 | 
| `@ignore`     | To ignore a test case or feature              | `Feature` `Scenario`  |
| `@US_<nnn>`   | User story ID of a function from TFS          | `Feature`             |
| `@TC_<nnn>`   | Test case ID  of a test case from MTM         | `Scenario`            |
| `@smoke`      | Smoke test eligible scenario                  | `Scenario`            |
| `@sat`        | System level test case                        | `Feature` `Scenario`  |
