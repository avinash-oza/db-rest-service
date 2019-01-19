from flask import request
from flask_restplus import Namespace, Resource, fields, reqparse
from pymysql.cursors import DictCursor

from db_rest_service import app
from db_rest_service.db_config import mysql_nagios

api = Namespace('nagios', description='Nagios alerts related operations')

NagiosAlertModel = api.model('NagiosAlertModel',
                             {'date_inserted': fields.DateTime(),
                              'message_text': fields.String(),
                              'hostname': fields.String(),
                              'id': fields.Integer()})
NagiosAlertListModel = api.model('NagiosAlertListModel', {
    'alerts': fields.List(fields.Nested(NagiosAlertModel))
})

NagiosInsertAlertModel = api.model('NagiosInsertAlertModel',
                                   {'hostname': fields.String(),
                                    'service_name': fields.String(),
                                    'notification_type': fields.String(),
                                    'message_text': fields.String()
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

        conn = mysql_nagios.get_db()
        cursor = conn.cursor(cursor=DictCursor)
        cursor.execute(query)
        return {'alerts': list(cursor)}

    @api.expect(NagiosInsertAlertModel, validate=True)
    def post(self):
        """
        Allows the addition of new alerts
        :return:
        """
        alert_data = request.json

        conn = mysql_nagios.get_db()
        cursor = conn.cursor()
        query = "INSERT INTO `nagios_alerts`(`message_text`, `hostname`, `service_name`, `notification_type`) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (alert_data['message_text'], alert_data['hostname'], alert_data['service_name'], alert_data['notification_type']))
        conn.commit()
        app.logger.info("Inserted alert successfully")

    @api.doc(params={'id': 'The ID to update', 'status': 'The new status of the alert'})
    def put(self):
        """
        Handles updating an alerts status
        :return: 200 if successful
        """
        new_status = request.args['status'].upper()
        alert_id = int(request.args['id'])

        query = "UPDATE nagios_alerts SET status=%s, date_sent=NOW() where id=%s"

        conn = mysql_nagios.get_db()
        cursor = conn.cursor()
        cursor.execute(query, (new_status, alert_id))
        conn.commit()