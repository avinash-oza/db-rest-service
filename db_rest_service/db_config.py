from db_rest_service import app
from flaskext.mysql import MySQL

mysql_nagios = MySQL()
 # TODO: proper passwords and settings here
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'my-secret-pw'
app.config['MYSQL_DATABASE_DB'] = 'telegram_bot'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql_nagios.init_app(app)