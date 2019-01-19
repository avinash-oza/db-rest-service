from flask_restplus import Namespace, Resource, fields, reqparse
from pymysql.cursors import DictCursor

from db_rest_service import app
from db_rest_service.db_config import mysql_nagios

api = Namespace('nagios', description='Nagios alerts related operations')

NagiosAlertModel = api.model('NagiosAlertModel',
                             {'date_inserted': fields.DateTime(),
                              'message_text': fields.String(),
                              'hostname': fields.String()})
NagiosAlertListModel = api.model('NagiosAlertListModel', {
    'alerts': fields.List(fields.Nested(NagiosAlertModel))
})

parser = reqparse.RequestParser()
parser.add_argument('type', type=str, choices=['UNSENT', 'ALL'], default='UNSENT', help='types of alerts to return')
parser.add_argument('limit', type=int, default=5, help='number of alerts to return')


@api.route('/')
class NagiosAlerts(Resource):
    @api.marshal_with(NagiosAlertListModel)
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        if args['type'] == 'ALL':
            alerts_filter = '1=1'
        else:
            alerts_filter = "status='{}'".format(args['type'])

        limit_filter = 'LIMIT {}'.format(args['limit'])

        query = "SELECT * FROM telegram_bot.nagios_alerts WHERE {} ORDER BY id ASC {}".format(alerts_filter,
                                                                                              limit_filter)
        app.logger.info("Query to execute is {}".format(query))

        conn = mysql_nagios.connect()
        cursor = conn.cursor(cursor=DictCursor)
        cursor.execute(query)
        return {'alerts': list(cursor)}
