#!/bin/bash

set -e
set -x

package=schema-salad
module=schema_salad
repo=https://github.com/common-workflow-language/schema_salad.git
run_tests="py.test --pyarg ${module}"

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
pip uninstall -y ${package} || true; pip uninstall -y ${package} || true; make install
mkdir testenv1/not-${module}
# if there is a subdir named '${module}' py.test will execute tests
# there instead of the installed module's tests
pushd testenv1/not-${module}; ../bin/${run_tests}; popd


# Secondly we test via pip

cd testenv2
source bin/activate
pip install -U setuptools==3.4.1
pip install -e git+${repo}@${HEAD}#egg=${package}
cd src/${package}
make install-dependencies
make dist
make test
cp dist/${package}*tar.gz ../../../testenv3/
pip uninstall -y ${package} || true; pip uninstall -y ${package} || true; make install
cd ../.. # no subdir named ${proj} here, safe for py.testing the installed module
bin/${run_tests}

# Is the distribution in testenv2 complete enough to build another
# functional distribution?

cd ../testenv3/
source bin/activate
pip install -U setuptools==3.4.1
pip install ${package}*tar.gz
pip install pytest
tar xzf ${package}*tar.gz
cd ${package}*
make dist
make test
pip uninstall -y ${package} || true; pip uninstall -y ${package} || true; make install
mkdir ../not-${module}
pushd ../not-${module} ; ../bin/${run_tests}; popd
