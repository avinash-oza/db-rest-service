import datetime
from flask import request
from flask_restplus import Namespace, Resource, fields, reqparse
from pymysql.cursors import DictCursor
from dateutil.parser import parse

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

parser = reqparse.RequestParser()
parser.add_argument('type', type=str, choices=['UNSENT', 'ALL'], default='UNSENT', help='types of alerts to return')
parser.add_argument('limit', type=int, default=5, help='number of alerts to return')

# insert alert parser
insert_parser = reqparse.RequestParser()
insert_parser.add_argument('host_name', type=str, required=True, help='host name')
insert_parser.add_argument('host_state', type=str, required=True, help='host state')
insert_parser.add_argument('host_address', type=str, required=True, help='host state')
insert_parser.add_argument('n_datetime', type=str, required=True, help='host state')
insert_parser.add_argument('service_name', type=str, required=True, help='host state')
insert_parser.add_argument('notification_type', type=str, required=True, help='host state')
insert_parser.add_argument('alert_type', type=str, required=True, help='host state')
insert_parser.add_argument('output_text', type=str, required=True, help='host state')


MESSAGE_TEXT="""
***** Nagios *****
Notification Type: {alert_type}
{host_or_service_line}
State: {host_state}
Address: {host_address}
Info: {output_text}
Date/Time: {n_datetime}
"""


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

    @api.expect(insert_parser, validate=True)
    def post(self):
        """
        Allows the addition of new alerts
        :return:
        """
        alert_data = insert_parser.parse_args()
        alert_data['n_datetime'] = parse(alert_data['n_datetime']) if alert_data['n_datetime'] else datetime.datetime.utcnow()
        alert_data['host_or_service_line'] = ""
        if alert_data['alert_type'].upper() == 'HOST':
            alert_data['host_or_service_line'] = "HOST:{0}".format(alert_data['host_name'])

        message_text = MESSAGE_TEXT.format(**alert_data)

        conn = mysql_nagios.get_db()
        cursor = conn.cursor()
        query = "INSERT INTO `nagios_alerts`( `date_inserted`, `message_text`, `hostname`, `service_name`, `notification_type`) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (alert_data['n_datetime'], message_text, alert_data['host_name'], alert_data['service_name'], alert_data['notification_type']))
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