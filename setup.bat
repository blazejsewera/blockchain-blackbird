@echo off

echo "Python version should be 3.10 or higher"
mkdir -p ./venv
py -m venv ./venv

call .\venv\bin\activate.bat
& C:/Users/48795/AppData/Local/Programs/Python/python10/python.exe -m pip install -r .\requirements.txt
