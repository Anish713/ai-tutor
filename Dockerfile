# docker build -t anishest2020/ai_tutor_ui:v1.2 .

FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT [ "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0" ]



# docker build -t anishest2020/ollama_phi3_gsm8k:v1.0 .
# docker buildx build --progress=plain -t anishest2020/ollama_phi3_gsm8k:v1.0 .
#  docker push anishest2020/ollama_phi3_gsm8k:v1.0


#### OLLAMA SETUP
# FROM ollama/ollama

# COPY ./run-ollama.sh /tmp/run-ollama.sh

# WORKDIR /tmp

# RUN chmod +x run-ollama.sh \
#     && ./run-ollama.sh

# EXPOSE 11434