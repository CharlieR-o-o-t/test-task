from __future__ import absolute_import

import logging

import boto3
from botocore.client import ClientError
from sentry_plugins.base import CorePluginMixin
from sentry.plugins.bases.data_forwarding import DataForwardingPlugin
from sentry_plugins.utils import get_secret_field_config
from sentry.utils import json, metrics

logger = logging.getLogger(__name__)


def get_regions():
    return boto3.session.Session().get_available_regions("sns")


class AmazonSNSPlugin(CorePluginMixin, DataForwardingPlugin):
    title = "Amazon SNS"
    slug = "amazon-sns"
    description = "Forward Sentry events to Amazon SNS (SMS messaging)"
    conf_key = "amazon-sns"
    sms_type = 'Promotional'

    def validate_config(self, project, config, actor):
        if len(config['sender_name']) > 11:
            logger.exception(six.text_type(exc))
            raise PluginError('Sentry-sns: sender name can\'t be more than 11 characters')
        return config

    def get_config(self, project, **kwargs):
        return [
            {
                "name": "topic_arn",
                "label": "AWS sns arn",
                "type": "text",
                "placeholder": "arn:aws:sns:eu-west-1:514409672635:SentyNotificationTopicAuto",
                "required": True,
            },
            {
                "name": "sender_name",
                "label": "Sender_name",
                "type": "text",
                "default": "SentrySNS",
                "help": "Name of sender, length should be MAX 11 characters!",
            },
            {
                "name": "rate_limit",
                "label": "Limit per minute",
                "type": "number",
                "default": 10,
                "help": "SMS messages limit per minute",
            },
        ]

    # Use get_rate_limit from parent class
    def get_rate_limit(self):
        # number of requests, number of seconds (window)
        return (self.get_option("rate_limit"), 1)

    def forward_event(self, event, payload):

        secret_key_id = environ.get('SECRET_KEY_ID')
        secret_key = environ.get('SECRET_KEY')
        topic_arn = self.get_option("topic_arn")
        sender_name = self.get_option("sender_name")

        if not all((access_key, secret_key, region, sender_name)):
            return

        try:
            client = boto3.client(
                service_name="sns",
                aws_access_key_id=secret_key_id,
                aws_secret_access_key=secret_key,
            )

            client.set_sms_attributes(
                attributes={
                        'DefaultSenderID': sender_name,
                        'DefaultSMSType': sms_type
                }
            )

            client.publish(
                    Message=json.dumps(message),
                    TopicArn=topic_arn,
            )
        except ClientError as e:
            if e.message.startswith("An error occurred (AccessDenied)"):
                logger.error("Sentry-sns: AccessDenied check aws key/id")

                return False
            else:
                logger.error('Sentry-sns: Failed to public event: '+ six.text_type(exc))

                return False


        return True



