FROM python:3.9

ARG HOME=/app

WORKDIR ${HOME}/
ENV PYTHONPATH ${HOME}/

COPY ./requirements.txt ${HOME}/
COPY ./requirements.dev.txt ${HOME}/

RUN pip install -r ${HOME}/requirements.txt && pip install -r ${HOME}/requirements.dev.txt

COPY . ${HOME}/

CMD ["python", "ws_assets"]