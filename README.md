# Project Mate

Sell Mate to your colleagues. Fast! WOW!

## Install

### Main Application

After you checked out the project you have to install a virtual environment:  
`python3 -m venv mate`

Start the virtual environment:  
Linux/Unix: `source mate/bin/activate`  
Windows (PS): `.\mate\Scripts\Activate.ps1`

Install required packages via: `pip install -r requirements.txt `

Export Flask variables:

To reload on file changes:  
Linux/Unix: `export FLASK_DEBUG="1"`  
Windows (PS): `$env:FLASK_DEBUG="1"`

To use custom commands bellow:  
Linux/Unix: `export FLASK_APP="clubmate.py"`  
Windows (PS): `$env:FLASK_APP="clubmate.py"`

Initialize the database and compile the languages:  
`flask translate compile`  
`flask db upgrade`

Export the confguration variables for the [configuration](config.py).
For Example: `export MAIL_SERVER="smtp.example.com"`
If you use the background worker, you need to export the `REDIS_URL`.

Then you can start the development server via `flask run` and open `localhost:5000` in your browser.

### Celery worker

For some jobs, like the billing, you need a celery worker with a [Redis](https://redis.io/download).
Export the same variables as exported above for the main application.

Start the celery worker after you activated the virtual environment.
Start worker: `celery worker -A app.celery -B --loglevel=info`
