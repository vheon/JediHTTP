#!/bin/bash
set -e

if [[ ${TRAVIS_OS_NAME} == "osx" ]]; then
  # install pyenv
  git clone https://github.com/yyuu/pyenv.git ~/.pyenv
  PYENV_ROOT="$HOME/.pyenv"
  PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init -)"

  case "${TOXENV}" in
    py26)
      curl -O https://bootstrap.pypa.io/get-pip.py
      python get-pip.py --user
      ;;
    py27)
      curl -O https://bootstrap.pypa.io/get-pip.py
      python get-pip.py --user
      ;;
    py33)
      pyenv install 3.3.6
      pyenv global 3.3.6
      ;;
  esac
  pyenv rehash
  python -m pip install --user virtualenv
else
  pip install virtualenv
fi

python -m virtualenv ~/.venv
source ~/.venv/bin/activate
echo "Installing TOX!!!"
pip install tox
