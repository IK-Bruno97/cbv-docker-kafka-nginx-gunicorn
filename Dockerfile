FROM python:3.10.0a1-alpine3.12
# create directory for the app user
RUN mkdir -p /usr/src

# create the app user
RUN addgroup -S app && adduser -S app -G app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create the appropriate directories
ENV HOME=/usr/src
ENV APP_HOME=/usr/src/app
RUN mkdir $APP_HOME
WORKDIR $APP_HOME
RUN mkdir $APP_HOME/staticfiles

COPY . $APP_HOME

# install dependencies
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
#    python3 manage.py makemigrations &&\
#    python3 manage.py migrate

# copy entrypoint.sh
RUN sed -i 's/\r$//g' $APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/entrypoint.sh

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "cbv.wsgi:application"]