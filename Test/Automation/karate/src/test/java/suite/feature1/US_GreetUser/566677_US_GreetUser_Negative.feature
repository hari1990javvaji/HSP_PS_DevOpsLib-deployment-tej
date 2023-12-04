@parallel=false 
@UTC_718645 @TC_718645 @USUID_XXXX

Feature: get customized greeting 

	Background:
		* url greet_host
	
	@S_1	
	Scenario: incorrect path
		Given path '/hello1'
		When method get
		Then status 404
		