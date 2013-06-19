#!/bin/bash

_PYTHON=${2:-python2.7}
_PYTHON_VERSION=$($_PYTHON -c 'import sys; print ".".join([str(v) for v in sys.version_info[:2]])')
_ENV=${1:-eyeD3-${_PYTHON_VERSION}}

source /usr/bin/virtualenvwrapper.sh

mkvirtualenv -a $(pwd) --python=${_PYTHON} --distribute ${_ENV}
workon $_ENV

# FIXME
PKGS_OPTS=
if test -d ./.pip-download-cache; then
    export PIP_DOWNLOAD_CACHE=./.pip-download-cache    
fi

if test $_PYTHON_VERSION = "2.6"; then
    pip install $PKG_OPTS -r requirements-26.txt
    pip install $PKG_OPTS -r dev-requirements-26.txt
else
    pip install $PKG_OPTS -r dev-requirements.txt
fi

cat /dev/null >| $VIRTUAL_ENV/bin/postactivate
echo "alias cd-top=\"cd $PWD\"" >> $VIRTUAL_ENV/bin/postactivate
echo "export PATH=\"$PWD/bin:$PATH\"" >> $VIRTUAL_ENV/bin/postactivate
echo "export PYTHONPATH=\"$PWD/src\"" >> $VIRTUAL_ENV/bin/postactivate

cat /dev/null >| $VIRTUAL_ENV/bin/postdeactivate
echo "unalias cd-top" >> $VIRTUAL_ENV/bin/postdeactivate
# The changes to PATH are handled by normal deactivate
# Changes to PYTHONPATH are not undone, yet.
