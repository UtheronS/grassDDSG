import asyncio
import random
import ssl
import json
import time
import uuid
from loguru import logger
from websockets_proxy import Proxy, proxy_connect


async def connect_to_wss(socks5_proxy, user_id, user_agent):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy))
    logger.info(device_id)
    while True:
        try:
            await asyncio.sleep(random.randint(1, 10) / 10)
            custom_headers = {
                "User-Agent": user_agent
            }
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            uri = "wss://proxy.wynd.network:4650/"
            server_hostname = "proxy.wynd.network"
            proxy = Proxy.from_url(socks5_proxy)
            async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=server_hostname,
                                     extra_headers=custom_headers) as websocket:
                async def send_ping():
                    while True:
                        send_message = json.dumps(
                            {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}})
                        logger.debug(send_message)
                        await websocket.send(send_message)
                        await asyncio.sleep(20)

                await asyncio.sleep(1)
                asyncio.create_task(send_ping())

                while True:
                    response = await websocket.recv()
                    message = json.loads(response)
                    logger.info(message)
                    if message.get("action") == "AUTH":
                        auth_response = {
                            "id": message["id"],
                            "origin_action": "AUTH",
                            "result": {
                                "browser_id": device_id,
                                "user_id": user_id,
                                "user_agent": custom_headers['User-Agent'],
                                "timestamp": int(time.time()),
                                "device_type": "extension",
                                "version": "2.5.0"
                            }
                        }
                        logger.debug(auth_response)
                        await websocket.send(json.dumps(auth_response))

                    elif message.get("action") == "PONG":
                        pong_response = {"id": message["id"], "origin_action": "PONG"}
                        logger.debug(pong_response)
                        await websocket.send(json.dumps(pong_response))
        except Exception as e:
            logger.error(e)
            logger.error(socks5_proxy)


async def main():
    user_ids = ['2pIv69fJsj7FckViQBpGZA62cQo', '2pIvxieqZpw4jo0XpNXyAEfeQBf', '2pIwd1RZoaQcGtWhL7kSqbXt7yg',
                '2pIxEyMGhOR41n2PjDFIUtZ8kBV', '2pIxnfgZFIq9vcvTffrkDeIGkYL', '2pIyOw3Wg17C57LPMCuXbMQir7z']  # Добавьте до 100 user_id
    socks5_proxy_list = [
        'http://L7AaGtfWgMzK:RNW78Fm5@pool.proxy.market:10029',
        'http://V0KDP7thHMUq:RNW78Fm5@pool.proxy.market:10089',
        'http://WNPmwYfrvpcN:RNW78Fm5@pool.proxy.market:10047',
        'http://4bXUISbp31Ct:RNW78Fm5@pool.proxy.market:10055',
        'http://08MTthJXmNAO:RNW78Fm5@pool.proxy.market:10012',
        'http://S2ZTQhOtequS:RNW78Fm5@pool.proxy.market:10070',
        # Добавьте до 100 прокси
    ]
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.89 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.71 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.101 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.59 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.70 Safari/537.36",
        # Добавьте другие User-Agent для разнообразия
    ]

    tasks = []
    for user_id, proxy, user_agent in zip(user_ids, socks5_proxy_list, user_agents):
        tasks.append(asyncio.ensure_future(connect_to_wss(proxy, user_id, user_agent)))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())