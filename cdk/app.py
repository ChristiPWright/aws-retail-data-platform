#!/usr/bin/env python3
from aws_cdk import App
from stacks.foundation_stack import FoundationStack
import os

app = App()

FoundationStack(
    app,
    os.getenv('ENV_NAME', 'dev'),
    env=app.node.try_get_context("env"),  # account/region from profile or context
)

app.synth()