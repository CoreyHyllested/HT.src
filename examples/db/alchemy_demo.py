import sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

#Connection

engine = create_engine('sqlite:///:memory:', echo=True)

engine.execute("select 1").scalar()

#Declare Base

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


#Creating Sessiona and activating the session
Session = sessionmaker(bind=engine)
session=Session()

#Flushing out all the tables!

Base.metadata.create_all(engine) 

# Create User Object

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
metadata = MetaData()

class User(Base):
     __tablename__ = 'users'

     id = Column(Integer, Sequence(user_id_seq),primary_key=True)
     name = Column(String)
     fullname = Column(String)
     password = Column(String)

     def __init__(self, name, fullname, password):
         self.name = name
         self.fullname = fullname
         self.password = password

     def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)

     addresses = relationship("Address", order_by="Address.id", backref="user",cascade="all, delete, delete-orphan") #for Address table reference with cascade delete

#Creating foreign key relationship with a email table which has user id to email one to many relationship	

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class Address(Base):
     __tablename__ = 'addresses'
     id = Column(Integer, primary_key=True)
     email_address = Column(String, nullable=False)
     user_id = Column(Integer, ForeignKey('users.id'))

     user = relationship("User", backref=backref('addresses', order_by=id))

     def __init__(self, email_address):
         self.email_address = email_address

     def __repr__(self):
         return "<Address('%s')>" % self.email_address

#Flushing out all the tables!

Base.metadata.create_all(engine) 

#Join two tables
for u, a in session.query(User, Address).\
                    filter(User.id==Address.user_id).\
                    filter(Address.email_address=='jack@google.com').\
                    all():   
    print u, a

query.join(Address, User.id==Address.user_id)    # explicit condition
query.join(User.addresses)                       # specify relationship from left to right
query.join(Address, User.addresses)              # same, with explicit target
query.join('addresses')                          # same, using a string

query.outerjoin(User.addresses)   # LEFT OUTER JOIN


#Adding New Objects//

ed_user = User('ed', 'Ed Jones', 'edspassword')
session.add(ed_user)
our_user = session.query(User).filter_by(name='ed').first()
our_user
//Check 
ed_user is our_user

session.add_all([
     User('wendy', 'Wendy Williams', 'foobar'),
     User('mary', 'Mary Contrary', 'xxg527'),
     User('fred', 'Fred Flinstone', 'blah')])

ed_user.password = 'f8s7ccs'

#Check the session status

session.dirty
session.New

session.commit()

#Rolling back

ed_user.name = 'Edwardo'
fake_user = User('fakeuser', 'Invalid', '12345')
session.add(fake_user)

session.query(User).filter(User.name.in_(['Edwardo', 'fakeuser'])).all()

session.rollback()
fake_user in session

session.query(User).filter(User.name.in_(['ed', 'fakeuser'])).all() 

#How to Query 
for instance in session.query(User).order_by(User.id): 
	print instance.name, instance.fullname
for name, fullname in session.query(User.name, User.fullname): 
    print name, fullname

for row in session.query(User, User.name).all(): 
    print row.User, row.name

#labeling

for row in session.query(User.name.label('name_label')).all(): 
    print(row.name_label)
#alias 

from sqlalchemy.orm import aliased
user_alias = aliased(User, name='user_alias')
for row in session.query(user_alias, user_alias.name).all(): 
    print row.user_alias

for u in session.query(User).order_by(User.id)[1:3]: 
    print u

for name, in session.query(User.name).\
			filter_by(fullname='Ed Jones'): 
    print name

for user in session.query(User).\
          filter(User.name.like('%ed%').\
          filter(User.fullname=='Ed Jones')\
          : 
    print user

#AND

from sqlalchemy import and_
filter(and_(User.name == 'ed', User.fullname == 'Ed Jones'))

filter(User.name == 'ed').filter(User.fullname == 'Ed Jones')

#Match

query.filter(User.name.match('wendy'))

#Lists and scalar

query = session.query(User).filter(User.name.like('%ed')).order_by(User.id)
query.all()
query.first()

#order-by

for user in session.query(User).\
            filter("id<224").\
            order_by("id").all(): 
     print user.name

session.query(User).filter("id<:value and name=:name").\
     params(name='fred').order_by(User.id).one() 

#Using SQL directly. Have to use from_statement 

session.query(User).from_statement(
                     "SELECT * FROM users where name=:name").\
                     params(name='ed').all()

session.query("id", "name", "thenumber12").\
         from_statement("SELECT id, name, 12 as "
                 "thenumber12 FROM users where name=:name").\
                 params(name='ed').all()


#Count so easy

session.query(User).filter(User.name.like('%ed')).count() 

# Count with function

from sqlalchemy import func
session.query(func.count(User.name), User.name).group_by(User.name).all()  

#Count all
session.query(func.count('*')).select_from(User).scalar()

#Join two tables
for u, a in session.query(User, Address).\
                    filter(User.id==Address.user_id).\
                    filter(Address.email_address=='jack@google.com').\
                    all():   
    print u, a

query.join(Address, User.id==Address.user_id)    # explicit condition
query.join(User.addresses)                       # specify relationship from left to right
query.join(Address, User.addresses)              # same, with explicit target
query.join('addresses')                          # same, using a string

query.outerjoin(User.addresses)   # LEFT OUTER JOIN

User.__table__ 
User.__mapper__ 

# Sub Query

from sqlalchemy.sql import func
stmt = session.query(Address.user_id, func.count('*').\
         label('address_count')).\
         group_by(Address.user_id).subquery()

for u, count in session.query(User, stmt.c.address_count).\
     outerjoin(stmt, User.id==stmt.c.user_id).order_by(User.id): 
     print u, count

#Exists to check elements in joined tables

from sqlalchemy.sql import exists
stmt = exists().where(Address.user_id==User.id)
for name, in session.query(User.name).filter(stmt):   
     print name

#any

for name, in session.query(User.name).\
         filter(User.addresses.any()):   
    print name

# Any to match exact word. Can be useful for Search

for name, in session.query(User.name).\
    filter(User.addresses.any(Address.email_address.like('%google%'))):   
    print name


# has just in case

session.query(Address).\
        filter(~Address.user.has(User.name=='jack')).all() 

# Joined Load

from sqlalchemy.orm import joinedload

jack = session.query(User).\
                        options(joinedload(User.addresses)).\
                        filter_by(name='jack').one()


#subquery Load

from sqlalchemy.orm import subqueryload
jack = session.query(User).\
                 options(subqueryload(User.addresses)).\
                 filter_by(name='jack').one()

conn = engine.connect()
conn

result = conn.execute(ins)

# Sending list of Dictionaries

conn.execute(addresses.insert(), [ 
    {'user_id': 1, 'email_address' : 'jack@yahoo.com'},
    {'user_id': 1, 'email_address' : 'jack@msn.com'},
    {'user_id': 2, 'email_address' : 'www@www.org'},
    {'user_id': 2, 'email_address' : 'wendy@aol.com'},
 ])

# Basic Select

from sqlalchemy.sql import select
s = select([users])
result = conn.execute(s) 

for row in result:
     print row 


#Column objects directly as key

for row in conn.execute(s):  
     print "name:", row[users.c.name], "; fullname:", row[users.c.fullname


# One to Many relationship

class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    children = relationship("Child", backref="parent")

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))

#Many to One

class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('child.id'))
    child = relationship("Child")

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True, backref="parents")



#One to One

class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('child.id'))
    child = relationship("Child", backref=backref("parent", uselist=False))

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)

#Many to many

association_table = Table('association', Base.metadata,
    Column('left_id', Integer, ForeignKey('left.id')),
    Column('right_id', Integer, ForeignKey('right.id'))
)

class Parent(Base):
    __tablename__ = 'left'
    id = Column(Integer, primary_key=True)
    children = relationship("Child",
                    secondary=association_table,
                    backref="parents")

class Child(Base):
    __tablename__ = 'right'
    id = Column(Integer, primary_key=True)


