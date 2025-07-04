#!/usr/bin/env python3

# /// script
# dependencies = [
#  
# ]
# ///

from typing import Union, Dict, Any, Optional
import requests
from prefect import task, flow
from prefect.logging import get_run_logger
import time
import subprocess


@task(retries=0, log_prints=True)
def run_rpa_challenge():
    subprocess.run(["rcc", "run", "-t", "CookingWithGas"], check=True)

# @task(retries=0, log_prints=True)
# def runProducer():
#     subprocess.run(["rcc", "runTask", "-T", "producer"], check=True)

# @task(retries=0, log_prints=True)
# def runConsumer():
#     """Insert consumer logic here"""
#     subprocess.run(["rcc", "runTask", "-T", "consumer"], check=True)

@flow(name="rpaservicesflow", log_prints=True)
def rpaservicesflow():
    """
    Flow that handles the RPA challenge
    """
    logger = get_run_logger()
    run_rpa_challenge()


if __name__ == "__main__":
    rpaservicesflow()
