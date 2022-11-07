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

# UFF Table PATERN -----------------------------------------------------------------------

# sqlite> PRAGMA table_info(medical);
# 0,age,TEXT,0,,0
# 1,sex,TEXT,0,,0
# 2,bmi,TEXT,0,,0
# 3,children,TEXT,0,,0
# 4,smoker,TEXT,0,,0
# 5,region,TEXT,0,,0
# 6,charges,TEXT,0,,0

# *bmi = kg/m² 

# This dataset consists of 1338 rows.

# more datails about the dataset ---------------------------------------------------------

# https://www.kaggle.com/datasets/mirichoi0218/insurance?select=insurance.csv

# About Dataset
# Context

# Machine Learning with R by Brett Lantz is a book that provides an introduction to machine learning using R. As far as I can tell, Packt Publishing does not make its datasets available online unless you buy the book and create a user account which can be a problem if you are checking the book out from the library or borrowing the book from a friend. All of these datasets are in the public domain but simply needed some cleaning up and recoding to match the format in the book.
# Content

# Columns

#     age: age of primary beneficiary

#     sex: insurance contractor gender, female, male

#     bmi: Body mass index, providing an understanding of body, weights that are relatively high or low relative to height,
#     objective index of body weight (kg / m ^ 2) using the ratio of height to weight, ideally 18.5 to 24.9

#     children: Number of children covered by health insurance / Number of dependents

#     smoker: Smoking

#     region: the beneficiary's residential area in the US, northeast, southeast, southwest, northwest.

#     charges: Individual medical costs billed by health insurance

# Acknowledgements

# The dataset is available on GitHub here. https://github.com/stedy/Machine-Learning-with-R-datasets
# Inspiration

# Can you accurately predict insurance costs?

from asyncio.log import logger
from os import environ

import requests
import sqlite3
import json

class Myclass():

    def advance(self,data,rollup_server,hex2str,str2hex):

        logger.info(f"Received advance request body {data}")

        # retrieves SQL statement from input payload
        statement = hex2str(data["payload"])
        #statement = data["payload"]
        logger.info(f"Received statement: '{statement}'")

        # connects to internal database
        con = sqlite3.connect("data.db")
        cur = con.cursor()

        result = None
        status = "accept"
        try:
            # attempts to execute the statement and fetch any results
            cur.execute("CREATE TABLE IF NOT EXISTS Medical (age INT, sex TEXT, bmi REAL, children INT, smoker TEXT, region TEXT, charges REAL)")
            cur.execute(statement)
            result = cur.fetchall()

        except Exception as e:
            status = "reject"
            msg = f"Error executing statement '{statement}': {e}"
            logger.error(msg)
            response = requests.post(rollup_server + "/report", json={"payload": str2hex(msg)})
            logger.info(f"Received report status {response.status_code} body {response.content}")

        finally:
            # closes connection to database
            con.commit()
            con.close()

        if (result):
            # if there is a result, converts it to JSON and posts it as a notice
            payloadJson = json.dumps(result)
            payload = str2hex(payloadJson)
            logger.info(payload)
            logger.info(f"Adding notice with payload: {payloadJson}")
            response = requests.post(rollup_server + "/notice", json={"payload": payload})
            logger.info(f"Received notice status {response.status_code} body {response.content}")



