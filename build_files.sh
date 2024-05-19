curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.9 get-pip.py

# build_files.sh
python3.9 -m pip install -r requirements.txt

# make migrations
python3.9 manage.py migrate 
python3.9 manage.py collectstatic
