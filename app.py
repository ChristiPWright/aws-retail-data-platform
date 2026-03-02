#!/usr/bin/env python3
import os
from aws_cdk import App
from cdk.stacks.foundation_stack import FoundationStack

app = App()

FoundationStack(
    app,
    os.getenv('ENV_NAME', 'dev'),
    env=app.node.try_get_context("env"),  # account/region from profile or context -> TODO explict env to fallback cli account
)

app.synth()