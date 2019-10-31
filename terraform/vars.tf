
	variable "aws_region" {
			type = string
			description = "Aws region to use"
	}

	variable "sns_topic_name" {
			type = string
			description = "SNS topic name to use on create"
	}

	variable "sns_usd_limit" {
			type = string
			description = "Monthly USD limit to spend sending SMS"
			default = "1"
	}

	variable "sns_sender" {
			type = string
			description = "String that is displayed as the sender on the receiving device"
	}

	variable "phone_numbers" {
		description = "List of phone numbers to add to subscription"
		default = []
	}