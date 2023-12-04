Following are the instructions for uploading test automation script results to mtm test case (manual test cases).

1. Ensure all automation scripts (feature files) are executed through Karate Framework.
2. Create Test Plan in MTM if it is not created
3. Create a Suite and pull test cases which are automated
4. Update mtm test plan id and suite ids in mtmconfig.json file. If you have more suites, then provide suites ids separated  by camma (,)
5. Following command to run to upload automation script results to MTM.

COMMAND:
java -jar CucumberReportUploadToTFS.jar 3101XXXX <pwd> <TYPE> <ws>/target/surefire-reports <ws>/Results <ws>/project.properties

OUTPUT: 
Following files will be created under Results folder

TestReport.json
Regression_TestCase_Report.json
Non_Regression_TestCase_Report.json

Example:
java -jar CucumberReportUploadToTFS.jar 3101XXXX <pwd> TEST_FULLTEST C:\HSDP\2020\surefire-reports C:\HSDP\2020\Results C:\HSDP\2020\CI\project.properties


For Generating HTML Reports and 

COMMAND:
python summary_report.py 3101XXXX <PWD> <ws>/CI/project.properties <ws>/Results/TestReport.json <ws>/Results/Regression_TestCase_Report.json <ws>/Results/Non_Regression_TestCase_Report.json <ws>/Results

OUTPUT: 
Following files will be created under Results folder

Test_Summary.json
Regression_TestCase_Report.html
Non_Regression_TestCase_Report.html


Example:
python summary_report.py 3101XXXX <pwd> <ws>/CI/project.properties C:\HSDP\2020\Results\TestReport.json C:\HSDP\2020\Results\Regression_TestCase_Report.json C:\HSDP\2020\Results\Non_Regression_TestCase_Report.json C:\HSDP\2020\Results



Note:
project.properties file will be checked in the respective service repo under TEST/CI folder.
Content of Properties file for example:

[GLOBAL]
project_name=System
project_release=Release 1
test_plan=53XXX

tfshostapi=https://tfsapac04.ta.philips.com/tfs/DHPCollection
customtfshostapi=https://testautomation-pic.ta.philips.com/TestRunUpdateService.svc
attachsteplogs=false
attachtestcaselog=true
tfs_query_path=Shared Queries/Team Testing/CICD_Queries_GIT
build_type=TEST
total_tc=Total_TestCases
total_attc=Automated_TestCases
total_reg_tc=Regression_TestCases
total_reg_attc=Regression_Automated_TestCases
total_non_reg_tc=Non_Regression_TestCases
total_non_reg_attc=Non_Regression_Automated_TestCases
total_reg_at_perf_tc=Regression_Automated_Performance_TestCases
total_reg_at_sec_tc=Regression_Automated_Security_TestCases
api_retry=3

[TEST_SMOKETEST]
reg_suite_id=570724,682582
non_reg_suite_id=648656

[TEST_FULLTEST]
reg_suite_id=570724
non_reg_suite_id=648656

