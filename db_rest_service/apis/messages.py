from flask import request
from flask_restplus import Namespace, Resource, fields, reqparse
from pymysql.cursors import DictCursor

from db_rest_service import app
from db_rest_service.db_config import mysql_nagios

api = Namespace('messages', description='Message related operations')


class AcknowledgeableMessage(fields.Raw):
    def format(self, value):
        print("XXXX", value)
        return True if value is not None else False

MessageModel = api.model('MessageModel',
                         {'date_inserted': fields.DateTime(),
                          'message_text': fields.String(),
                          'can_acknowledge': AcknowledgeableMessage(default=False),
                          'id': fields.Integer()})
MessageListModel = api.model('MessageListModel ', {
    'alerts': fields.List(fields.Nested(MessageModel))
})

parser = reqparse.RequestParser()
parser.add_argument('type', type=str, choices=['UNSENT', 'ALL'], default='UNSENT', help='types of alerts to return')
parser.add_argument('limit', type=int, default=5, help='number of alerts to return')

# insert message parser
insert_parser = reqparse.RequestParser()
insert_parser.add_argument('message_text', type=str, required=True, help='message text to send')


@api.route('/')
class MessagesResource(Resource):
    @api.marshal_with(MessageListModel)
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
        Allows the addition of new messages
        :return:
        """
        alert_data = insert_parser.parse_args()

        conn = mysql_nagios.get_db()
        cursor = conn.cursor()
        query = "INSERT INTO `nagios_alerts`( `message_text`) VALUES (%s)"
        cursor.execute(query, (alert_data['message_text'], ))
        conn.commit()
        app.logger.info("Inserted message successfully")

@api.route('/<int:message_id>')
class MessageUpdate(Resource):
    @api.doc(params={'status': 'The new status of the message'})
    def post(self, message_id):
        """
        Handles updating an alerts status
        :return: 200 if successful
        """
        new_status = request.args['status'].upper()

        query = "UPDATE nagios_alerts SET status=%s, date_sent=NOW() where id=%s"

        conn = mysql_nagios.get_db()
        cursor = conn.cursor()
        cursor.execute(query, (new_status, message_id))
        conn.commit()