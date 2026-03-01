FROM jupyter/datascience-notebook:python-3.11

# Force upgrade to latest JupyterLab
RUN pip install jupyterlab==4.2.5

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
