@ECHO OFF
REM This may not be the safest way to perform this
PUSHD %~dp0\\..\\..\\
mkdocs serve --config-file custom.yml %*
POPD
