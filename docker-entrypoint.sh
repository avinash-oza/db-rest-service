#!/bin/bash

set +e

gunicorn -b 0.0.0.0:5000 db_rest_service:app

exec "$@"