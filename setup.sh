echo "Python version should be 3.10 or higher"
mkdir -p ./venv
python3 -m venv ./venv

source ./venv/bin/activate
pip3 install -r ./requirements.txt
