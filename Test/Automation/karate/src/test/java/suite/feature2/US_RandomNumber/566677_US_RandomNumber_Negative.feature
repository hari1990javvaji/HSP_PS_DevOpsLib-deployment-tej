@parallel=false 
@UTC_718646 @TC_718646 @USUID_XXXXX

Feature: get Random number with name

	Background:
		* url randomNum_host
	
	@S_1	
	Scenario: incorrect path
		Given path '/generate1'
		When method get
		Then status 404

  