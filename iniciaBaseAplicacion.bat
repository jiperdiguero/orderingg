set FLASK_APP=orderingg.py
flask db upgrade
python fixture.py
set FLASK_DEBUG=1
flask run