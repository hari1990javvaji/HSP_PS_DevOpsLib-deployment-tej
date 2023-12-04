@parallel=false 
@UTC_718643 @TC_718643 @USUID_XXXXX

Feature: get Random number with name

	Background:
		* url randomNum_host
	
	@S_1	
	Scenario: get random number without name
		Given path '/generate'
		When method get
		Then status 200
		And match response == { number: '#number', name: 'Null' }
		
	@S_2
	Scenario: get random number with name 
  		Given path '/generate'
        And param name = 'User'
    	When method get
    	Then status 200
    	And match response == { number: '#number', name: 'User' }
  
  