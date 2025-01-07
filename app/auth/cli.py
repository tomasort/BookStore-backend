# cli utilities for dealing with users
from flask.cli import with_appcontext
from app.auth.models import User
from app.auth import auth
import click
from app import db
from flask import current_app


@auth.cli.command(name='add-user')
@click.option('-u', '--username', help='CSV file to read book data from')
@click.option('-p', '--password', help='Size of the batch to commit to the database', default="password")
@click.option('-e', '--email', help='Size of the batch to commit to the database', default="password")
@with_appcontext
def add_user(username, password, email):
    logger = current_app.logger
    logger.info('Adding user')
    user = User(username=username, email=email)
    user.set_password(str(password))
    db.session.add(user)
    db.session.commit()
    logger.info(f'User: {user} added successfully')
    click.echo('User added successfully')
