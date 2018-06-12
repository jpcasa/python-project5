from peewee import *
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin

DATABASE = SqliteDatabase("journals.db")


class User(UserMixin, Model):
    email = CharField(unique=True)
    password = CharField()

    @classmethod
    def create_user(cls, email, password):
        try:
            cls.create(
                email=email,
                password=generate_password_hash(password)
            )
        except IntegrityError:
            raise ValueError

    class Meta:
        database = DATABASE


class Entry(Model):
    title = CharField()
    date = DateTimeField()
    timeSpent = IntegerField()
    whatILearned = TextField()
    resourcesToRemember = TextField()
    tags = CharField()
    user = ForeignKeyField(User, related_name='entries')

    class Meta:
        database = DATABASE
        order_by = ('-date',)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry], safe=True)
