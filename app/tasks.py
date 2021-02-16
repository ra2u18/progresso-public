import time
import sys
import json

from flask import render_template

from app import create_app

from rq import get_current_job
from app import db
from app.models import Task

from app.models import User, ProjectPortfolio, Report
from app.email import send_mail

app = create_app()
app.app_context().push()

def _set_task_progress(progress):
    job = get_current_job()
    print(job)
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        
        if progress >= 100:
            task.completed = True

        db.session.commit()

''' Why do we wrap the code in try/except? '''
''' This is because the export_posts function is run in a different process.
    It is not bound to the main application, i.e. Flask which chatches errors by default.
    In case of errors, the separate process controlled by RQ, not flask, will abort the task.
    Unless you are watching the output of the RQ worker or logging it to a file, you will never find out
    there was an error.
'''
def export_posts(user_id):
    try:
        user = User.query.get(user_id)
        _set_task_progress(0)
        data = []
        i = 0
        total_posts = user.projects_portfolio.count()
        for post in user.projects_portfolio.order_by(ProjectPortfolio.timestamp.asc()):
            data.append({'body': post.title_bg, 'timestamp': post.timestamp.isoformat() + 'Z'})
            time.sleep(5)
            i += 1
            _set_task_progress(100 * i // total_posts)

        send_mail('[Progresso Nel Edilizia] Postarile tale', recipients=app.config['ADMINS'],
            text_body=render_template('email/export_posts.txt', user=user, what='rapoartele'),
            html_body=render_template('email/export_posts.html', user=user, what='rapoartele'),
            attachments=[('posts.json', 'application/json',
                    json.dumps({'posts': data}, indent=4))],
            sync=True)
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)        

def export_reports(user_id):
    try:
        user = User.query.get(user_id)
        reports_query = Report.query.order_by(Report.timestamp.desc())
        _set_task_progress(0)
        data = []
        i = 0
        total_posts = reports_query.count()

        for report in reports_query.all():
            data.append({
                'employee_id': report.employee.id,
                'employee_name': report.employee.name,
                'report_observation': report.observations,
                'report_timestamp': report.timestamp.strftime('%d/%m/%Y %H:%M'),
                'report_checkin': 'Prezent' if report.check_in else 'Absent',
            })
            time.sleep(1)
            i += 1
            _set_task_progress(100 * i // total_posts)
        
        send_mail('[Progresso Nel Edilizia] Rapoartele tale', recipients=app.config['ADMINS'],
            text_body=render_template('email/export_posts.txt', user=user, what='rapoartele'),
            html_body=render_template('email/export_posts.html', user=user, what='rapoartele'),
            attachments=[('posts.json', 'application/json',
                    json.dumps({'posts': data}, indent=4))],
            sync=True)
    except: 
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    _set_task_progress(100)