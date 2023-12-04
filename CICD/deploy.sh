#!/bin/bash -e

BUILD_SHARE="/home/jenkins/TFS_CI_SHARE"
echo -e "######## SOFTWARES VERSION ########" 

echo -e "CLOUD FOUNDARY VERSION"
cf -v
echo -e "PYTHON VERSION"
python --version

if [ "$BUILD_TYPE" != "DD" ]; then
    echo "######## PROXY ENV SETUP ########"
    export http_proxy=${PROXY_URL}
    export https_proxy=${PROXY_URL}
    export no_proxy="artifactory-ehv.ta.philips.com"
else
    echo "######## DD ENV SETUP ########"
fi

echo "HTTP Proxy Inside Docker = $http_proxy  and HTTPS Proxy Inside Docker = $https_proxy"

######## INSTALL CF, CF_FRAMEWORK AND VAULT FROM ARTIFACTORY ########
if [ -d ${WORKSPACE}/Source/SampleApp/hsp_cf_framework ]; then
    rm -rf ${WORKSPACE}/Source/SampleApp/hsp_cf_framework
fi
echo "DEPLOY_RELEASE_VERSION = $DEPLOY_RELEASE_VERSION"

if [ "$PYTHON_VERSION" == "2" ]; then
    echo "Start deploying Python2 DevOpsLib packages"
    if [[ $BUILD_TYPE =~ ^(RELEASE|UPDATE|DD)  && $DEPLOY_RELEASE_VERSION == true ]]; then
        echo "Deploy Release DevOpsLib packages"
        pip install --client-cert $HSP_ARTIFACTORY_SCT_FILE_CERTIFICATE_PEM \
                    --extra-index-url https://$ART_USER:$ART_PWD@artifactory-ehv.ta.philips.com/artifactory/api/pypi/hsp-pypi-releases-local/simple \
                    hsp_cf
        pip install --client-cert $HSP_ARTIFACTORY_SCT_FILE_CERTIFICATE_PEM \
                    --extra-index-url https://$ART_USER:$ART_PWD@artifactory-ehv.ta.philips.com/artifactory/api/pypi/hsp-pypi-releases-local/simple \
                    hsp_vault
        pip install --client-cert $HSP_ARTIFACTORY_SCT_FILE_CERTIFICATE_PEM \
                    --extra-index-url https://$ART_USER:$ART_PWD@artifactory-ehv.ta.philips.com/artifactory/api/pypi/hsp-pypi-releases-local/simple \
                    --target=${WORKSPACE}/Source/SampleApp \
                    hsp_cf_framework
    else
        echo "Deploy Snapshot DevOpsLib packages"
        pip install --client-cert $HSP_ARTIFACTORY_SCT_FILE_CERTIFICATE_PEM \
                    --extra-index-url https://$ART_USER:$ART_PWD@artifactory-ehv.ta.philips.com/artifactory/api/pypi/hsp-pypi-snapshots-local/simple \
                    --pre \
                    hsp_cf
        pip install --client-cert $HSP_ARTIFACTORY_SCT_FILE_CERTIFICATE_PEM \
                    --extra-index-url https://$ART_USER:$ART_PWD@artifactory-ehv.ta.philips.com/artifactory/api/pypi/hsp-pypi-snapshots-local/simple \
                    --pre \
                    hsp_vault
        pip install --client-cert $HSP_ARTIFACTORY_SCT_FILE_CERTIFICATE_PEM \
                    --extra-index-url https://$ART_USER:$ART_PWD@artifactory-ehv.ta.philips.com/artifactory/api/pypi/hsp-pypi-snapshots-local/simple \
                    --target=${WORKSPACE}/Source/SampleApp \
                    --pre \
                    hsp_cf_framework
    fi
    echo "End deploying Python2 DevOpsLib packages"
elif [ "$PYTHON_VERSION" == "3" ]; then
    echo "Start deploying Python3 DevOpsLib packages"
    if [[ $BUILD_TYPE =~ ^(RELEASE|UPDATE|DD) && $DEPLOY_RELEASE_VERSION == true ]]; then
        echo "Deploy Release DevOpsLib packages"
        pip3 install --client-cert $HSP_ARTIFACTORY_SCT_FILE_CERTIFICATE_PEM \
                     --extra-index-url https://$ART_USER:$ART_PWD@artifactory-ehv.ta.philips.com/artifactory/api/pypi/hsp-pypi-releases-local/simple \
                     hsp_cf
        pip3 install --client-cert $HSP_ARTIFACTORY_SCT_FILE_CERTIFICATE_PEM \
                     --extra-index-url https://$ART_USER:$ART_PWD@artifactory-ehv.ta.philips.com/artifactory/api/pypi/hsp-pypi-releases-local/simple \
                     hsp_vault
        pip3 install --client-cert $HSP_ARTIFACTORY_SCT_FILE_CERTIFICATE_PEM \
                     --extra-index-url https://$ART_USER:$ART_PWD@artifactory-ehv.ta.philips.com/artifactory/api/pypi/hsp-pypi-releases-local/simple \
                     --target=${WORKSPACE}/Source/SampleApp \
                     hsp_cf_framework
    else
        echo "Deploy Snapshot DevOpsLib packages"
        pip3 install --client-cert $HSP_ARTIFACTORY_SCT_FILE_CERTIFICATE_PEM \
                     --extra-index-url https://$ART_USER:$ART_PWD@artifactory-ehv.ta.philips.com/artifactory/api/pypi/hsp-pypi-snapshots-local/simple \
                     --pre \
                     hsp_cf
        pip3 install --client-cert $HSP_ARTIFACTORY_SCT_FILE_CERTIFICATE_PEM \
                     --extra-index-url https://$ART_USER:$ART_PWD@artifactory-ehv.ta.philips.com/artifactory/api/pypi/hsp-pypi-snapshots-local/simple \
                     --pre \
                     hsp_vault
        pip3 install --client-cert $HSP_ARTIFACTORY_SCT_FILE_CERTIFICATE_PEM \
                     --extra-index-url https://$ART_USER:$ART_PWD@artifactory-ehv.ta.philips.com/artifactory/api/pypi/hsp-pypi-snapshots-local/simple \
                     --target=${WORKSPACE}/Source/SampleApp \
                     --pre \
                     hsp_cf_framework
    fi
    echo "End deploying Python2 DevOpsLib packages"
else
    echo "Wrong Python version given: $PYTHON_VERSION"
fi

echo "ls ${WORKSPACE}/Source/SampleApp"
ls ${WORKSPACE}/Source/SampleApp

if [[ $BUILD_TYPE =~ ^(RELEASE|UPDATE|DAY|NIGHTLY|GATED) ]]; then
    ## For DD the binaries are already in the archive ##
    ######## COPY BINARIES FROM SHARED PATH TO THE JENKINS WORKSPACE PATH ########
    cp -rf ${BUILD_SHARE}/${BUILD_NAME}/${BUILD_NUM}/binary/* ${WORKSPACE}/Source/SampleApp/hsp_cf_framework/binary/
fi

#echo -e "######## CF PARAMETERS ########"
echo -e " PCF_TEST   : ${PCF_TEST} "
echo -e " CF_LOGIN   : ${CF_LOGIN} "
echo -e " HSDP_CI_ORG: ${HSDP_CI_ORG} "
echo -e " CF_SPACE   : ${CF_SPACE} "
echo -e " CF_USN     : ${CF_USN} "

######## CF DEPLOYMENT EXECUTION ########
cd ${WORKSPACE}/Source/SampleApp/hsp_cf_framework
if [ "$PYTHON_VERSION" == "2" ]; then
    echo -e "PYTHON VERSION"
    python --version
    python auto_deploy.py ${PCF_TEST} ${CF_LOGIN} ${HSDP_CI_ORG} ${CF_SPACE} ${CF_USN} ${CF_PWD} smoke.csv info 1.0.0.0
elif [ "$PYTHON_VERSION" == "3" ]; then
    echo -e "PYTHON VERSION"
    python3 --version
    python3 auto_deploy.py ${PCF_TEST} ${CF_LOGIN} ${HSDP_CI_ORG} ${CF_SPACE} ${CF_USN} ${CF_PWD} smoke.csv info 1.0.0.0
else
    echo "Wrong Python version given: $PYTHON_VERSION"
fi