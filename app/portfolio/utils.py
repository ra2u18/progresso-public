import os, shutil
import string
import random

from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app

''' Encode multiple images in a single string for the database. '''
def list_to_string(image_paths):
    return '&'.join(image_paths)

'''Creates a random string of alphanumeric characters.'''
def randstr():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) \
                for _ in range(16))

def upload(images, output_size, is_background):
    
    project_paths = []

    # We received a carousel request.
    if len(images) > 3:
        output_size = (1740,900)

    for image in images:
        safe_filename = secure_filename(randstr() + image.filename)
        image_path = os.path.join(current_app.root_path, current_app.config['IMAGE_DIR'])

        with Image.open(image) as i:
            i = Image.open(image)
            
            # If the image is for background, create multiple sizes.
            if is_background:
                img_1920_1920 = i.resize((1920, 1920), Image.LANCZOS)
                img_400_400 = i.resize((800, 533), Image.LANCZOS)

                img_1920_1920.save( os.path.join(image_path, '1920_1920/', safe_filename), optimize=True, quality=85)
                img_400_400.save( os.path.join(image_path, '800_533/', safe_filename), optimize=True, quality=85)

                # Add images to s3 bucket
                current_app.s3_client.upload_file(os.path.join(image_path, '1920_1920/', safe_filename), current_app.config['AWS_BUCKET_NAME'], os.path.join(current_app.config['IMAGE_DIR'], '1920_1920/', safe_filename))
                current_app.s3_client.upload_file(os.path.join(image_path, '800_533/', safe_filename), current_app.config['AWS_BUCKET_NAME'], os.path.join(current_app.config['IMAGE_DIR'], '800_533/', safe_filename))

            else:
                i = i.resize(output_size, Image.LANCZOS)
                i.save(os.path.join(image_path, safe_filename), optimize=True, quality=85)
                current_app.s3_client.upload_file(os.path.join(image_path, safe_filename), current_app.config['AWS_BUCKET_NAME'], os.path.join(current_app.config['IMAGE_DIR'], safe_filename))


        project_paths.append(safe_filename)
    
    return project_paths

''' Delete all files related to that post and free memory. '''
def delete_files_of_post(post):
    base_image_path = os.path.join(current_app.root_path, current_app.config['IMAGE_DIR'])
    bg_1920_1920 = os.path.join(base_image_path, '1920_1920/', post.get_background_image_path())
    bg_800_533 = os.path.join(base_image_path, '800_533/', post.get_background_image_path())

    if(os.path.isfile(bg_1920_1920) and os.path.isfile(bg_800_533)):
        os.remove(bg_1920_1920)
        os.remove(bg_800_533)
    else:
        app.logger.error(f'Error: {bg_1920_1920} or {bg_800_533} files not found')

    body_images = post.parse_images()
    for body_image in body_images:
        body_image_path = os.path.join(base_image_path, body_image)
        if(os.path.isfile(body_image_path)):
            os.remove(body_image_path)
        else:
            app.logger.error(f'Error: {body_image_path} file not found')

def delete_post_images_s3(post):
    image_1920_1920 = os.path.join(current_app.config['IMAGE_DIR'], '1920_1920/', post.get_background_image_path())
    image_900_533 = os.path.join(current_app.config['IMAGE_DIR'], '800_533/', post.get_background_image_path())
    
    current_app.s3_client.delete_object(Bucket='progressoneledilizia', Key=image_1920_1920)
    current_app.s3_client.delete_object(Bucket='progressoneledilizia', Key=image_900_533)

    body_images = post.parse_images()
    for body_image in body_images:
        body_image_fullpath = os.path.join(current_app.config['IMAGE_DIR'], body_image)
        current_app.s3_client.delete_object(Bucket='progressoneledilizia', Key=body_image_fullpath)


def uploade_carousel_images(images):
    output_size = (1740,900)

    for image in images:
        safe_filename = secure_filename(randstr() + image.filename)
        image_path = os.path.join(current_app.root_path, current_app.config['GENERAL_IMAGES_PATH'])

        with Image.open(image) as i:
            i = Image.open(image)
            
            i = i.resize(output_size, Image.LANCZOS)
            i.save(os.path.join(image_path, safe_filename), optimize=True, quality=85)

''' Delete all files related to that post and free memory. '''
def delete_carousel_images():
    deleted = False
    folder = os.path.join(current_app.root_path, current_app.config['GENERAL_IMAGES_PATH'])

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                deleted = True
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                deleted = True
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
            deleted = False
    
    return deleted

''' Search for metallic structure images and returns path of the images. '''
def search_carousel_paths():
    paths = []
    folder = os.path.join(current_app.root_path, current_app.config['GENERAL_IMAGES_PATH'])

    paths = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    return paths