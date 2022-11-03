FROM python:3.9.5
WORKDIR /python
COPY ./python/requirements.txt requirements.txt
COPY ../ML_models ML_models
RUN pip3 install -r requirements.txt
COPY /python .
CMD [ "python3", "model_training.py"]