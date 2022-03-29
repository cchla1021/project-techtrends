FROM python:3.8
LABEL maintainer="Joe Chien"

COPY . /app
WORKDIR /app
RUN pip install -r ~/cchla1021/project-techtrends/techtrends/requirements.txt

#EXPOSE 3111

# command to run on container start
CMD [ "python", "init_db.py"]
CMD [ "python", "app.py" ]
