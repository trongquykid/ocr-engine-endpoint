FROM vcr.vngcloud.vn/105622-ai-platform-nonprod/ocr-engine:v1

RUN pip3 install pandas==2.1.4 --index-url=https://nexus.msb.com.vn/repository/pypi/simple
RUN pip3 install numpy==1.26.4 --index-url=https://nexus.msb.com.vn/repository/pypi/simple

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--log-config", "log_config.json"]
