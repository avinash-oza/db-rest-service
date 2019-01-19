from flask import Flask
from flask_restplus import Api
from .apis import api

app = Flask(__name__)
api.init_app(app)

# app.config.from_mapping({'GENERAL_HOSTNAME': 'DEFAULT_HOST'})
# if not app.config.from_envvar('APP_SETTINGS', silent=True):
#     print("Did not find a config to load")