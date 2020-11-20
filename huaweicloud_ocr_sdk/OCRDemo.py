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
#
# sdk reference linking：https://support.huaweicloud.com/sdkreference-ocr/ocr_04_0016.html

from pathlib import Path

from HWOcrClientAKSK import HWOcrClientAKSK
from HWOcrClientToken import HWOcrClientToken


def token_request():
    """
    Token demo code
    """
    username = "xxx"
    password = "xxx"
    domain_name = "xxx"  # If the current user is not an IAM user, the domain_name is the same as the username.
    region = "cn-north-4"  # cn-north-1,cn-east-2 etc.
    req_uri = "/v1.0/ocr/vat-invoice"
    img_path = "./data/vat-invoice-demo.jpg"  # File path or URL of the image to be recognized.
    option = {}
    # option["side"] = "front"
    try:
        ocrClient = HWOcrClientToken(domain_name, username, password, region)
        response = ocrClient.request_ocr_service_base64(req_uri, Path(img_path).read_bytes(), option)
        print("Status code:" + str(response.status_code) + "\ncontent:" + response.text)
    except ValueError as e:
        print(e)


def aksk_request():
    """
    AK SK demo code
    """
    AK = "xxx"  # AK from authentication.
    SK = "xxx"  # SK from authentication.
    region = "cn-north-4"  # http region information.
    req_uri = "/v1.0/ocr/id-card"
    img_path = "./data/id-card-demo.jpg"  # File path or URL of the image to be recognized.
    option = {}
    # option["side"]="front"
    try:
        ocr_client = HWOcrClientAKSK(AK, SK, region)  # Initialize the ocr_client.
        response = ocr_client.request_ocr_service_base64(req_uri, img_path,
                                                         option)  # Call the OCR API to recognize image.
        print("Status code:" + str(response.status_code) + "\ncontent:" + response.text)
    except ValueError as e:
        print(e)


if __name__ == '__main__':
    token_request()
    # aksk_request()
