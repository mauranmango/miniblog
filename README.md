# ReadME

## Instalimi

Instalo te gjitha librarite ne menyre qe mos te shfaqen errore.

```bash
pip install -r requirements.txt
```
## Migrimi i db

Krijo nje databaze ne PostgreSQL dhe vendos kredencialet e tua ne environment variables ose te file config.py

```python
import os

class Config(object):
   
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'celes-sekret'

    user  = "mauran"
    pass = "1234abcd"
    db = "microdb"

    SQLALCHEMY_DATABASE_URI = f"postgres://{user}:{pass}@localhost:5432/{db}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```
Per tu lidhur dhe per te migruar modelet(tabelat) aplikojme komandat ne terminal:

*flask db init*\
*flask db migrate -m "migrimi i databazes"*\
*flask db upgrade*


## Perdorimi 

Per te ekzekutuar aplikacionin do shkojme te file app.py dhe i japim run.

```python
from microblog import app


if __name__ == '__main__':
    app.run(debug=False)

```
