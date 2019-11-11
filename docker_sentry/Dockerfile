FROM sentry:9.1.2

COPY bootstrap.py /bootstrap.py 

RUN pip install --no-cache-dir sentryflo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["run", "web"]
