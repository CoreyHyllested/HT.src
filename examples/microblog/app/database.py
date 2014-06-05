from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


print 'import::db -- create engine'
engine = create_engine('postgresql://htdb:passw0rd@beta.cesf5wqzwzr9.us-east-1.rds.amazonaws.com:5432/htdb', echo=True)

print 'import::db -- create scoped session, bound to engine'
db_session = scoped_session(sessionmaker(bind=engine))

print 'import::db -- create db base'
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
	from app import models
	# configure postgresql, by creating
	print 'import::db -- create_all()'
	Base.metadata.create_all(bind=engine)
	print 'returned'
