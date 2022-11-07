# Copyright 2022 Cartesi Pte. Ltd.
#
# SPDX-License-Identifier: Apache-2.0
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from os import environ
import sqlite3
import traceback
import logging
import requests
import datasets_sqlite
import json

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)
my_class = datasets_sqlite.Myclass()

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

def hex2str(hex):
    return bytes.fromhex(hex[2:]).decode("utf-8")

def str2hex(str):
    return "0x" + str.encode("utf-8").hex()

def handle_advance(data):
    logger.info(f"Received advance request data {data}")

    status = "accept"
    try:
        #logger.info("Adding notice")
        #response = requests.post(rollup_server + "/notice", json={"payload": data["payload"]})
        #logger.info(f"Received notice status {response.status_code} body {response.content}")
        my_class.advance(data,rollup_server,hex2str,str2hex)

    except Exception as e:
        status = "reject"
        msg = f"Error processing data {data}\n{traceback.format_exc()}"
        logger.error(msg)
        response = requests.post(rollup_server + "/report", json={"payload": str2hex(msg)})
        logger.info(f"Received report status {response.status_code} body {response.content}")

    return status

def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    try:
        statement = hex2str(data["payload"])
        logger.info(f"Received statement: '{statement}'")

        try:
            con = sqlite3.connect("data.db")
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS Medical (age INT, sex TEXT, bmi REAL, children INT, smoker TEXT, region TEXT, charges REAL)")
        except Exception as e:
            msg = f"Critical error connecting to database: {e}"
            logger.error(msg)
            requests.post(rollup_server + "/exception", json={"payload": str2hex(msg)})
            sys.exit(1)

        result = None
        status = "accept"

        try:
            cur.execute(statement)
            result = cur.fetchall()

        except Exception as e:
            status = "reject"
            msg = f"Error executing statement '{statement}': {e}"
            logger.error(msg)
            response = requests.post(rollup_server + "/report", json={"payload": str2hex(msg)})
            logger.info(f"Received report status {response.status_code} body {response.content}")

        finally:
            con.commit()
            con.close()
        
        if (result):
            payloadJson = json.dumps(result)
            payload = str2hex(payloadJson)
            logger.info(f"Adding report with payload: {payloadJson}")
            response = requests.post(rollup_server + "/report", json={"payload": payload})
            logger.info(f"Received notice status {response.status_code}")
    
    except Exception as e:
        status = "reject"
        msg = f"Error processing data {data}\n{traceback.format_exc()}"
        logger.error(msg)
        response = requests.post(rollup_server + "/report", json={"payload": str2hex(msg)})
        logger.info(f"Received report status {response.status_code} body {response.content}")

    return status

handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}
rollup_address = None

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        # metadata = rollup_request["data"]["metadata"]
        # if metadata["epoch_index"] == 0 and metadata["input_index"] == 0:
        if rollup_request["data"].get("metadata") and rollup_request["data"]["metadata"]["epoch_index"] == 0 and rollup_request["data"]["metadata"]["input_index"] == 0:
            rollup_address = rollup_request["data"]["metadata"]["msg_sender"]
            logger.info(f"Captured rollup address: {rollup_address}")
        else:
            handler = handlers[rollup_request["request_type"]]
            finish["status"] = handler(rollup_request["data"])
