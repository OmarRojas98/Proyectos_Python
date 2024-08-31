# Google Maps Web Scrapper

FastAPI docs in local environment: localhost:8000/docs

## How to use

### Local
~~~
# installation
pip install pipenv
pipenv install

# running
python ./main.py
~~~

### Docker

~~~
# image
docker build -t google-bot .

# container
docker run -d --name google-maps-bot -p 4001:4001 google-bot
~~~
