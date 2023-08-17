py -3.11 -m PyInstaller gcft.spec
if %errorlevel% neq 0 exit /b %errorlevel%
py -3.11 build.py
if %errorlevel% neq 0 exit /b %errorlevel%
