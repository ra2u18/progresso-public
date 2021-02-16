from flask import Blueprint

bp = Blueprint('portfolio', __name__)

from app.portfolio import routes