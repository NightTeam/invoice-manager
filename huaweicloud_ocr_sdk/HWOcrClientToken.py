# -*- coding:utf-8 -*-
# Copyright 2018 Huawei Technologies Co.,Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License.  You may obtain a copy of the
# License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations under the License.

import base64
import time

import requests


class HWOcrClientToken(object):
    """
    OCR client authenticated by token

    initializd by username,domainname,passwrod,region

    Attributes:
        domainname: domain name for the OCR user. If not IAM user, it's the same as username
        password: password for the OCR user
        region: region name for the OCR user, such as cn-north-1,cn-east-2
        httpendpoint: HTTP endpoint for the OCR request
        token: temporary authentication key for the OCR user, which will expire after 24 hours
    """

    def __init__(self, domain_name, username, password, region):
        """
        Constructor for the HWOcrClientToken
        """
        if domain_name == "" or username == "" or password == "" or region == "":
            raise ValueError("The parameter for the HWOcrClientToken constructor cannot be empty.")
        self.domainname = domain_name
        self.username = username
        self.password = password
        self.region = region
        self.httpendpoint = "ocr." + region + ".myhuaweicloud.com"
        self.token = None

        self.refreshCount = 0
        self._RETRY_TIMES = 3
        self._POLLING_INTERVAL = 2.0

    def get_token(self):
        """
        Obtain the token for the OCR user from the IAM server
        :return:
        """
        if self.token is not None:
            return
        retry_times = 0
        endpoint = "iam.%s.myhuaweicloud.com" % self.region
        url = "https://%s/v3/auth/tokens" % endpoint
        headers = {"Content-Type": "application/json"}
        payload = {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "name": self.username,
                            "password": self.password,
                            "domain": {
                                "name": self.domainname
                            }
                        }
                    }
                },
                "scope": {
                    "project": {
                        "name": self.region  # region name
                    }
                }
            }
        }
        try:
            while True:
                response = requests.post(url, json=payload, headers=headers, verify=False)
                if 201 != response.status_code:
                    if retry_times < self._RETRY_TIMES:
                        retry_times += 1
                        print("Obtain the token again.")
                        time.sleep(self._POLLING_INTERVAL)
                        self.token = None
                        continue
                    else:
                        print("Failed to obtain the token.")
                        print(response.text)
                        self.token = None
                        return
                else:
                    print("Token obtained successfully.")
                    token = response.headers.get("X-Subject-Token", "")
                    self.token = token
                    return
        except Exception as e:
            print(e)
            print("Invalid token request.")

    def refresh_token(self):
        """
        Refresh the attribute token
        :return:None
        """
        print("The token expires and needs to be refreshed.")
        self.token = None
        self.get_token()

    def request_ocr_service_base64(self, uri, image_data, options=None):
        if not image_data or uri == "":
            raise ValueError("The parameter for request_ocr_service_base64 cannot be empty.")
        self.get_token()
        if self.token is not None:
            try:
                url = "https://" + self.httpendpoint + uri
                headers = {
                    "Content-Type": "application/json",
                    "X-Auth-Token": self.token
                }

                payload = {}
                image_base64 = base64.b64encode(image_data).decode("utf-8")
                payload["image"] = image_base64
                if options:
                    payload.update(options)
                response = requests.post(url, json=payload, headers=headers)
                if 401 == response.status_code and ("The token expires." in response.text):
                    # The token expires and needs to be refreshed.
                    self.refresh_token()
                    return self.request_ocr_service_base64(uri, image_data, options)

                elif 403 == response.status_code and ("The authentication token is abnormal." in response.text):
                    # The token expires and needs to be refreshed.
                    self.refresh_token()
                    return self.request_ocr_service_base64(uri, image_data, options)

                return response
            except Exception as e:
                print(e)
                return None
        return None
