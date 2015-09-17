#!flask/bin/python

from migrate.versioning import api
from config import SQLASCHEMY_DATABASE_URI
from config import SQLASCHEMY_MIGRATE_REPO
from app import db
import os.path

db.create_all()

if not os.path.exists(SQLASCHEMY_MIGRATE_REPO):
    api.create(SQLASCHEMY_MIGRATE_REPO,'database repository')
    api.version_control(SQLASCHEMY_DATABASE_URI,SQLASCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLASCHEMY_DATABASE_URI,SQLASCHEMY_MIGRATE_REPO,
                        api.version(SQLASCHEMY_MIGRATE_REPO))