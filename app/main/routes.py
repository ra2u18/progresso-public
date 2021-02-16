from flask import render_template, request, current_app, flash, redirect, url_for

from flask_mail import Message
from flask_login import login_required, current_user
from app import mail, db

from app.models import ProjectPortfolio, Badge
from app.main.forms import ContactForm

from app.email import send_awsses_mail

from app.portfolio.utils import uploade_carousel_images, delete_carousel_images, search_carousel_paths

from app.main import bp

@bp.route('/')
@bp.route('/acasa')
def home():
    constr_recent = ProjectPortfolio.query.join(Badge).filter(Badge.category == 'Constructii') \
                .order_by(ProjectPortfolio.timestamp.desc()).first()
    instal_recent = ProjectPortfolio.query.join(Badge).filter(Badge.category == 'Instalatii') \
                .order_by(ProjectPortfolio.timestamp.desc()).first()
    elec_recent =  ProjectPortfolio.query.join(Badge).filter(Badge.category == 'Constructii') \
                .order_by(ProjectPortfolio.timestamp.desc()).all()

    elec_recent_elet = None
    if len(elec_recent) >= 2:
        elec_recent_elet = elec_recent[1]

    return render_template('home.html', constr_recent=constr_recent, instal_recent=instal_recent, elec_recent=elec_recent_elet)

@bp.route('/despre-noi')
def about():
    return render_template('about.html', title='Despre Noi')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if request.method == 'POST':
        if form.validate_on_submit():

            data = {
                'name': form.name.data,
                'phone': form.phone.data,
                'email': form.email.data.strip(),
                'message': form.message.data
            }

            send_awsses_mail(subject='Formular de contact', text_body=f'{form.name.data} says {form.message.data}', 
                    html_body=render_template('flask-mail.html', data=data))

            flash(f'You sent the message successfully', 'success')
            return redirect(url_for('main.contact'))

    return render_template('contact.html', title='Contacteaza-ne', form=form)

def process_carousel(images_request_path, home):
    images = request.files.getlist(images_request_path)
    uploade_carousel_images(images)
    flash(f'Ati uploadat imaginile cu succes', 'success')
    return redirect(url_for(home))

def unprocess_carousel():
    if current_user.is_authenticated:
        deleted = delete_carousel_images()
        if deleted:
            flash('Ai sters pozele cu succes', 'success')
        else:
            flash('Nu s-au putut sterge pozele', 'danger')

@bp.route('/servicii-firma-de-constructii', methods=['POST','GET'])
def construction():
    ''' Set carousel route to be able to update, delete, edit carousel images. '''
    current_app.config['GENERAL_IMAGES_PATH'] = 'static/assets/images/general/construction/carousel/'

    if request.method == 'POST' and current_user.is_authenticated:
        process_carousel('images-construction', 'main.construction')

    paths = search_carousel_paths()
    return render_template('construction.html', title='Constructii', paths=paths)


@bp.route('/servicii/hale-metalice', methods=['POST', 'GET'])
def metallic_structures():
    ''' Set carousel route to be able to update, delete, edit carousel images. '''
    current_app.config['GENERAL_IMAGES_PATH'] = 'static/assets/images/general/metallic-structures/carousel/'

    if request.method == 'POST' and current_user.is_authenticated:
        process_carousel('images-metallic-structures', 'main.metallic-structures')
    
    paths = search_carousel_paths()
    return render_template('metallic-structures.html', title='Hale Metalice', paths=paths)

@bp.route('/servicii/instalatii', methods=['POST','GET'])
def installation():
    ''' Set carousel route to be able to update, delete, edit carousel images. '''
    current_app.config['GENERAL_IMAGES_PATH'] = 'static/assets/images/general/installation/carousel/'

    if request.method == 'POST' and current_user.is_authenticated:
        process_carousel('images-installation', 'main.installation')
    
    paths = search_carousel_paths()
    return render_template('installation.html', title='Instalatii si Termoficare', paths=paths)

@bp.route('/servicii/cladiri-social-culturale', methods=['POST','GET'])
def buildings():
    return render_template('buildings.html', title='Constructii cladiri social-culturale')

@bp.route('/servici/hale-metalice/delete-images')
def delete_metallic_carousel():
    unprocess_carousel()
    return redirect(url_for('main.metallic_structures'))

@bp.route('/servici/instalatii/delete-images')
def delete_installation_carousel():
    unprocess_carousel()
    return redirect(url_for('main.installation'))

@bp.route('/servici/constructii/delete-images')
def delete_construction_carousel():
    unprocess_carousel()
    return redirect(url_for('main.construction'))

@bp.route('/export_posts')
@login_required
def export_posts():
    # if current_user.get_task_in_progress('export_posts'):
    #     flash('An export task is currently in progress')
    # else:
    #     current_user.launch_task('export_posts', 'Exporting posts...')
    #     db.session.commit()
    print('someone pressed export_posts')
    return redirect(url_for('main.home'))

@bp.route('/export_reports')
@login_required
def export_reports():
    # if current_user.get_task_in_progress('export_reports'):
    #     flash('An export task is currently in progress')
    # else:
    #     current_user.launch_task('export_reports', 'Exporting reports...')
    #     db.session.commit()
    print('someone pressed export_reports')
    return redirect(url_for('main.home'))
