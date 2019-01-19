from flask_restplus import Namespace, Resource, fields

api = Namespace('nagios', description='Nagios alerts related operations')

@api.route('/')
class NagiosAlerts(Resource):
    def get(self):
        return 'Hello World'