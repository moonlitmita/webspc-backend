FROM python:3.11.5
LABEL maintainer="valleyfo <wynmamtf@163.com>"

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --default-timeout=300 -r requirements.txt
RUN pip install gevent
RUN pip install gunicorn[gevent]
COPY . .
EXPOSE 8000
ENV FLASK_APP=RealProject
ENV FLASK_ENV=production
ENTRYPOINT ["python"]
