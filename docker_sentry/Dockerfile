FROM sentry:9.1.2

COPY plugin/sentryflo-0.1.dev0.tar.gz /usr/src/sentry/

RUN pip install --no-cache-dir /usr/src/sentry/sentryflo-0.1.dev0.tar.gz

ENTRYPOINT ["/entrypoint.sh"]
CMD ["run", "web"]
