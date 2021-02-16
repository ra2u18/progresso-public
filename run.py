from app import create_app

app = create_app()

if __name__ == '__main__':
    app.debug = True
    app.run()

from app.models import User, ProjectPortfolio, Badge, Task, Employee, Job, Report
from app import db

''' Populate the flask shell with usual imports. ''' 
@app.shell_context_processor
def make_shell_context():
    return { 'db': db, 'User': User, 'ProjectPortfolio': ProjectPortfolio, 
    'Badge': Badge, 'Task': Task, 'Employee': Employee, 'Job': Job, 'Report': Report }

    