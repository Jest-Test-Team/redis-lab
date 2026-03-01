# from jupyter_server.auth import passwd
# import os

# password = os.environ.get("JUPYTER_PASSWORD")
# if password:
#     c.ServerApp.password = passwd(password)
# else:


c.ServerApp.token = ''
c.ServerApp.password_required = False

c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False

# These fix CORS/XSRF issues
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = True
c.ServerApp.allow_remote_access = True
c.ServerApp.trust_xheaders = True
c.ServerApp.allow_credentials = True

c.LabApp.custom_css = True