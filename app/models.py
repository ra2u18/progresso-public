from app import db, login_manager
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app

import rq
import redis

# Decorated function that takes user id as argument
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # author backref for project portfolio
    projects_portfolio = db.relationship('ProjectPortfolio', backref='author', lazy='dynamic')
    # user backref for tasks
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    ''' Representation function of User. '''
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    ''' Set hashed password. '''
    def set_password(self, password):
        self.password = generate_password_hash(password)

    ''' Check hashed password. '''
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    ''' Submitting a task to the RQ, along with adding it to the database. '''
    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id, *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description, user=self)
        db.session.add(task)

        return task
    
    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, completed=False).all()
    
    def get_task_in_progress(self, name):
        return Task.query.filter_by(user=self, name=name, completed=False).first()

class ProjectPortfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    badges_id = db.Column(db.Integer, db.ForeignKey('badge.id'))
    
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Change predefined sizes if they're too small
    title_bg = db.Column(db.String(120), nullable=False)
    description_bg = db.Column(db.String(240), nullable=False)
    title_intro = db.Column(db.String(120), nullable=False)
    description_intro = db.Column(db.Text(), nullable=False)
    title_end = db.Column(db.String(120))
    description_end = db.Column(db.Text())

    # Store image paths
    bg_image = db.Column(db.Text(), nullable = False)
    bg_body_images = db.Column(db.Text(), nullable = False)

    def __repr__(self):
        ''' Representation function of Post. '''
        return f"Project {self.id} written at {self.timestamp}"

    def parse_images(self):
        ''' Tokenize the images paths into a list. '''
        return self.bg_body_images.split('&')
    
    def is_carousel(self):
        ''' Checks if the post should be loaded with a carousel or normally. '''
        return True if len(self.parse_images()) > 3 else False

    def set_background_image_path(self, path):
        self.bg_image = path
    
    def set_body_image_path(self, path):
        self.bg_body_images = path
    
    def get_background_image_path(self):
        return self.bg_image

    def serialize(self):
        return {
            'id' : self.id,
            'badge_id': self.badges_id,
            'title_intro': self.title_intro,
            'description_intro': self.description_intro,
            'img_path': self.bg_image
        }

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(24), index=True, nullable=False)

    projects_portfolio = db.relationship('ProjectPortfolio', backref='category', lazy='dynamic')


    ''' Representation method of Job. '''
    def __repr__(self):
        return f"Badge {self.category} with id {self.id}."

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String(64), index=True, nullable=False)

    job = db.relationship('Employee', backref='job', lazy='dynamic')

    ''' Representation method of Job. '''
    def __repr__(self):
        return f"Job {self.job_type} with id {self.id}."


class Task(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    completed = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection = current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100

    ''' Representation method of Task. '''
    def __repr__(self):
        return f"Task {self.id} is processing {self.description}"

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    since = db.Column(db.DateTime)

    name = db.Column(db.String(64), nullable=False, index=True)
    about = db.Column(db.Text())

    report = db.relationship('Report', backref='employee', lazy='dynamic')

    ''' Representation method of Employee. '''
    def __repr__(self):
        return f"Employee {self.name} with id {self.id}"
    
    def serialize(self):
        return {
            'id' : self.id,
            'name': self.name,
            'since':  self.since.strftime('%Y/%m')
        }

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    observations = db.Column(db.Text())
    check_in = db.Column(db.Boolean, nullable=False, default=False)

    ''' Representation method of Report. '''
    def __repr__(self):
        return f"Report {self.id} of Employee {self.employee_id}"

