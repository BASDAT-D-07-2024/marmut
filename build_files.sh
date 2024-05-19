curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.9 get-pip.py

PYTHON_PATH=/usr/bin/python3.9

# Install dependencies
$PYTHON_PATH -m pip install --upgrade setuptools
$PYTHON_PATH -m pip install -r requirements.txt

# Jalankan migrasi dan kumpulkan static files
$PYTHON_PATH manage.py migrate 
$PYTHON_PATH manage.py collectstatic
