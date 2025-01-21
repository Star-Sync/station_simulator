FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY State_machines.py .

EXPOSE 5000

CMD ["python", "State_machines.py"]
