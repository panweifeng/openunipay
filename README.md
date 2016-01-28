openunipay 统一支付接口 - 集成了微信、支付宝支付
=======================

为微信支付，支付宝支付提供统一接口。做到一次集成即可使用多种支付渠道

此为服务端，随后会提供Android, IOS, JS client SDK.

目前在开发阶段，请勿在生产环境中使用。

----

安装方法：
=======================
pip install openunipay

----
服务端部署：
=======================
（需要基于django 项目部署。随后会提供开箱即用的Docker Image)
此module 需要集成在django 项目中。
1, 在settings.py 里 将openunipay 添加到 install app中
INSTALLED_APPS = (
    ......
    'openunipay',
)

2, 发布 支付宝 和 微信支付支付 异步支付结果通知URL。支付成功后，支付宝和微信支付 在支付成功后会通过此URL通知支付结果
openunipay 已经提供了用于处理支付结果的django view. 你只需配置django URL 将openunipay的view 发布即可。
openuipay 提供了一下两个view
openuipay.api.views_alipay.process_notify
openuipay.api.views_weixin.process_notify

在你的url.py里
*********************************************************
from openunipay.api import views_alipay, views_weixin

urlpatterns = [
    url(r'^notify/weixin/$', views_weixin.process_notify),
    url(r'^notify/alipay/$', views_alipay.process_notify),
]
***********************************************************

3，在settings.py里添加以下配置项

#####支付宝支付配置
ALIPAY = {
        'partner':'XXX', //支付宝partner ID
        'seller_id':'XXX', //收款方支付宝账号如 pan.weifeng@live.cn
        'notify_url':'http://XXX/notify/alipay/', //支付宝异步通知接收URL
        }
#####微信支付配置
WEIXIN = {
        'app_id':'XXX', //微信APPID
        'app_seckey':'XXX', //微信APP Sec Key
        'mch_id':'XXX', //微信商户ID
        'mch_seckey':'XXX',//微信商户seckey
        'mch_notify_url':'XXX/notify/weixin/', //微信支付异步通知接收URL
        }

4, 同步数据库

python manage.py migrate --run-syncdb

----