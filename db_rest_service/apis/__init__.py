from flask_restplus import Api

from .nagios import api as ns1

api = Api(
    title='DB rest service',
    version='1.0',
    description='A description',
    # All API metadatas
)

api.add_namespace(ns1)
