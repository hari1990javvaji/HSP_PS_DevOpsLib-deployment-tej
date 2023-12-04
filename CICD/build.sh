#!/bin/bash -e

echo "######## PROXY ENVIRONMENT SETUP ########"
export http_proxy=${http_proxy}
export https_proxy=${http_proxy}

BUILD_SHARE="/home/jenkins/TFS_CI_SHARE"

gitSecretGate() {
    SECRET_SCAN_PATH="${WORKSPACE}/ROBOCI/CICD/Scripts/git_secret_scan"
    chmod 755 -R ${SECRET_SCAN_PATH}/*
    PATH="${PATH}:${GIT_SECRET_PATH}"
    cd ${WORKSPACE}
    cat ${WORKSPACE}/CICD/git-secrets-allow-pattern_${PSNAME}.txt >> ${SECRET_SCAN_PATH}/patterns-allow.txt
    cat ${WORKSPACE}/CICD/git-secrets-allow-pattern_${PSNAME}.txt >> ${SECRET_SCAN_PATH}/patterns-allow-test.txt
    ${SECRET_SCAN_PATH}/gitsecret-gate.sh ${WORKSPACE} ${PSNAME} ${SECRET_SCAN_PATH}/patterns-prohibit.txt ${SECRET_SCAN_PATH}/patterns-allow.txt ${WORKSPACE} source	
    ${SECRET_SCAN_PATH}/gitsecret-gate.sh ${WORKSPACE} ${PSNAME} ${SECRET_SCAN_PATH}/patterns-prohibit-test.txt ${SECRET_SCAN_PATH}/patterns-allow-test.txt ${WORKSPACE} test	
}

sonarqubeanalysisTestcode() {
    #Script to be taken from CICD/TESTSCAN.pipeline
    cd ${WORKSPACE}
	${SONAR_SCANNER_PATH}/sonar-scanner -Dsonar.projectKey=${PSNAME}:${SONAR_TEST_BRANCH} \
	-Dsonar.projectName=${PSNAME}_${SONAR_TEST_BRANCH} \
	-Dsonar.projectVersion=1.0 \
	-Dsonar.sources=Test/. \
	-Dsonar.exclusions=Test/Automation/karate/** \
	-Dsonar.host.url=${HSDP_SONARQUBE_URL_NEW} \
	-Dsonar.ws.timeout=300
}
sqDynamicGatingTestcode(){
   echo "Running SonarQube Dynamic Gating"
   cd ${WORKSPACE}/ROBOCI/CICD/Scripts
   ./SonarQubeDynamicGatingTestcode.sh ${PSNAME}
   cd ${WORKSPACE} 
}

sqDynamicGating(){
    echo "Running SonarQube Dynamic Gating"
    cd ${WORKSPACE}/ROBOCI/CICD/Scripts
    ./SonarQubeDynamicGatingSourcecode.sh ${PSNAME}
    cd ${WORKSPACE}
}

warningSuppressionCheck(){
    echo "Running Warning Suppression Gating"
    cd ${WORKSPACE}/ROBOCI/CICD/Scripts
    ./SuppressWarnings_gate.sh
    cd ${WORKSPACE}
}

sqReleasePrereq(){
    echo "Running SonarQube Release PreReq"
    cd ${WORKSPACE}/ROBOCI/CICD/Scripts
    ./SonarQubeReleasePrerequisites.sh
    cd ${WORKSPACE}
}

sonarqubeanalysis() {
 echo "********** SonarQube scan for Testcode has started ...**********"
if [[ $JOB_NAME =~ (DAY|NIGHTLY) ]]; then
	SONAR_TEST_BRANCH="TEST_NIGHTLY"
	sonarqubeanalysisTestcode
elif [[ $JOB_NAME =~ (RELEASE|UPDATE) ]]; then
	SONAR_TEST_BRANCH="TEST_NIGHTLY"
	sonarqubeanalysisTestcode
elif [ $BUILD_TYPE = GATED -a $JOB_NAME != RELEASE -a $JOB_NAME != UPDATE ]; then
	SONAR_TEST_BRANCH="TEST_GATED"
	sonarqubeanalysisTestcode
	sqDynamicGatingTestcode
else
	echo " ${BUILD_TYPE} is Invalid "
fi
echo "********** SonarQube scan for Testcode is Completed.**********"

cd ${WORKSPACE}   
    if [[ $JOB_NAME =~ (DAY|NIGHTLY) ]]; then
        SONAR_BRANCH="DEV_NIGHTLY"
    elif [[ $JOB_NAME =~ (RELEASE) ]]; then
        sqReleasePrereq
        SONAR_BRANCH="DEV_RELEASE"
    elif [[ $JOB_NAME =~ (UPDATE) ]]; then
        sqReleasePrereq
        SONAR_BRANCH="DEV_UPDATE"
    elif [ $BUILD_TYPE = GATED -a $JOB_NAME != RELEASE -a $JOB_NAME != UPDATE ]; then
        SONAR_BRANCH="GATED"
    else
        echo "${BUILD_TYPE} is Invalid"
    fi

    /home/jenkins/sonar-scanner-3.2.0/bin/sonar-scanner -Dsonar.projectKey=${PSNAME}:${SONAR_BRANCH} \
        -Dsonar.projectName=${PSNAME}_${SONAR_BRANCH} \
        -Dsonar.projectVersion=1.0 \
        -Dsonar.sources=Source/Python/. \
        -Dsonar.python.coverage.reportPaths=Source/Python/coverage.xml \
        -Dsonar.python.coveragePlugin=cobertura \
        -Dsonar.exclusions=Source/Python/cf_framework/** \
        -Dsonar.host.url=${HSDP_SONARQUBE_URL_NEW} \
        -Dsonar.cpd.js.minimumTokens=50 \
        -Dsonar.cpd.ts.minimumTokens=50 \
        -Dsonar.ws.timeout=600
}

build(){
      ##### TO CHECK DEVELOPMENT TYPE AND BUILD EXECUTION #####
    if [ "${DEV_TYPE,,}" == "java" ]; then
            echo "##### JAVA BUILD EXECUTION #####"
        if [[ $BUILD_TYPE =~ (GATED) ]]; then
            gitSecretGate
            warningSuppressionCheck
            sqDynamicGating
            cd Source/SampleApp
            mvn -B clean install
        elif [[ $BUILD_TYPE =~ (DAY|NIGHTLY|RELEASE|UPDATE) ]]; then
            cd Source/SampleApp
            mvn -B clean install
        else
            echo "$BUILD_TYPE is INVALID"
        fi

        export BINARY_PATH=${BUILD_SHARE}/${BUILD_NAME}/${BUILD_NUM}/binary
        mkdir -p ${BINARY_PATH}
        echo "##### COPY BINARIES TO THE BINARY SERVER #####"
        cd ${WORKSPACE}/Source/SampleApp
        find . -name "*.jar" -exec cp {} ${BINARY_PATH}/  \;
    elif [ "${DEV_TYPE,,}" == "python" ]; then
            echo "##### ${DEV_TYPE} Unit test execution #####"
            cd ${WORKSPACE}/Source/Python/cf
        echo "Executing CF unit tests python2"
        python -m tests.test_create_manifests
        python -m tests.test_create_services -u ${CF_USN} -p ${CF_PWD}
        python -m tests.test_cf -u ${CF_USN} -p ${CF_PWD}
        
        coverage3 run --parallel-mode -m tests.test_create_manifests
        coverage3 run --parallel-mode -m tests.test_create_services -u ${CF_USN} -p ${CF_PWD}
        coverage3 run --parallel-mode -m tests.test_cf -u ${CF_USN} -p ${CF_PWD}

        cd ${WORKSPACE}/Source/Python/vault
        echo "Executing Vault unit tests python2"
        python -m tests.test_vaultoperations -s ${DEVOPSLIB_SECRET_ID}
        python -m tests.test_vaultservicecreds -u ${CF_USN} -p ${CF_PWD}

        coverage3 run --parallel-mode -m tests.test_vaultoperations -s ${DEVOPSLIB_SECRET_ID}
        coverage3 run --parallel-mode -m tests.test_vaultservicecreds -u ${CF_USN} -p ${CF_PWD}

        cd ${WORKSPACE}/Source/Python
        coverage3 combine cf/ vault/
        coverage3 xml
        echo "Coverage xml report generated"

        if [[ $BUILD_TYPE =~ ^(DAY|NIGHTLY|GATED) ]]; then
            sonarqubeanalysis
        elif [[ $JOB_NAME =~ "_RELEASE" ]]; then
            sonarqubeanalysis
        elif [[ $JOB_NAME =~ "_UPDATE" ]]; then
            sonarqubeanalysis
        else
            echo "Not a CI or GATED build - skipping SonareQube Scan"
        fi
      else
            echo "##### ${DEV_TYPE} IS NOT A VALID DEVELOPMENT FRAMEWORK #####"
    fi
}

buildWithoutSonarQube(){
    cd ${WORKSPACE}/Source/SampleApp
    mvn clean install
}

if [[ $BUILD_TYPE =~ ^(GATED|DAY|NIGHTLY|RELEASE|UPDATE) ]]; then
    build
elif [[ $BUILD_TYPE =~ ^(BLACKDUCK|FORTIFY) ]]; then
    echo " BUILD_TYPE IS: $BUILD_TYPE Running Build without SonarQube"
      buildWithoutSonarQube
else
      echo "Not a CI or GATED build - Skipping SonareQube Scan"
fi