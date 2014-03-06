#
# cd myproject
# virtualenv venv
# bash setup_venv.sh
# source venv/bin/activate
# ./util_db_create.py


venv/bin/pip install Flask==0.10.1
venv/bin/pip install Flask-Assets==0.8
venv/bin/pip install Flask-Compress==0.10.0
venv/bin/pip install Flask-Mail==0.9.0
venv/bin/pip install Flask-Oauthlib==0.4.2
venv/bin/pip install Flask-OpenID==1.1.1
venv/bin/pip install Flask-Redis==0.0.3
venv/bin/pip install Flask-SQLAlchemy==1.0
venv/bin/pip install Flask-Uploads==0.1.3
venv/bin/pip install Flask-WTF==0.9.2
venv/bin/pip install Flask-gzip==0.1
venv/bin/pip install Jinja2==2.7.1
venv/bin/pip install MarkupSafe==0.18
venv/bin/pip install SQLAlchemy==0.8.2
venv/bin/pip install WTForms==1.0.5
venv/bin/pip install Werkzeug==0.9.4
venv/bin/pip install beautifulsoup4==4.3.2
venv/bin/pip install blinker==1.3
venv/bin/pip install boto==2.13.3
venv/bin/pip install itsdangerous==0.23
venv/bin/pip install python-openid==2.2.5
venv/bin/pip install redis==2.9.0
venv/bin/pip install webassets==0.8
venv/bin/pip install wsgiref==0.1.2
venv/bin/pip install distribute==0.6.28
venv/bin/pip install gunicorn==18.0
venv/bin/pip install httplib2==0.8
venv/bin/pip install oauth2==1.5.211
venv/bin/pip install psycopg2==2.5.1
venv/bin/pip install pyOpenSSL==0.13.1
venv/bin/pip install pysolr==3.1.0
venv/bin/pip install python-linkedin==4.0
venv/bin/pip install requests==2.0.0
venv/bin/pip install requests-oauth==0.4.1
venv/bin/pip install stripe==1.9.5
venv/bin/pip install wtf==0.1
venv/bin/pip install sqlalchemy-migrate==0.8.2
venv/bin/pip install flask-whooshalchemy==0.54a
venv/bin/pip install flup

echo "39 packages"
venv/bin/pip freeze | wc
