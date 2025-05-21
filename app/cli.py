import click
from flask.cli import with_appcontext
from app import db
from app.models.user import User, Role

@click.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin(username, email, password):
    """Create an admin user."""
    if User.query.filter_by(username=username).first():
        click.echo(f'User {username} already exists.')
        return

    user = User(
        username=username,
        email=email,
        role=Role.ADMIN,
        first_name='Admin',
        last_name='User'
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f'Created admin user: {username}') 