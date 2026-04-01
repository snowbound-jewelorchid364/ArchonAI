from __future__ import annotations
import pytest


_TF_CONTENT = """
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
}

resource "aws_lambda_function" "handler" {
  function_name = "my-handler"
  runtime       = "python3.11"
}

variable "region" {
  default = "us-east-1"
}

output "bucket_name" {
  value = aws_s3_bucket.data.bucket
}
"""

_CFN_CONTENT = """
AWSTemplateFormatVersion: "2010-09-09"
Description: Sample CloudFormation template
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-func
"""


@pytest.mark.asyncio
async def test_iac_parser_terraform():
    from archon.input.iac_parser import IaCParser
    parsed = await IaCParser().parse(_TF_CONTENT)
    assert parsed.metadata["format"] == "terraform"


@pytest.mark.asyncio
async def test_iac_parser_cloudformation():
    from archon.input.iac_parser import IaCParser
    parsed = await IaCParser().parse(_CFN_CONTENT)
    assert parsed.metadata["format"] == "cloudformation"


@pytest.mark.asyncio
async def test_iac_parser_resource_count():
    from archon.input.iac_parser import IaCParser
    parsed = await IaCParser().parse(_TF_CONTENT)
    assert parsed.metadata["resource_count"] > 0
    parsed_cfn = await IaCParser().parse(_CFN_CONTENT)
    assert parsed_cfn.metadata["resource_count"] > 0
