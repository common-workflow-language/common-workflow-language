#!/bin/bash

set -e
set -x

proj=schema-salad
repo=https://github.com/common-workflow-language/schema_salad.git
run_tests="py.test ${proj}"

rm -Rf testenv? || /bin/true

export HEAD=`git rev-parse HEAD`
virtualenv testenv1
virtualenv testenv2
virtualenv testenv3
virtualenv testenv4

# First we test the head
source testenv1/bin/activate
make install-dependencies
make test
pip uninstall -y ${proj} || true; pip uninstall -y ${proj} || true; make install
mkdir testenv1/not-${proj}
# if there is a subdir named '${proj}' py.test will execute tests
# there instead of the installed module's tests
pushd testenv1/not-${proj}; ../bin/${run_tests}; popd


# Secondly we test via pip

cd testenv2
source bin/activate
pip install -U setuptools==3.4.1
pip install -e git+${repo}@${HEAD}#egg=${proj}
cd src/${proj}
make install-dependencies
make dist
make test
cp dist/${proj}*tar.gz ../../../testenv3/
pip uninstall -y ${proj} || true; pip uninstall -y ${proj} || true; make install
cd ../.. # no subdir named ${proj} here, safe for py.testing the installed module
bin/${run_tests}

# Is the distribution in testenv2 complete enough to build another
# functional distribution?

cd ../testenv3/
source bin/activate
pip install -U setuptools==3.4.1
pip install ${proj}*tar.gz
pip install nose
tar xzf ${proj}*tar.gz
cd ${proj}*
make dist
make test
pip uninstall -y ${proj} || true; pip uninstall -y ${proj} || true; make install
mkdir ../not-${proj}
pushd ../not-${proj} ; ../bin/${run_tests}; popd
