from __future__ import absolute_import

import logging
import os
import boto3
import string

from botocore.client import ClientError
from sentry_plugins.base import CorePluginMixin
from sentry.plugins.bases.data_forwarding import DataForwardingPlugin
from sentry.utils import json, metrics
from sentry.exceptions import PluginError

logger = logging.getLogger(__name__)


class AmazonSNSPlugin(CorePluginMixin, DataForwardingPlugin):
    title = "Amazon SNS"
    slug = "amazon-sns"
    description = "Forward Sentry events to Amazon SNS (SMS messaging)"
    conf_key = "amazon-sns"

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
                "name": "region",
                "label": "AWS aws_region",
                "type": "text",
                "placeholder": "eu-west-1",
                "required": True,
            },
            {
                "name": "sender_name",
                "label": "Sender_name",
                "type": "text",
                "default": "SentrySNS",
                "help": "Name of sender, length should be MAX 11 characters!",
            },
        ]

    # Use get_rate_limit from parent class
    def get_rate_limit(self):
        limit = os.environ.get('SNS_RATELIMIT', 10)
        logger.info(
            'sentryflo.amazon_sns.get_rate_limit_call',
            extra={
                "limit_per_minute": limit,
            },
        )
        return (limit, 1)

    def forward_event(self, event, payload):
        logger.info(
            'sentryflo.amazon_sns.forward_event_call',
            extra={
                "project_id": event.project.id,
            },
        )

        secret_key_id = os.environ.get('SNS_SECRET_KEY_ID')
        secret_key = os.environ.get('SNS_SECRET_KEY')
        topic_arn = self.get_option("topic_arn", event.project)
        region = self.get_option("region", event.project)
        sender_name = self.get_option("sender_name", event.project)

        if not all((region, secret_key_id, secret_key, sender_name, topic_arn)):
            logger.error(
                'sentryflo.amazon_sns.config_settings_failed',
                extra={
                    "project_id": event.project.id,
                },
            )
            return

        ## Forward only message since it's not good approach to send all event via sms
        ## SMS limited to 160 characters long
        if len(payload['message']) > 160:
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
                region_name=region,
            )

            client.set_sms_attributes(
                attributes={
                        'DefaultSenderID': sender_name,
                        'DefaultSMSType': 'Promotional'
                }
            )

            client.publish(
                    Message=payload['message'],
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

        logger.info(
            'sentryflo.amazon_sns.forward_event_success',
            extra={
                "project_id": event.project.id,
            },
        )
        return True



