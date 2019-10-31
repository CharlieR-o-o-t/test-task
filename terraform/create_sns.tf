
	provider "aws" {
		profile	= "default"
		region	= var.aws_region
	}

	data "aws_sns_topic" "new_sns" {
		name = var.sns_topic_name
		depends_on = [
			aws_sns_topic.new_sns,
		]
	}

	resource "aws_sns_topic" "new_sns" {
		name = var.sns_topic_name
	}

# TODO: Invalid argument, responce = 400
#	resource "aws_sns_sms_preferences" "new_sns_pref" {
#		monthly_spend_limit = "10"
#	}

	resource "aws_sns_topic_subscription" "add_new_sns_target" {
		for_each = toset(var.phone_numbers)
		topic_arn = data.aws_sns_topic.new_sns.arn
		protocol  = "sms"
		endpoint = "${each.value}"
	}