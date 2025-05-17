#!/usr/bin/env bash
poetry run pytest --maxfail=5 --disable-warnings
code=$?
if [ $code -eq 0 ] || [ $code -eq 5 ]; then
  exit 0
else
  exit $code
fi 