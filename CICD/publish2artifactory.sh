#!/bin/bash -e
BRANCHNAME=$1

echo "######## PROXY ENVIRONMENT SETUP ########"
export http_proxy=${http_proxy}
export https_proxy=${http_proxy}
export no_proxy="artifactory-ehv.ta.philips.com,tfsapac04.ta.philips.com"

echo "http_proxy=${http_proxy}"
echo "https_proxy=${http_proxy}"
echo "no_proxy=${no_proxy}"

cd ${WORKSPACE}/Source

if [[ $BUILD_TYPE =~ ^(RELEASE|UPDATE) && $CREATE_RELEASE_VERSION ]]; then
    ARTIFACTORY_REPO=artifactory-release
    echo "Bumping build version to release"
    bumpversion --allow-dirty release
else
    echo "Bumping build version to dev"
    bumpversion --allow-dirty build
    ARTIFACTORY_REPO=artifactory-snapshot
fi

echo "ARTIFACTORY_REPO=${ARTIFACTORY_REPO}"
echo "BRANCHNAME = ${BRANCHNAME}"

RAW_VERSION=$(sed -n '2p' < .bumpversion.cfg)
VERSION=$(echo ${RAW_VERSION} | cut -d"=" -f2)
echo "Version bumped to: ${VERSION}"

find . -name 'setup.py' | xargs git add
git add .bumpversion.cfg
git commit -m "Updated the version of packages to version ${VERSION}"
git push  https://tfsapac04.ta.philips.com/tfs/DHPCollection/DHP/_git/DevOpsLib ${BRANCHNAME}

python3 --version

cd ${WORKSPACE}/Source/Python/cf
python3 setup.py sdist bdist_wheel --universal upload -r ${ARTIFACTORY_REPO}

cd ${WORKSPACE}/Source/Python/cf_framework
python3 setup.py sdist bdist_wheel --universal upload -r ${ARTIFACTORY_REPO}

cd ${WORKSPACE}/Source/Python/vault
python3 setup.py sdist bdist_wheel --universal upload -r ${ARTIFACTORY_REPO}
