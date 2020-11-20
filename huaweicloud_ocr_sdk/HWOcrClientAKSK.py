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
import json

import requests
from apig_sdk import signer


class HWOcrClientAKSK(object):
    """
    OCR client authenticated by AK and SK

    initializd by ak,sk,endpoint

    Attributes:
        ak: Access key for the OCR user
        sk: Secret key for the OCR user
    """

    def __init__(self, ak, sk, region):
        if ak == "" or sk == "" or region == "":
            raise ValueError("The parameter for the HWOcrClientAKSK constructor cannot be empty.")
        self.endpoint = "ocr." + region + ".myhuaweicloud.com"
        self.sig = signer.Signer()
        self.sig.AppKey = ak
        self.sig.AppSecret = sk
        self.httpschema = "https"  # Only HTTPS is supported.
        self.httpmethod = "POST"  # Only POST is supported.

    def request_ocr_service_base64(self, uri, imagepath, options=None):
        """
        :param uri: URI for the HTTP request to be called
        :param imagepath: full path or URL of the image to be recognized
        :param options: optional parameter in the HTTP request of OCR
        :return:None
        """
        if imagepath == "" or uri == "":
            raise ValueError("The parameter for requestOcrServiceBase64 cannot be empty.")
        request = signer.HttpRequest()
        request.scheme = self.httpschema
        request.host = self.endpoint
        request.method = self.httpmethod
        request.uri = uri
        request.headers = {"Content-Type": "application/json"}

        body = {}
        if "http://" in imagepath or "https://" in imagepath:
            body["url"] = imagepath
        else:
            with open(imagepath, "rb") as f:
                img = f.read()
            img_base64 = base64.b64encode(img).decode("utf-8")
            body["image"] = img_base64
        if options:
            body.update(options)
        request.body = json.dumps(body)
        self.sig.Sign(request)
        url = self.httpschema + "://" + self.endpoint + uri
        response = requests.post(url, data=request.body, headers=request.headers)
        return response
