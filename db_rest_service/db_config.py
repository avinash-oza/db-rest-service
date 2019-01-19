import os
from db_rest_service import app
from flaskext.mysql import MySQL

mysql_nagios = MySQL()
# TODO: proper passwords and settings here
keys_to_defaults = {'MYSQL_DATABASE_USER': 'root',
                    'MYSQL_DATABASE_PASSWORD': 'my-secret-pw',
                    'MYSQL_DATABASE_DB': 'telegram_bot',
                    'MYSQL_DATABASE_HOST': 'localhost'}
for key, default in keys_to_defaults.items():
    app.config[key] = os.environ.get(key, default)

mysql_nagios.init_app(app)