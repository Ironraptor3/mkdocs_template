@echo off
REM This may not be the safest way to perform this
pushd %~dp0\\..\\..\\
mkdocs serve --config-file custom.yml %*
popd
