from flask import render_template, Blueprint

err = Blueprint('err', __name__)

@err.errorhandler(404)
def not_found_error(error):
   
   
    return render_template('404.html'), 404


@err.errorhandler(500)
def internal_error(error):
    from microblog import db
   
   
   
    db.session.rollback()
    return render_template('500.html'), 500
