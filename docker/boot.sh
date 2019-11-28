{\rtf1\ansi\ansicpg1252\cocoartf2509
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 Menlo-Regular;}
{\colortbl;\red255\green255\blue255;\red255\green255\blue255;\red7\green22\blue36;}
{\*\expandedcolortbl;;\cssrgb\c100000\c100000\c100000;\cssrgb\c1961\c11765\c18824;}
\paperw11900\paperh16840\margl1440\margr1440\vieww15320\viewh11660\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs36 \cf2 \cb3 \expnd0\expndtw0\kerning0
While true; do\
	flask db upgrade\
	if [[\'a0\'84$?\'93 == \'840\'93 ]]; then\
		break\
	fi\
	echo Deploy command failed, retrying in 5 secs\'85\
	sleep 5\
done\
flask translate compile\
gunicorn -b 0.0.0.0:5000 clubmate:app}