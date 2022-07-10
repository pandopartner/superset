from flask import redirect, g, flash, request
from flask_appbuilder.security.views import UserDBModelView,AuthDBView
from superset.security import SupersetSecurityManager
from flask_appbuilder.security.views import expose
from flask_appbuilder.security.manager import BaseSecurityManager
from flask_login import login_user, logout_user
import requests as rq

class CustomAuthDBView(AuthDBView):
    login_template = 'appbuilder/general/security/login_db.html'

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        redirect_url = self.appbuilder.get_url_for_index
        print('arguments:', request.args)
        if request.args.get('redirect') is not None:
            redirect_url = request.args.get('redirect') 
        # print('USERNAME!', request.args.get('username'), request.args.get('redirect'), request.args)
        if request.args.get('username') is not None:
            # user needs to have been created already -- set fb id as username
            user = self.appbuilder.sm.find_user(username=request.args.get('username')) # find if the user has access
            login_user(user, remember=False)
            print('redirecting to', redirect_url)
            return redirect(redirect_url)
        elif g.user is not None and g.user.is_authenticated:
            return redirect(redirect_url)
        else:
            flash('Unable to auto login', 'warning')
            return super(CustomAuthDBView,self).login()

class CustomSecurityManager(SupersetSecurityManager):
    authdbview = CustomAuthDBView
    def __init__(self, appbuilder):
        super(CustomSecurityManager, self).__init__(appbuilder)