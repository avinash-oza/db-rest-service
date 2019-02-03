from flask_restplus import Api

from .nagios import api as ns1
from .status import api as ns2
from .messages import api as ns3

api = Api(
    title='DB rest service',
    version='1.0',
    description='A description',
    # All API metadatas
)

api.add_namespace(ns1)
api.add_namespace(ns2)
api.add_namespace(ns3)
