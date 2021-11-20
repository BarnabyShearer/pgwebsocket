FROM python
ENV PYTHONUNBUFFERED=1
COPY pyproject.toml setup.cfg /src/
COPY pgwebsocket /src/pgwebsocket/
RUN SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0 python3 -m pip install /src
COPY test_app.py /src/
USER 1000
CMD /src/test_app.py
