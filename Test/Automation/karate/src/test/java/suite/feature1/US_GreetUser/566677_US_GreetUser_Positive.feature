@parallel=false 
@UTC_718635 @TC_718635 @USUID_XXXXX

Feature: get customized greeting 

	Background:
		* url greet_host
	
	@S_1	
	Scenario: get default greeting (without parameter)
		Given path '/hello'
		When method get
		Then status 200
		And match response == { id: '#number', content: 'Hello, World!' }
		
	@S_2
	Scenario: get custom greeting (with parameter)

  		Given path '/hello'
      And param name = 'Anaghesh'
    	When method get
    	Then status 200
    	And match response == { id: '#number', content: 'Hello, Anaghesh!' }
   
   @S_3 	
   Scenario: get custom greeting (with numeric parameter)

  		Given path '/hello'
      And param name = '123'
    	When method get
    	Then status 200
    	And match response == { id: '#number', content: 'Hello, 123!' }
   
   @S_4 	
   Scenario: get custom greeting (with Alpha-numeric parameter)

  		Given path '/hello'
      And param name = 'User123'
    	When method get
    	Then status 200
    	And match response == { id: '#number', content: 'Hello, User123!' }
    	