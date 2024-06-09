@echo off
REM Create the Miniconda directory
mkdir %USERPROFILE%\miniconda3

REM Download the Miniconda installer for Windows
curl -L "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe" -o "%USERPROFILE%\miniconda3\miniconda.exe"

REM Run the installer
start /wait "" %USERPROFILE%\miniconda3\miniconda.exe /InstallationType=JustMe /RegisterPython=0 /S /D=%USERPROFILE%\miniconda3

REM Remove the installer
del %USERPROFILE%\miniconda3\miniconda.exe

REM Initialize conda for the Command Prompt
call %USERPROFILE%\miniconda3\Scripts\conda init
