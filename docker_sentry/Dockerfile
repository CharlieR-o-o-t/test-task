FROM sentry:9.1.2

COPY plugin/sentryflo-0.1.dev0.tar.gz /usr/src/sentry/
COPY bootstrap.py /bootstrap.py 

RUN pip install --no-cache-dir sentryflo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["run", "web"]
