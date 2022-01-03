@echo off

echo "Python version should be 3.10 or higher"
mkdir -p ./venv
python3 -m venv ./venv

call .\venv\bin\activate.bat
pip3 install -r ./requirements.txt
