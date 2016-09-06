# This file is part of schema-salad,
# https://github.com/common-workflow-language/schema-salad/, and is
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Contact: common-workflow-language@googlegroups.com

# make pep8 to check for basic Python code compliance
# make autopep8 to fix most pep8 errors
# make pylint to check Python code for enhanced compliance including naming
#  and documentation
# make coverage-report to check coverage of the python scripts by the tests

MODULE=schema_salad

# `SHELL=bash` Will break Titus's laptop, so don't use BASH-isms like
# `[[` conditional expressions.
PYSOURCES=$(wildcard ${MODULE}/**.py tests/*.py) setup.py
DEVPKGS=pep8 diff_cover autopep8 pylint coverage pep257 pytest flake8

VERSION=$(shell git describe --tags --dirty | sed s/v//)

## all         : default task
all: ./setup.py develop

## help        : print this help message and exit
help: Makefile
	@sed -n 's/^##//p' $<

## install-dep : install most of the development dependencies via pip
install-dep: install-dependencies

install-dependencies:
	pip install --upgrade $(DEVPKGS)
	pip install -r requirements.txt

## install     : install the ${MODULE} module and schema-salad-tool
install: FORCE
	pip install .

## dist        : create a module package for distribution
dist: dist/${MODULE}-$(VERSION).tar.gz

dist/${MODULE}-$(VERSION).tar.gz: $(SOURCES)
	./setup.py sdist

## clean       : clean up all temporary / machine-generated files
clean: FORCE
	rm -f ${MODILE}/*.pyc tests/*.pyc
	./setup.py clean --all || true
	rm -Rf .coverage
	rm -f diff-cover.html

## pep8        : check Python code style
pep8: $(PYSOURCES)
	pep8 --exclude=_version.py  --show-source --show-pep8 $^ || true

pep8_report.txt: $(PYSOURCES)
	pep8 --exclude=_version.py $^ > $@ || true

diff_pep8_report: pep8_report.txt
	diff-quality --violations=pep8 pep8_report.txt

## pep257      : check Python code style
pep257: $(PYSOURCES)
	pep257 --ignore=D100,D101,D102,D103 $^ || true

pep257_report.txt: $(PYSOURCES)
	pep257 setup.py $^ > $@ 2>&1 || true

diff_pep257_report: pep257_report.txt
	diff-quality --violations=pep8 pep257_report.txt

## autopep8    : fix most Python code indentation and formatting
autopep8: $(PYSOURCES)
	autopep8 --recursive --in-place --ignore E309 $^

# A command to automatically run astyle and autopep8 on appropriate files
## format      : check/fix all code indentation and formatting (runs autopep8)
format: autopep8
	# Do nothing

## pylint      : run static code analysis on Python code
pylint: $(PYSOURCES)
	pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
                $^ || true

pylint_report.txt: ${PYSOURCES}
	pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
		$^ > $@ || true

diff_pylint_report: pylint_report.txt
	diff-quality --violations=pylint pylint_report.txt

.coverage: $(PYSOURCES)
	coverage run --branch --source=${MODULE} setup.py test
	coverage run --append --branch --source=${MODULE} \
		-m schema_salad.main \
		--print-jsonld-context schema_salad/metaschema/metaschema.yml \
		> /dev/null
	coverage run --append --branch --source=${MODULE} \
		-m schema_salad.main \
		--print-rdfs schema_salad/metaschema/metaschema.yml \
		> /dev/null
	coverage run --append --branch --source=${MODULE} \
		-m schema_salad.main \
		--print-avro schema_salad/metaschema/metaschema.yml \
		> /dev/null
	coverage run --append --branch --source=${MODULE} \
		-m schema_salad.main \
		--print-rdf schema_salad/metaschema/metaschema.yml \
		> /dev/null
	coverage run --append --branch --source=${MODULE} \
		-m schema_salad.main \
		--print-pre schema_salad/metaschema/metaschema.yml \
		> /dev/null
	coverage run --append --branch --source=${MODULE} \
		-m schema_salad.main \
		--print-index schema_salad/metaschema/metaschema.yml \
		> /dev/null
	coverage run --append --branch --source=${MODULE} \
		-m schema_salad.main \
		--print-metadata schema_salad/metaschema/metaschema.yml \
		> /dev/null
	coverage run --append --branch --source=${MODULE} \
		-m schema_salad.makedoc schema_salad/metaschema/metaschema.yml \
		> /dev/null

coverage.xml: .coverage
	coverage xml

coverage.html: htmlcov/index.html

htmlcov/index.html: .coverage
	coverage html
	@echo Test coverage of the Python code is now in htmlcov/index.html

coverage-report: .coverage
	coverage report

diff-cover: coverage.xml
	diff-cover $^

diff-cover.html: coverage.xml
	diff-cover $^ --html-report $@

## test        : run the ${MODULE} test suite
test: FORCE
	python setup.py test

sloccount.sc: ${PYSOURCES} Makefile
	sloccount --duplicates --wide --details $^ > $@

## sloccount   : count lines of code
sloccount: ${PYSOURCES} Makefile
	sloccount $^

list-author-emails:
	@echo 'name, E-Mail Address'
	@git log --format='%aN,%aE' | sort -u | grep -v 'root'

mypy: ${PYSOURCES}
	rm -Rf typeshed/2.7/ruamel/yaml
	ln -s $(shell python -c 'from __future__ import print_function; import ruamel.yaml; import os.path; print(os.path.dirname(ruamel.yaml.__file__))') \
		typeshed/2.7/ruamel/
	MYPYPATH=typeshed/2.7 mypy --py2 --disallow-untyped-calls \
		 --fast-parser --warn-redundant-casts --warn-unused-ignores \
		 schema_salad

jenkins:
	rm -Rf env && virtualenv env
	. env/bin/activate ; \
	pip install -U setuptools pip wheel ; \
	${MAKE} install-dep coverage.html coverage.xml pep257_report.txt \
		sloccount.sc pep8_report.txt pylint_report.txt
	if ! test -d env3 ; then virtualenv -p python3 env3 ; fi
	. env3/bin/activate ; \
	pip install -U setuptools pip wheel ; \
	${MAKE} install-dep ; \
	pip install -U mypy-lang typed-ast ; ${MAKE} mypy

FORCE:
