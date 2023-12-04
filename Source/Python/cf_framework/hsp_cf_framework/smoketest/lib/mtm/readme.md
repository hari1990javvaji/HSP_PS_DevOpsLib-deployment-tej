Please follow below instructions before running the above python tool.

1.	Install Python 2.7.X (latest version)  (https://www.python.org/downloads/release/python-2715/)
2.	Install python pacakges:
	python -m pip install --upgrade pip
	pip install jinja2
	pip install logging
	pip install configobj
	pip install pathlib
	pip install requests
	pip install requests_ntlm
	pip install datetime

3.	Unzip the attached tool.
4.  Before running below command, make sure NodeJS framework is executed all functional automation scripts and generated a nodejs json report/log.
5.	Run the following command….
	<Location of extration>\python test_driver.py <code1_id> <code1_pwd> <Project_Name> <Release_Number> <mtm_plan_id> <nodejs log json file path> <log_location> TEST

Example:
	python test_driver.py 310171211 XXXXXXX ConnectMDM "Release 1.2" 306400 "C:\HSDP\Testing\TFS_REST\MDM\logs\sample_nodjs_execution_report.json" "C:\HSDP\Testing\TFS_REST\MDM\logs" TEST
