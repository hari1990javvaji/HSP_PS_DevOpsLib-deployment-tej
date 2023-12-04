ReadMe file for Usage Service Smoke Test
==============================================
1. Prerequisite: 

	Python:
		a. Install Python 2.7.11 version with respect to OS [i.e. Windows/Linux]
		b. Install all python module mentioned in the requirements.txt file.
		c. Copy Python test scripts parent folder to the execution box(in folder name smoketest)
		

2. Update config.properties file which is available under parent folder.
        Example:
        
        [APP]
                
        [STATIC]
        
        [CREDENTIALS]
        
        [RUNTIME]
                
        Add or update key value pairs under relevant sections. No need to specify anything in RUNTIME section.    



2. 	Executon of smoke scripts
	a. Go to the source folder location of python test scripts
	b. Launch terminal/command prompt
	c. Run the following test execution command:

			driver.py smoke.csv <logLevel> <Release_Version>
			
						
3. Execution Logs 
	a. Execution Summary Log file under <DIR>/reports/smoke
	

4. Folder structure of smoke suite:
	1. ext: Contains driver for UI execution(This is not required for this service)
	
	2. Lib: It has the following sub folders:-
	
			core: Contains files and methods for converting csv to json format.
			
			java: Contains files and methods for customized java library, which is needed to be called for a service.(Not required for this service)
			
			mtm: 
			
			python: Contains files and methods for customized python library which is requires to be called for your a service. In Usage we are calling this python library to fetch cloud watch logs and download/deleteting config file from vault.
			
			rest : Contains files and methods to execute and validate rest api's.
			
			vault: Contains files and methods to download and delete files from vault.
			
	3. reports: Contains test case wise execution reports.
			
	4. test_data: Contains the data required to execute smoke test cases.
								
