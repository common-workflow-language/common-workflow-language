#!/bin/bash

set -e
set -x

package=schema-salad
module=schema_salad
slug=${TRAVIS_PULL_REQUEST_SLUG:=common-workflow-language/schema_salad}
repo=https://github.com/${slug}.git
run_tests="bin/py.test --pyarg ${module}"
pipver=8.0.1 # minimum required version of pip
setupver=20.10.1 # minimum required version of setuptools
PYVER=${PYVER:=2.7}

rm -Rf "testenv${PYVER}_"? || /bin/true

export HEAD=${TRAVIS_PULL_REQUEST_SHA:-$(git rev-parse HEAD)}

if [ "${RELEASE_SKIP}" != "head" ]
then
	virtualenv "testenv${PYVER}_1" -p "python${PYVER}"
	# First we test the head
	# shellcheck source=/dev/null
	source "testenv${PYVER}_1/bin/activate"
	rm "testenv${PYVER}_1/lib/python-wheels/setuptools"* \
		&& pip install --force-reinstall -U pip==${pipver} \
	        && pip install setuptools==${setupver} wheel
	make install-dependencies
	make test
	pip uninstall -y ${package} || true; pip uninstall -y ${package} \
		|| true; make install
	mkdir "testenv${PYVER}_1/not-${module}"
	# if there is a subdir named '${module}' py.test will execute tests
	# there instead of the installed module's tests
	
	pushd "testenv${PYVER}_1/not-${module}"
	# shellcheck disable=SC2086
	../${run_tests}; popd
fi


virtualenv "testenv${PYVER}_2" -p "python${PYVER}"
virtualenv "testenv${PYVER}_3" -p "python${PYVER}"
virtualenv "testenv${PYVER}_4" -p "python${PYVER}"
virtualenv "testenv${PYVER}_5" -p "python${PYVER}"


# Secondly we test via pip

pushd "testenv${PYVER}_2"
# shellcheck source=/dev/null
source bin/activate
rm lib/python-wheels/setuptools* \
	&& pip install --force-reinstall -U pip==${pipver} \
        && pip install setuptools==${setupver} wheel
# The following can fail if you haven't pushed your commits to ${repo}
pip install -e "git+${repo}@${HEAD}#egg=${package}"
pushd src/${package}
make install-dependencies
make dist
make test
cp dist/${package}*tar.gz "../../../testenv${PYVER}_3/"
cp dist/${module}*whl "../../../testenv${PYVER}_4/"
pip uninstall -y ${package} || true; pip uninstall -y ${package} || true; make install
popd # ../.. no subdir named ${proj} here, safe for py.testing the installed module
# shellcheck disable=SC2086
${run_tests}
popd

# Is the source distribution in testenv${PYVER}_2 complete enough to build
# another functional distribution?

pushd "testenv${PYVER}_3/"
# shellcheck source=/dev/null
source bin/activate
rm lib/python-wheels/setuptools* \
	&& pip install --force-reinstall -U pip==${pipver} \
        && pip install setuptools==${setupver} wheel
pip install ${package}*tar.gz
pip install pytest
mkdir out
tar --extract --directory=out -z -f ${package}*.tar.gz
pushd out/${package}*
make dist
make test
pip uninstall -y ${package} || true; pip uninstall -y ${package} || true; make install
mkdir ../not-${module}
pushd ../not-${module}
# shellcheck disable=SC2086
../../${run_tests}; popd
popd
popd

# Is the wheel in testenv${PYVER}_2 installable and will it pass the tests

pushd "testenv${PYVER}_4/"
# shellcheck source=/dev/null
source bin/activate
rm lib/python-wheels/setuptools* \
	&& pip install --force-reinstall -U pip==${pipver} \
        && pip install setuptools==${setupver} wheel
pip install ${module}*.whl
pip install pytest
mkdir not-${module}
pushd not-${module}
# shellcheck disable=SC2086
../${run_tests}; popd
popd
