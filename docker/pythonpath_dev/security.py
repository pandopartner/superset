from flask import redirect, g, flash, request
from flask_appbuilder.security.views import UserDBModelView,AuthDBView
from superset.security import SupersetSecurityManager
from flask_appbuilder.security.views import expose
from flask_appbuilder.security.manager import BaseSecurityManager
from flask_login import login_user, logout_user
import requests as rq
from superset import db
from flask_appbuilder.security.sqla.models import User

class CustomAuthDBView(AuthDBView):
    login_template = 'appbuilder/general/security/login_db.html'

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        redirect_url = self.appbuilder.get_url_for_index
        print('arguments:', request.args)
        if request.args.get('redirect') is not None:
            redirect_url = request.args.get('redirect') 
        if request.args.get('username') is not None:
            # user needs to have been created already -- set fb id as username
            fb_user = rq.post(
                'https://conan-joxeqqr52q-uc.a.run.app/v1/graphql', 
                json={
                    'query': '''
                        query GetUserByFb($firebase_id: String = "") {
                            user(where: {firebase_id: {_eq: $firebase_id}}) {
                                firebase_id
                                id
                                org_user_bonds {
                                    org_id
                                }
                            }
                        }
                    ''',
                    'variables': {
                        'firebase_id': request.args.get('username')
                    }
                }, 
                headers={
                    'Content-Type': 'application/json', 
                    'x-hasura-admin-secret': 'myadminsecretkey' # is this secure?
                }
            ).json()
            org_id = redirect_url.split('?')[1].split('&')[0].split('=')[1]
            org_exists = next((f for f in fb_user['data']['user'][0]['org_user_bonds'] if f['org_id'] == org_id), None)
            if org_exists is None:
                print('User is not a part of this org')
                flash('You do not have access to this organization')
                return super(CustomAuthDBView,self).login()
            else:
                print('User is a part of this org - redirecting...')
                user = self.appbuilder.sm.find_user(username=org_id) # find if the user has access
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