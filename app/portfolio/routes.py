import json

from app import db
from flask import render_template, url_for, flash, redirect, request, current_app, jsonify
from flask_login import current_user

from app.portfolio import bp
from app.portfolio.utils import list_to_string, upload, delete_files_of_post, delete_post_images_s3

from app.portfolio.forms import ProjectPortfolioForm
from app.models import ProjectPortfolio, Badge

from flask_login import login_required

current_page = None

output_img_bg = (1920, 1920)
output_img_body = (800, 1000)

''' Homepage of the portfolio blueprint. '''
@bp.route('/proiecte-firma-de-constructii', methods=['GET', 'POST'])
def home():
    return render_template('projects.html', title="Proiectele Noastre")

''' Route of dynamically generated post. '''
@bp.route('/proiecte/postare/<post_id>')
def post(post_id):
    project = ProjectPortfolio.query.get(post_id)
    
    images = {
        'background_image': project.get_background_image_path(),
        'body_images': project.parse_images(),
        'carousel': project.is_carousel()
    }

    return render_template('post.html', title=f'Proiectul {post_id}', project=project, images=images)

''' Ajax path for filtering between project Categories. '''
@bp.route('/search_pill', methods=['POST'])
def search_pill():
    category = request.form['category']
    current_page = int(request.form['current_page'])
    
    if category == '':
        project_filtered = ProjectPortfolio.query.paginate(current_page, current_app.config['POSTS_PER_PILL'], False)
    else:    
        project_filtered = ProjectPortfolio.query.join(Badge).filter(Badge.category == category) \
                .paginate(current_page, current_app.config['POSTS_PER_PILL'], False)

    project_list = project_filtered.items
    page_has_next = project_filtered.has_next
    page_has_prev = project_filtered.has_prev

    return jsonify(result = [p.serialize() for p in project_list], has_next = page_has_next, has_prev = page_has_prev)

''' Pagination of the different project Categories. '''
@bp.route('/pill_paginate', methods=['POST'])
def pill_paginate():

    direction = request.form['direction']
    current_page = int(request.form['current_page'])
    category = request.form['category']

    if direction == 'next':
        current_page = current_page + 1
    elif direction == 'prev' and (current_page - 1) > 0:
        current_page = current_page - 1
    else: 
        return jsonify(result = [], current_page = current_page)

    if category == '':
        page = ProjectPortfolio.query.paginate(current_page, current_app.config['POSTS_PER_PILL'], False)
    else:
        page = ProjectPortfolio.query.join(Badge).filter(Badge.category == category) \
                    .paginate(current_page, current_app.config['POSTS_PER_PILL'], False)

    page_posts = page.items
    page_has_next = page.has_next
    page_has_prev = page.has_prev

    if page_posts:
        print('Page has items')
        return jsonify(result = [p.serialize() for p in page_posts], current_page = current_page, has_next = page_has_next, has_prev = page_has_prev)
    else:
        print('Page doesn\'t have items')
        current_page = current_page - 1 if direction == 'next' else current_page + 1
        return jsonify(result = [], current_page = current_page, has_next = page_has_next, has_prev = page_has_prev)

@bp.route('/create_post', methods=['GET','POST'])
@login_required
def create_post():
    form = ProjectPortfolioForm()
    form.badges.choices = [(badge.id, badge.category) for badge in Badge.query.order_by('category')]

    if request.method == 'POST' and current_user.is_authenticated:

        if form.validate_on_submit():
            # Handle images request
            images = request.files.getlist('images')
            project_bg = request.files.getlist('project_bg')

            project_bg_path = ''.join(upload(project_bg, output_img_bg, True))
            project_image_paths = upload(images, output_img_body, False)

            # Get string out of all paths
            db_project_image_path = list_to_string(project_image_paths)

            # Rest of the form
            title_bg = form.title_bg.data
            description_bg = form.description_bg.data
            title_intro = form.title_intro.data
            description_intro = form.description_intro.data
            title_end = form.title_end.data
            description_end = form.description_end.data
            choice = form.badges.data

            category = Badge.query.get(choice)

            project = ProjectPortfolio(title_bg=title_bg, description_bg=description_bg, \
                title_intro=title_intro, title_end=title_end, \
                description_end = description_end, description_intro = description_intro, \
                category = category, author = current_user)
            
            project.set_background_image_path(project_bg_path)
            project.set_body_image_path(db_project_image_path)
            
            db.session.add(project)
            db.session.commit()

            flash(f'You have posted successfuly', 'success')

            return redirect(url_for('portfolio.post', post_id=project.id))

    return render_template('create-post.html', form=form, legend='Creeaza Postare')

''' Upload post information to the database '''
@bp.route('/delete_post/<post_id>')
@login_required
def delete_post(post_id):
    post = ProjectPortfolio.query.get_or_404(post_id)
    
    delete_files_of_post(post)
    
    db.session.delete(post)
    db.session.commit()
    
    delete_post_images_s3(post)

    flash(f'Post deleted successfuly!', 'success')

    return redirect(url_for('portfolio.home'))

''' Upload post information to the database '''
@bp.route('/edit_post/<post_id>', methods=['GET','POST'])
@login_required
def edit_post(post_id):
    post = ProjectPortfolio.query.get_or_404(post_id)
    form = ProjectPortfolioForm()

    if request.method == 'POST':
        if form.validate_on_submit:
            post.title_bg = form.title_bg.data
            post.description_bg = form.description_bg.data
            post.title_intro = form.title_intro.data
            post.description_intro = form.description_intro.data
            post.title_end = form.title_end.data
            post.description_end = form.description_end.data
            choice = form.badges.data

            category = Badge.query.get(choice)
            post.category = category

            db.session.commit()

            flash('Ai editat postarea cu success', 'success')

            return redirect(url_for('portfolio.post', post_id=post.id))
    elif request.method == 'GET':
        form.title_bg.data = post.title_bg
        form.description_bg.data = post.description_bg
        form.title_intro.data = post.title_intro
        form.description_intro.data = post.description_intro
        form.title_end.data = post.title_end
        form.description_end.data = post.description_end
        form.badges.choices = [(badge.id, badge.category) for badge in Badge.query.order_by('category')]

    return render_template('create-post.html', form=form, legend='Editeaza Postarea', is_edit=True)
