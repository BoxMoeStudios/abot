from httpx import AsyncClient
from PIL import Image
from io import BytesIO
from .browser import get_ua


av_url = "https://q2.qlogo.cn/headimg_dl?dst_uin=%s&spec=100"

async def aget_av(uin: int) -> Image:
    headers = {'User-Agent': get_ua()}
    async with AsyncClient() as c:
        resp = await c.get(av_url % uin, headers=headers)
    if resp.status_code != 200:
        raise ValueError('failded to fetch qq avatar')
    return Image.open(BytesIO(resp.content))