from flask import Flask
app = Flask(__name__)

from .apis import api
api.init_app(app)




# app.config.from_mapping({'GENERAL_HOSTNAME': 'DEFAULT_HOST'})
if not app.config.from_envvar('APP_SETTINGS', silent=True):
    print("Did not find a config to load")