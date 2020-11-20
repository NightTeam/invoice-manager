import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_manager.settings')
django.setup()

from wand.image import Image
from wand.color import Color
from manager.models import Invoice
from datetime import datetime
from huaweicloud_ocr_sdk.HWOcrClientToken import HWOcrClientToken
from invoice_manager.settings import IMPORT_PATH, INVOICES_PATH

username = "xxx"
password = "xxx"
domain_name = "xxx"  # If the current user is not an IAM user, the domain_name is the same as the username.
region = "cn-north-4"  # cn-north-1,cn-east-2 etc.
req_uri = "/v1.0/ocr/vat-invoice"
ocrClient = HWOcrClientToken(domain_name, username, password, region)


def ocr(invoice_path):
    option = {}
    try:
        img = Image(blob=invoice_path.read_bytes(), resolution=300)
        img.format = 'png'
        img.background_color = Color("white")
        img_bytes = img.make_blob()

        response = ocrClient.request_ocr_service_base64(req_uri, img_bytes, option)
        if response.status_code != 200:
            print("Status code:" + str(response.status_code) + "\ncontent:" + response.text)
        return response.json()["result"]
    except ValueError as e:
        print(e)


def run():
    for invoice_path in IMPORT_PATH.iterdir():
        if invoice_path.is_file() and invoice_path.suffix == ".pdf":
            invoice_data = ocr(invoice_path)
            print(invoice_data)
            invoice = Invoice(
                id=invoice_data["number"],
                description="、".join([item["name"] for item in invoice_data["item_list"]]),
                create_date=datetime.strptime(invoice_data["issue_date"], "%Y年%m月%d日"),
                company_name=invoice_data["buyer_name"],
                company_id=invoice_data["buyer_id"],
                price=float(invoice_data["total"].replace("￥", "")),
            )

            # 判断抬头和税号是否正确
            if invoice.company_id != "XXX" or invoice.company_name != "XXX":
                print(f"{invoice_path.name} 税号或税号与配置中的不符，已跳过")
                continue

            invoice.save()
            invoice_path.rename(INVOICES_PATH / f"{invoice.id}.pdf")


if __name__ == '__main__':
    run()
