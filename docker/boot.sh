While true; do
	flask db upgrade
	if [[ „$?“ == „0“ ]]; then
		break
	fi
	echo Deploy command failed, retrying in 5 secs…
	sleep 5
done
flask translate compile
gunicorn -b 0.0.0.0:5000 clubmate:app
