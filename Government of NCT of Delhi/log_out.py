from flask import session, redirect,Blueprint

logout_bp=Blueprint('logout_bp',__name__)

@logout_bp.route('/user_logout')
def user_logout():
    session.clear()
    return redirect('/')


@logout_bp.route('/admin_logout')
def admin_logout():
    session.clear()
    return redirect('/')


@logout_bp.route('/superadmin_logout')
def sueperadmin_logout():
    session.clear()
    return redirect('/superadmin')

@logout_bp.route('/doctor_logout')
def doctor_logout():
    session.clear()
    return redirect('/')