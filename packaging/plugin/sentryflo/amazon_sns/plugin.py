from __future__ import absolute_import

import logging

import boto3
import string

from botocore.client import ClientError
from sentry_plugins.base import CorePluginMixin
from sentry.plugins.bases.data_forwarding import DataForwardingPlugin
from sentry_plugins.utils import get_secret_field_config
from sentry.utils import json, metrics
from sentry.exceptions import PluginError

logger = logging.getLogger(__name__)


class AmazonSNSPlugin(CorePluginMixin, DataForwardingPlugin):
    title = "Amazon SNS"
    slug = "amazon-sns"
    description = "Forward Sentry events to Amazon SNS (SMS messaging)"
    conf_key = "amazon-sns"
    sms_type = 'Promotional'

    def validate_config(self, project, config, actor):
        if len(config['sender_name']) > 11:
            logger.exception(
                'sentryflo.amazon_sns.sender_name_to_long',
                extra = {
                  "sender_name": config['sender_name'],
                },
            )

            raise PluginError('Sentry-sns: sender name can\'t be more than 11 characters')
        elif not config['sender_name'].isalnum():
            logger.exception(
                'sentryflo.amazon_sns.sender_name_not_alphanumeric',
                extra = {
                  "sender_name": config['sender_name'],
                },
            )

            raise PluginError('Sentry-sns: sender_name supports only alphanumeric characters')
        return config

    def get_config(self, project, **kwargs):
        logger.info(
            'sentryflo.amazon_sns.get_config_call',
            extra={
                "project_id": project.id,
            },
        )

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
        logger.info('sentryflo.amazon_sns.get_rate_limit_call')
        return (self.get_option("rate_limit"), 1)

    def forward_event(self, event, payload):
        logger.info(
            'sentryflo.amazon_sns.forward_event_call',
            extra={
                "project_id": event.project.id,
            },
        )

        secret_key_id = environ.get('SECRET_KEY_ID')
        secret_key = environ.get('SECRET_KEY')
        topic_arn = self.get_option("topic_arn")
        sender_name = self.get_option("sender_name")

        if not all((access_key, secret_key, region, sender_name)):
            logger.error(
                'sentryflo.amazon_sns.config_settings_failed',
                extra={
                    "project_id": event.project.id,
                },
            )
            return

        message = json.dumps(payload)

        if len(message) > 160:
            logger.error(
                'sentryflo.amazon_sns.message_too_long_for_sms',
                extra={
                    "project_id": event.project.id,
                    "message": "Message too long for sms review via dashboard"
                },
            )
            return False
        

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
                logger.error(
                    'sentryflo.amazon_sns.aws_access_denied',
                    extra={
                        "project_id": event.project.id,
                    },
                )

                return False
            else:
                logger.error(
                    'sentryflo.amazon_sns.public_event_failed',
                    extra={
                        "project_id": event.project.id,
                        "error": "Event forwarding failed",
                    },
                )

                return False


        return True



