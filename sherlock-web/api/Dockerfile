FROM sherlock

RUN pip3 install fastapi[all]

COPY main.py /app/

WORKDIR /app/

ENTRYPOINT ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000", "--reload"]