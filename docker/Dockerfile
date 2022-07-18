FROM python:3.8-buster
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
VOLUME [ "/data" ]
ENTRYPOINT ["python", "./preprocess.py"]
CMD ["--url","https://www.sec.gov/forms", "--folder_path", "."]