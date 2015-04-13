import os

DEBUG = True

# Database
MONGODB_HOST = os.environ.get('MONGODB_HOST')
MONGODB_PORT = int(os.environ.get('MONGODB_PORT'))
MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE')
