
from flask_migrate import MigrateCommand
from flask_script import Manager
from app import app, db

# Initialize the Manager
manager = Manager(app)

# Add the 'db' command to the manager
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
