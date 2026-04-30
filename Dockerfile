FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    "a2a-sdk[http-server]>=1.0.0" \
    "protobuf>=5.29,<6" \
    httpx \
    uvicorn \
    starlette

COPY controller.py .

ENV AGENT_HOST=0.0.0.0
ENV AGENT_PORT=9010
ENV UPSTREAM_URL=https://agentbazaar.tech/v1/invoke

EXPOSE 9010

CMD ["python", "controller.py"]
