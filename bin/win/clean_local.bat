@ECHO OFF
REM This may not be the safest way to perform this
PUSHD %~DP0\\..\\..\\
SETLOCAL
REM Use a var for consistency, still need to udpate .gitignore if this is changed
set DOCS_OUT=local_docs
RMDIR /S /Q %DOCS_OUT%
DEL /Q %DOCS_OUT%.zip
ENDLOCAL
POPD
