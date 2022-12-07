from flask import render_template, Blueprint

err = Blueprint('err', __name__)

@err.errorhandler(404)
def not_found_error(error):
    # Pergjigjja qe kthehet kur thirret ky template to kete HTTP Status Code 200 (qe eshte kod i ekzekutimit me sukses)
    # Prandaj duhet te kthejme http code te sakte dhe krahas renderimit te templates kthejme dhe kodin
    return render_template('404.html'), 404


@err.errorhandler(500)
def internal_error(error):
    from microblog import db
    # Error 500 kthehet kur ngrihet nje Exception dhe nje nga rastet kur ndodh eshte kur DB ka te dhena ne session
    # te cilat nuk jane ruajtur. Mire eshte qe te pastrohet session.
    # Mire eshte qe per kete error te njoftohemi sepse kemi bug ne aplikacion.
    db.session.rollback()
    return render_template('500.html'), 500
