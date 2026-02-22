FROM python:3.14-alpine

WORKDIR /app
COPY src/requirements.txt ./
COPY src/main.py ./
COPY src/templates/* ./templates/

RUN pip install -r requirements.txt && rm requirements.txt

ENV JF_ADDRESS=NONE
ENV JF_API_KEY=NONE
CMD [ "fastapi", "run", "main.py", "--host", "0.0.0.0" ]
