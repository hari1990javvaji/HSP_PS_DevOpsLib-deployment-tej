Following are the instructions for uploading test automation script results to mtm test case (manual test cases).

1. Ensure all automation scripts (feature files) are executed through Karate Framework.
2. Create Test Plan in MTM if it is not created
3. Create a Suite and pull test cases which are automated
4. Update mtm test plan id and suite ids in mtmconfig.json file. If you have more suites, then provide suites ids separated  by camma (,)
5. Following command to run to upload automation script results to MTM.

java -jar KarateMTM.jar <code1id> <password> <ws>/target/surefire-reports <ws or any location>/TFSReport.json

Example:
java -jar KarateMTM.jar 3101XXXXX XXXXXXXXX C:/HSDP/karate_framework/target/surefire-reports C:/HSDP/karate_framework/TFSReport.json