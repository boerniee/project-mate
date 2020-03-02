while true; do
	flask db upgrade
	if [[ "$?" == "0" ]]; then
		break
	fi
	echo Deploy command failed, retrying in 5 secs
	sleep 5
done
export FLASK_APP=clubmate.py
flask translate compile
gunicorn -b 0.0.0.0:5000 --access-logfile - clubmate:app
