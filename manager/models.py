from django.db import models


class Invoice(models.Model):
    # 发票号码（唯一ID）
    id = models.CharField(verbose_name="发票号码", primary_key=True, max_length=100)
    # 货物或应税劳务、服务名称（开票内容）
    description = models.CharField(verbose_name="开票内容", max_length=100)
    # 开票日期
    create_date = models.DateField(verbose_name="开票日期")
    # 购买方名称（公司名）
    company_name = models.CharField(verbose_name="公司名", max_length=100)
    # 购买方纳税人识别号（税号）
    company_id = models.CharField(verbose_name="税号", max_length=100)
    # 价税合计（发票金额）
    price = models.FloatField(verbose_name="发票金额")
    # 是否已使用
    used = models.BooleanField(verbose_name="已使用", default=False)

    type_transportation_fee = "交通费"
    type_dining_fee = "餐饮费"
    type_not_selected = "未选择"
    categories = [
        (type_transportation_fee, "交通费"),
        (type_dining_fee, "餐饮费"),
        (type_not_selected, "未选择"),
    ]
    # 所属类型
    category = models.CharField(
        verbose_name="发票类型",
        max_length=100,
        choices=categories,
        default=type_not_selected
    )
