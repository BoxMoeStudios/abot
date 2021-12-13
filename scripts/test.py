from PIL import Image
import requests
import base64
import io

url = 'http://q2.qlogo.cn/headimg_dl?dst_uin=1366723936&spec=100'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Host': 'q1.qlogo.cn',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8'
}

sess = requests.Session()

r = sess.get(url, headers=headers).content

im = Image.open(io.BytesIO(r)).convert('L')

im.show()