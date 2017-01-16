.PHONY: clean-pyc clean-build clean-patch clean-local docs clean help lint \
        test test-all coverage docs release dist tags install \
        build-release pre-release freeze-release _tag-release _upload-release \
        _pypi-release _github-release clean-docs cookiecutter changelog
SRC_DIRS = ./src/eyed3
TEST_DIR = ./src/test
TEMP_DIR ?= ./tmp
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
    from urllib import pathname2url
except:
    from urllib.request import pathname2url
webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"
NAME ?= Travis Shirk
EMAIL ?= travis@pobox.com
BITBUCKET_USER ?= nicfit
BITBUCKET_REPO ?= eyed3
HG=hg
PYPI_REPO = pypitest

help:
	@echo "test - run tests quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "clean-docs - remove autogenerating doc artifacts"
	@echo "clean-patch - remove patch artifacts (.rej, .orig)"
	@echo "lint - check style with flake8"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "test-all - run tests on various Python versions with tox"
	@echo "release - package and upload a release"
	@echo "          PYPI_REPO=[pypitest]|pypi"
	@echo "pre-release - check repo and show version"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"
	@echo ""
	@echo "Options:"
	@echo "TEST_PDB - If defined PDB options are added when 'pytest' is invoked"
	@echo "BROWSER - Set to "yes" to open docs/coverage results in a web browser"

clean: clean-local clean-build clean-pyc clean-test clean-patch clean-docs
	rm -rf tags

clean-local:
	@# XXX Add new clean targets here.

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -rf ${TEMP_DIR}

clean-patch:
	find . -name '*.rej' -exec rm -f '{}' \;
	find . -name '*.orig' -exec rm -f '{}' \;

lint:
	flake8 $(SRC_DIRS)

_PYTEST_OPTS=

ifdef TEST_PDB
    _PDB_OPTS=--pdb -s
endif

test:
	pytest $(_PYTEST_OPTS) $(_PDB_OPTS) ${TEST_DIR}

test-all:
	tox


coverage:
	pytest --cov=./src/eyed3 \
           --cov-report=html --cov-report term \
           --cov-config=setup.cfg ${TEST_DIR}

docs:
	rm -f docs/eyed3.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ ${SRC_DIRS}
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	@if test -n '$(BROWSER)'; then \
	    $(BROWSER) docs/_build/html/index.html;\
	fi

clean-docs:
	# TODO
	#$(MAKE) -C docs clean
	-rm README.html

# FIXME: never been tested
servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

pre-release: lint test changelog
	@test -n "${NAME}" || (echo "NAME not set, needed for git" && false)
	@test -n "${EMAIL}" || (echo "EMAIL not set, needed for git" && false)
	@# TODO: Check bitbucket settings
	$(eval VERSION = $(shell python setup.py --version 2> /dev/null))
	@echo "VERSION: $(VERSION)"
	$(eval RELEASE_TAG = v${VERSION})
	@echo "RELEASE_TAG: $(RELEASE_TAG)"
	$(eval RELEASE_NAME = $(shell python setup.py --release-name 2> /dev/null))
	@echo "RELEASE_NAME: $(RELEASE_NAME)"
	check-manifest
	@if ${HG} tags -q | grep ${RELEASE_TAG} > /dev/null; then \
        echo "Version tag '${RELEASE_TAG}' already exists!"; \
        false; \
    fi
	@# TODO: Update AUTHORS file
	@# TODO: Check for tool for making bitbucket releases

changelog:
	@# TODO

build-release: test-all dist

freeze-release:
	@(test -z "`${HG} status --modified --added --deleted`" && \
      ${HG} incoming | grep 'no changes found') || \
        (printf "\n!!! Working repo has uncommited/unstaged changes. !!!\n" && \
         printf "\nCommit and try again.\n" && false)

_tag-release:
	${HG} tag ${RELEASE_TAG}
	-${HG} commit -m "Release $(RELEASE_TAG)"
	${HG} push --rev .

release: pre-release freeze-release build-release _tag-release _upload-release


_bitbucket-release:
	# Not implemented
	false

_web-release:
	#find dist -type f -exec scp register -r ${PYPI_REPO} {} \;
	# Not implemented
	true


_upload-release: _bitbucket-release _pypi-release _web-release


_pypi-release:
	find dist -type f -exec twine register -r ${PYPI_REPO} {} \;
	find dist -type f -exec twine upload -r ${PYPI_REPO} --skip-existing {} \;

dist: clean
	python setup.py sdist
	python setup.py bdist_egg
	python setup.py bdist_wheel
	@# The cd dist keeps the dist/ prefix out of the md5sum files
	cd dist && \
    for f in $$(ls); do \
        md5sum $${f} > $${f}.md5; \
    done
	ls -l dist

install: clean
	python setup.py install

tags:
	ctags -R ${SRC_DIRS}

README.html: README.rst
	rst2html5.py README.rst >| README.html

cookiecutter:
	rm -rf ${TEMP_DIR}
	${HG} clone --updaterev `${HG} branch` . ${TEMP_DIR}/eyeD3
	# FIXME: Pull from a non-local ./cookiecutter
	cookiecutter -o ${TEMP_DIR} -f --config-file ./.cookiecutter.json \
                 --no-input ../../nicfit.py/cookiecutter
	cd ${TEMP_DIR}/eyeD3 && ${HG} status
