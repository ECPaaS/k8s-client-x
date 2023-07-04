FROM python:3.11
COPY ./controller /controller
RUN pip install kopf
RUN pip install kubernetes

CMD kopf run -A /controller/handler.py

