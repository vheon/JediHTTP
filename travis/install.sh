#     Copyright 2015 Cedraro Andrea <a.cedraro@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
#    limitations under the License.

#!/bin/bash
# Adapted from:
# https://github.com/pyca/cryptography/blob/master/.travis/install.sh

set -e

if [[ ${TRAVIS_OS_NAME} == "osx" ]]; then
  # RVM overrides the cd, popd, and pushd shell commands, causing the
  # "shell_session_update: command not found" error on macOS when executing those
  # commands.
  unset -f cd popd pushd

  # Install pyenv
  PYENV_ROOT="${HOME}/.pyenv"
  if [[ ! -d "${PYENV_ROOT}/.git" ]]; then
    rm -rf ${PYENV_ROOT}
    git clone https://github.com/yyuu/pyenv.git ${PYENV_ROOT}
  else
    ( cd ${PYENV_ROOT}; git pull; )
  fi
  PATH="${PYENV_ROOT}/bin:${PATH}"
  eval "$(pyenv init -)"

  case "${TOXENV}" in
    py26*)
      PYTHON_VERSION=2.6.9
      ;;
    py27*)
      PYTHON_VERSION=2.7.13
      ;;
    py33*)
      PYTHON_VERSION=3.3.6
      ;;
    py34*)
      PYTHON_VERSION=3.4.5
      ;;
    py35*)
      PYTHON_VERSION=3.5.2
      ;;
    py36*)
      PYTHON_VERSION=3.6.0
      ;;
  esac
  pyenv install -s ${PYTHON_VERSION}
  pyenv rehash
  pyenv global ${PYTHON_VERSION}
fi

# coverage.py 4.4 removed the path from the filename attribute in its reports.
# This leads to incorrect coverage from codecov as it relies on this attribute
# to find the source file.
pip install coverage==4.3.4 tox virtualenv
