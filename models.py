#!/usr/bin/env python3

import re
from unicodedata import normalize

from peewee import *
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin

DATABASE = SqliteDatabase("journals.db")

class User(UserMixin, Model):
    email = CharField(unique=True)
    password = CharField()

    def get_posts(self):
        """Get Posts from User organized by Date"""
        return Entry.select().where(
            Entry.user == self
        ).order_by(
            Entry.date.desc()
        )

    def get_post(self, url):
        return Entry.select().where(Entry.url == url)

    def slugify(self, text, delim=u'-'):
        """Creates a SEO Friendly URL from the title"""
        _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
        result = []
        for word in _punct_re.split(text.lower()):
            word = normalize('NFKD', word).encode('ascii', 'ignore')
            if word:
                result.append(word)
        return unicode(delim.join(result))

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
    url = CharField(unique=True)
    tags = CharField()
    user = ForeignKeyField(User, related_name='entries')

    class Meta:
        database = DATABASE
        order_by = ('-title',)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry], safe=True)
