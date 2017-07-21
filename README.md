openunipay 统一支付接口 - 集成了微信、支付宝支付
=======================

为微信支付，支付宝支付提供统一接口。做到一次集成即可使用多种支付渠道

此为服务端，随后会提供Android, IOS, JS client SDK.
目前此服务端只能集成在您自己的项目中使用。1.0版本时，会支持作为一个service发布.<br/>

[此为开发版本，生产环境使用请仔细审查代码!!!]<br/>

欢迎各位有兴趣的同学，参与维护这个开源项目！有意请联系pan.weifeng@live.cn.
=======================
欢迎赞助！支付宝: pan.weifeng@live.cn
=======================

更新:
=======================
V0.2.1 2017-07  增加扫码支付的支持，目前仅支持模式1<br/>

----

RoadMap:
=======================
1. 增加微信扫码模式2的支持<br/>
2，增加支付宝扫码支付的支持<br/>
3，支持支付宝新接口<br/>

安装方法：
=======================
pip install openunipay

----
服务端部署：
=======================
（需要基于django 项目部署。随后会提供开箱即用的Docker Image)
此module 需要集成在django 项目中。

----
1, 在settings.py 里 将openunipay 添加到 install app中<br/>
INSTALLED_APPS = (
    ......
    'openunipay',
)

----
2, 发布 支付宝 和 微信支付支付 异步支付结果通知URL。支付成功后，支付宝和微信支付 在支付成功后会通过此URL通知支付结果
openunipay 已经提供了用于处理支付结果的django view. 你只需配置django URL 将openunipay的view 发布即可。<br/>
openuipay 提供了以下三个个view<br/>
openuipay.api.views_alipay.process_notify<br/>
openuipay.api.views_weixin.process_notify<br/>
openuipay.api.views_weixin.process_qr_notify<br/>

在你的url.py里
*********************************************************
from openunipay.api import views_alipay, views_weixin<br/>

urlpatterns = [
    url(r'^notify/weixin/$', views_weixin.process_notify),      //用户使用微信付款后，微信服务器会调用这个接口。详细流程参看微信支付文档<br/>
	url(r'^qrnotify/weixin/$', views_weixin.process_qr_notify), //微信扫码支付， 用户扫描二维码后，微信服务器会调用这个接口。详细流程请参考微信扫码支付文档<br/>
    url(r'^notify/alipay/$', views_alipay.process_notify),      //支付宝支付后，支付宝服务器会调用这个接口。详细流程参看支付宝文档<br/>
]
***********************************************************

----
3，在settings.py里添加以下配置项<br/>

#####支付宝支付配置<br/>
ALIPAY = {<br/>
		'partner':'XXX', //支付宝partner ID<br/>
		'seller_id':'XXX', //收款方支付宝账号如 pan.weifeng@live.cn<br/>
		'notify_url':'https://XXX/notify/alipay/', //支付宝异步通知接收URL<br/>
		'ali_public_key_pem':'PATH to PEM File', //支付宝公钥的PEM文件路径,在支付宝合作伙伴密钥管理中查看(需要使用合作伙伴支付宝公钥)。如何查看，请参看支付宝文档<br/>
		'rsa_private_key_pem':'PATH to PEM File',//您自己的支付宝账户的私钥的PEM文件路径。如何设置，请参看支付宝文档<br/>
		'rsa_public_key_pem':'PATH to PEM File',//您自己的支付宝账户的公钥的PEM文件路径。如何设置，请参看支付宝文档<br/>
	}<br/>
#####微信支付配置<br/>
WEIXIN = {<br/>
		'app_id':'XXX', //微信APPID<br/>
		'app_seckey':'XXX', //微信APP Sec Key<br/>
		'mch_id':'XXX', //微信商户ID<br/>
		'mch_seckey':'XXX',//微信商户seckey<br/>
		'mch_notify_url':'https://XXX/notify/weixin/', //微信支付异步通知接收URL<br/>
		'clientIp':'',//扫码支付时，会使用这个IP地址发送给微信API, 请设置为您服务器的IP
	}<br/>
        
----
4, 同步数据库

python manage.py migrate --run-syncdb<br/>

----


如何使用：
=======================
1，创建订单<br/>
from openunipay.paygateway import unipay <br/>
from openunipay.models import PAY_WAY_WEIXIN,PAY_WAY_ALI  //PAY_WAY_WEIXIN:微信支付  PAY_WAY_ALI:支付宝支付<br/>

create_order.create_order(orderno, payway, clientIp, product_desc, product_detail, fee, user=None, attach=None, expire=1440, **kwargs): <br/>
此方法会返回支付信息。在APP中发起支付时 需要使用此支付信息。所有数据已经按照微信和支付宝接口要求做了处理。APP无需再次处理。<br/>


2, 查寻订单<br/>
query_order(orderno)<br/>
APP支付成功后，需要调用此接口确认支付。发货流程需要在此方法里处理。<br/>


3. 生成扫码支付二维码（目前仅支持微信扫码支付模式1)<br/>
generate_qr_pay_url(payway, productid)<br/>
已经在Admin 里增加了Production Model Admin. 只需要增加商品即可生成支付URL. 然后用URL生成二维码。 你也可以用此方法的链接在服务端生成二维码图片.<br/>

----