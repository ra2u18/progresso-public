from datetime import datetime

import json

from flask import render_template, url_for, flash, redirect, Blueprint, request, jsonify, current_app
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.auth.forms import LoginForm, RegisterForm
from app.main.forms import EmployeeForm, NoCheckInForm


from app.models import User, Employee, Job, Report
from app.auth import bp

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        if request.url.startswith('http://'):
            request.url.replace('http://', 'https://', 1)
            
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or user.check_password(form.password.data):
            flash(f'Logged in successfuly!', 'success')
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('auth/login.html', title='Login', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@bp.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    reports = Report.query.order_by(Report.timestamp.desc()).paginate(1, current_app.config['POSTS_PER_PILL'], False)
    add_employee_form = EmployeeForm()
    no_checkin_form = NoCheckInForm()

    add_employee_form.job.choices = [(job.id, job.job_type) for job in Job.query.order_by('job_type')]


    if request.method == 'POST':
        if add_employee_form.validate_on_submit and add_employee_form.name.data:
            print('Employee form is submitted.')
            name = add_employee_form.name.data
            about = add_employee_form.about.data
            since = datetime.strptime(request.form['datepicker'], "%d/%m/%Y")
            choice = add_employee_form.job.data

            job = Job.query.get(choice)

            employee = Employee(name=name, about=about, since=since, job=job)

            db.session.add(employee)
            db.session.commit()

            return redirect(url_for('auth.dashboard'))
        elif no_checkin_form.validate_on_submit and no_checkin_form.observation.data:
            print('No check in happened')

    
    return render_template('dashboard.html', title='Dashboard', reports=reports.items, add_employee_form=add_employee_form, no_checkin_form=no_checkin_form)

@bp.route('/request_employees', methods=['POST', 'GET'])
@login_required
def request_employees():
    employees = Employee.query.all()
    result = []

    for e in employees:
        result.append({
            'employee': e.serialize(),
            'job': e.job.job_type
        })

    return jsonify(result = result)

@bp.route('/delete_employee', methods=['POST'])
@login_required
def delete_employee():
    id = request.form['id'].strip()

    employee = Employee.query.get_or_404(id)
    reports = Report.query.filter(Report.employee == employee).all()

    if reports:
        for report in reports:
            db.session.delete(report)
    
    db.session.delete(employee)
    db.session.commit()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@bp.route('/report_employee', methods=['POST'])
@login_required
def report_employee():
    id = request.form['id'].strip()
    observation = request.form['observation']

    print(id, observation)

    employee = Employee.query.get_or_404(id)
    report = Report(employee=employee, observations=observation,
            check_in=False)

    db.session.add(report)
    db.session.commit()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@bp.route('/checkin_employee', methods=['POST'])
@login_required
def checkin_employee():
    id = request.form['id'].strip()
    observation = 'Prezent'

    employee = Employee.query.get_or_404(id)
    report = Report(employee=employee, observations=observation,
            check_in=True)


    db.session.add(report)
    db.session.commit()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
 