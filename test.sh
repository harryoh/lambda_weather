#!/bin/bash
PYTHONPATH=packages emulambda -v weather.lambda_handler api_event.json
