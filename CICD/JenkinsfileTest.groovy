package tests.job
import spock.lang.Unroll
import testSupport.PipelineSpockTestBase

/**
 * A spock test to test the Jenkinsfile that runs the gradle to run these Spock tests
 *gradle clean, gradle build, gradle tasks --all, gradle test
 */
class JenkinsfileTest extends PipelineSpockTestBase {
	
	def pipeline_file = 'Jenkinsfile'
	
	@Unroll
	def "validate when expression for build deploy smoketest fulltest performance and security test conditions"() {
		
		given:
		helper.registerAllowedMethod('validateDeclarativePipeline', [String.class], { false } )
		//addEnvVar('BUILD_TYPE', 'DAY')
		binding.setVariable('BUILD_TYPE', 'NIGHTLY')
		
		and:
		addParam('BUILD', P_BUILD)
		addParam('DEPLOY', P_DEPLOY)
		addParam('SMOKETEST', P_SMOKETEST)
		addParam('FULLTEST', P_FULLTEST)
		addParam('PERFORMTEST', P_PERFORMANCE_TEST)
		addParam('SECURITYTEST', P_SECURITY_TEST)

		when:	
		runScript(pipeline_file)
		
		then:	
		printCallStack()
		assertJobStatusSuccess()		
		

		where:
		P_BUILD	| P_DEPLOY	| P_SMOKETEST	| P_FULLTEST	| P_PERFORMANCE_TEST	| P_SECURITY_TEST
		true	| true		| true			| true			| true					| true		
		false   | false		| false			| false			| false					| false
		true    | false    	| false			| false			| false					| false
		false   | true     	| false			| false			| false					| false
		false   | false    	| true			| false			| false					| false
		false   | false    	| false			| true			| false					| false
		false   | false    	| false			| false			| true 					| false
		false   | false    	| false			| false			| false 				| true
	}
	
	@Unroll
	def "Jenkinsfile cover all build results for post sections - #RESULT"() {

		given:
		helper.registerAllowedMethod('validateDeclarativePipeline', [String.class], { true } )
		binding.setVariable('BUILD_TYPE', 'NIGHTLY')
		
		and:
		binding.getVariable('currentBuild').result = RESULT
		
		when:
		runScript(pipeline_file)
		
		then:
		def callEmailTest = ""
		def flag = false
		helper.callStack.findAll { call ->
			if (call.toString().contains(EMAIL_TEXT)) {
				callEmailTest = call.toString().contains(EMAIL_TEXT)
				flag = true
			}
		}
		
		if(flag == true){
			println "\nExpected Value is verified. Value is : "+EMAIL_TEXT +"\n"
		}else{
			println "\nDid not verify expected Value. Value is : "+EMAIL_TEXT +"\n"
		}
		
		assert callEmailTest == true				
		printCallStack()
		
		where:
		RESULT      | EMAIL_TEXT
		'SUCCESS'   | "CICD_BUILD_NUM_123' Succeeded"
		'FAILURE'   | "CICD_BUILD_NUM_123' Failed"
	}


	def "Check Jenkinsfile is executing the method exist in Options tag or not"() {
								
		when:
		binding.setVariable('BUILD_TYPE', 'NIGHTLY')
		runScript(pipeline_file)
		
		then:
				
		def callTest = ""
		def flag = false
		helper.callStack.findAll { call ->
			if (call.toString().contains(P_OPTIONS)) {
				callTest = call.toString().contains(P_OPTIONS)
				flag = true
			}
		}	
		
		if(flag == true){
			println "\nExpected Value is verified. Value is : "+P_OPTIONS +"\n"
		}else{
			println "\nDid not verify expected Value. Value is : "+P_OPTIONS +"\n"
		}
		
		assert callTest == P_ASSERT
		printCallStack()
		assertJobStatusSuccess()
		
		where:  
		P_OPTIONS						| P_ASSERT
		"disableConcurrentBuilds()" 	| true
		"timestamps()"					| true
	}	

	
	@Unroll
	def "validate methods exist in build deploy full test performance and security test stages"() {
		
		given:
		helper.registerAllowedMethod('validateDeclarativePipeline', [String.class], { false } )
		binding.setVariable('BUILD_TYPE', 'NIGHTLY')
		
		and:
		addParam('BUILD', P_BUILD)
		addParam('DEPLOY', P_DEPLOY)
		addParam('SMOKETEST', P_SMOKETEST)
		addParam('FULLTEST', P_FULLTEST)
		addParam('PERFORMTEST', P_PERFORMANCE_TEST)
		addParam('SECURITYTEST', P_SECURITY_TEST)
		addParam('COMMAND', BUILD_COMMAND)			
		
		when:
		runScript(pipeline_file)
				
		then:	
		def callTest = ""	
		def flag = false	
		helper.callStack.findAll { call ->
			if (call.toString().contains(BUILD_COMMAND)) {
				callTest = call.toString().contains(BUILD_COMMAND)
				flag = true
			}
		}	
		
		if(flag == true){
			println "\nExpected Value is verified. Value is : "+BUILD_COMMAND +"\n"
		}else{
			println "\nDid not verify expected Value. Value is : "+BUILD_COMMAND +"\n"
		}
				
		assert callTest == true
		printCallStack()
		assertJobStatusSuccess()
												
		where:
		P_BUILD	| P_DEPLOY	| P_SMOKETEST	| P_FULLTEST	| P_PERFORMANCE_TEST	| P_SECURITY_TEST	| BUILD_COMMAND
		true	| false		| false			| false			| false					| false				| "chmod -R 755 C:/TEST_WORKSPACE_CICD"
		true	| false		| false			| false			| false					| false				| "C:/TEST_WORKSPACE_CICD/CICD/build.sh"
		false	| false		| false			| true			| false					| false				| "chmod -R 755 C:/TEST_WORKSPACE_CICD"
		false	| false		| false			| true			| false					| false				| "C:/TEST_WORKSPACE_CICD/ROBOCI/CICD/Scripts/Ec2_Trigger.sh FULLTEST"
		false	| false		| false			| false			| true					| false				| "chmod -R 755 C:/TEST_WORKSPACE_CICD"
		false	| false		| false			| false			| true					| false				| "C:/TEST_WORKSPACE_CICD/ROBOCI/CICD/Scripts/Ec2_Trigger.sh PERFORMANCETEST"
		false	| false		| false			| false			| false					| true				| "chmod -R 755 C:/TEST_WORKSPACE_CICD"
		false	| false		| false			| false			| false					| true				| "C:/TEST_WORKSPACE_CICD/ROBOCI/CICD/Scripts/Ec2_Trigger.sh SECURITYTEST"			
	}
}		