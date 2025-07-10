FROM python:3.9

WORKDIR /code

COPY ./fastapi_project/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./fastapi_project /code

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]