import json

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
    req_uri = "/v1.0/ocr/auto-classification"
    img_path = "./data/vat-invoice-demo.jpg"  # File path or URL of the image to be recognized.
    option = {}
    option["type_list"] = ["vat_invoice", "id_card_portrait_side"]
    try:
        ocrClient = HWOcrClientToken(domain_name, username, password, region)
        response = ocrClient.request_ocr_service_base64(req_uri, img_path, option)
        print("Status code:" + str(response.status_code) + " content:" + response.text)

        # data analysis
        decode_response(response)

    except ValueError as e:
        print(e)


def aksk_request():
    """
    AK SK demo code
    """

    AK = "xxx"  # AK from authentication.
    SK = "xxx"  # SK from authentication.
    region = "cn-north-4"  # http region information.
    req_uri = "/v1.0/ocr/auto-classification"
    img_path = "./data/id-card-demo.jpg"  # File path or URL of the image to be recognized.
    option = {}
    option["type_list"] = ["vat_invoice", "id_card_portrait_side"]
    try:
        ocr_client = HWOcrClientAKSK(AK, SK, region)  # Initialize the ocr_client.
        response = ocr_client.request_ocr_service_base64(req_uri, img_path,
                                                         option)  # Call the OCR API to recognize image.
        print("Status code:" + str(response.status_code) + " content:" + response.text)

        # data analysis
        decode_response(response)

    except ValueError as e:
        print(e)


def decode_response(response):
    requestCode = response.status_code
    if requestCode == 200:
        resultDict = json.loads(response.text)
        error_code = resultDict.get("error_code", -1)
        if error_code == -1 or error_code == "AIS.0000":
            result = resultDict["result"]
            for result_item in result:
                content = result_item["content"]
                type = result_item["type"]
                if "id_card_portrait_side" == type:
                    name = content["name"]
                    sex = content["sex"]
                    ethnicity = content["ethnicity"]
                    birth = content["birth"]
                    address = content["address"]
                    number = content["number"]
                    print("type = " + type + "\nname = " + name + "\nsex = " + sex + "\nethnicity = " + ethnicity +
                          "\nbirth = " + birth + "\naddress = " + address + "\nnumber = " + number)
                elif "vat_invoice" == type:
                    serial_number = content["serial_number"]
                    attribution = content["attribution"]
                    code = content["code"]
                    check_code = content["check_code"]
                    machine_number = content["machine_number"]
                    print_number = content["print_number"]
                    number = content["number"]
                    issue_date = content["issue_date"]
                    encryption_block = content["encryption_block"]
                    buyer_name = content["buyer_name"]
                    buyer_id = content["buyer_id"]
                    buyer_address = content["buyer_address"]
                    buyer_bank = content["buyer_bank"]
                    seller_name = content["seller_name"]
                    seller_id = content["seller_id"]
                    seller_address = content["seller_address"]
                    seller_bank = content["seller_bank"]
                    subtotal_amount = content["subtotal_amount"]
                    subtotal_tax = content["subtotal_tax"]
                    total = content["total"]
                    total_in_words = content["total_in_words"]
                    remarks = content["remarks"]
                    receiver = content["receiver"]
                    reviewer = content["reviewer"]
                    issuer = content["issuer"]

                    supervision_seal = content["supervision_seal"]
                    seller_seal = content["seller_seal"]
                    item_list = content["item_list"]
                    print("type = " + type + "\nserial_number = " + serial_number + "\nattribution = " +
                          attribution + "\ncode = " + code + "\ncheck_code = " + check_code +
                          "\nmachine_number = " + machine_number + "\nnumber = " + number)
        else:
            print("Failed to request the OCR API")
    else:
        print("Failed to request the OCR API")


if __name__ == '__main__':
    token_request()
    # aksk_request()
