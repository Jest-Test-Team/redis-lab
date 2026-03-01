# import os
# from jupyter_server.auth import passwd

# password = os.environ.get("JUPYTER_PASSWORD")
# if password:
#     hash = passwd(password)
#     jupyter_config_dir = "/home/jovyan/.jupyter"
#     os.makedirs(jupyter_config_dir, exist_ok=True)
#     with open(os.path.join(jupyter_config_dir, "jupyter_server_config.py"), "w") as f:
#         f.write(f"c.ServerApp.password = u'{hash}'\n")

