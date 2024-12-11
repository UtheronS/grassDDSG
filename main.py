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
    logger.info(f"Запуск для {user_id} с прокси {socks5_proxy} и User-Agent {user_agent}")

    points_earned = 0  # Счетчик очков

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
                        logger.debug(f"Отправка PING: {send_message}")
                        await websocket.send(send_message)
                        await asyncio.sleep(10)

                await asyncio.sleep(1)
                asyncio.create_task(send_ping())

                while True:
                    response = await websocket.recv()
                    message = json.loads(response)
                    logger.info(f"Получено сообщение: {message}")

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
                        logger.debug(f"Отправка AUTH: {auth_response}")
                        await websocket.send(json.dumps(auth_response))

                    elif message.get("action") == "PONG":
                        pong_response = {"id": message["id"], "origin_action": "PONG"}
                        logger.debug(f"Отправка PONG: {pong_response}")
                        await websocket.send(json.dumps(pong_response))

                    # Пример обработки очков (замените на вашу логику)
                    elif message.get("action") == "POINTS_EARNED":
                        points_earned += message.get("points", 0)
                        logger.info(f"Очки заработаны: {points_earned}")

        except Exception as e:
            logger.error(f"Ошибка: {e}")
            logger.error(f"Проблема с прокси: {socks5_proxy}")


async def main():
    user_ids = ['2pIv69fJsj7FckViQBpGZA62cQo', '2pIvxieqZpw4jo0XpNXyAEfeQBf', '2pIwd1RZoaQcGtWhL7kSqbXt7yg',
                '2pIxEyMGhOR41n2PjDFIUtZ8kBV', '2pIxnfgZFIq9vcvTffrkDeIGkYL', '2pIyOw3Wg17C57LPMCuXbMQir7z',
                '2q1x2CrvTppyRMrPMw2QTZwgjQz', '2q1zwOkJF32v5RXHCPkzM8gWeyq', '2q21Vss1Yhcbi5r0WCC3Lwj1mrK',
                '2q233mJ7uq500wYW92H3Mt5CaG4', '2q28FBrz5ipxgmMIEkrCXnO69xQ', '2q2AG0UqN5n8CNpeMTCLeYZtWxU']

    socks5_proxy_list = [
        'http://josopbjoimytqqr103387-zone-resi-region-nl-session-NbZ0CMm5mgoO-sessTime-1440:ugykowwaay@resi-eu.lightningproxies.net:9999',
        'http://josopbjoimytqqr103387-zone-resi-region-nl-session-jVPwYoYkGvmr-sessTime-1440:ugykowwaay@resi-eu.lightningproxies.net:9999',
        'http://josopbjoimytqqr103387-zone-resi-region-nl-session-uXlNt9Oh9VWd-sessTime-1440:ugykowwaay@resi-eu.lightningproxies.net:9999',
        'http://josopbjoimytqqr103387-zone-resi-region-nl-session-xdOR67wxFs8Z-sessTime-1440:ugykowwaay@resi-eu.lightningproxies.net:9999',
        'http://josopbjoimytqqr103387-zone-resi-region-nl-session-dEGv7T255lct-sessTime-1440:ugykowwaay@resi-eu.lightningproxies.net:9999',
        'http://josopbjoimytqqr103387-zone-resi-region-nl-session-T2MeKOzF6Ify-sessTime-1440:ugykowwaay@resi-eu.lightningproxies.net:9999',
        'http://josopbjoimytqqr103387-zone-resi-region-nl-session-RIL8fGsiO4hV-sessTime-1440:ugykowwaay@resi-eu.lightningproxies.net:9999',
        'http://josopbjoimytqqr103387-zone-resi-region-nl-session-JAgDSdT8ctNr-sessTime-1440:ugykowwaay@resi-eu.lightningproxies.net:9999',
        'http://josopbjoimytqqr103387-zone-resi-region-nl-session-LEHnHOQrIiBE-sessTime-1440:ugykowwaay@resi-eu.lightningproxies.net:9999',
        'http://josopbjoimytqqr103387-zone-resi-region-nl-session-a5kuyEOqfEyF-sessTime-1440:ugykowwaay@resi-eu.lightningproxies.net:9999',
        'http://josopbjoimytqqr103387-zone-resi-region-nl-session-lZAJCFMlJNYs-sessTime-1440:ugykowwaay@resi-eu.lightningproxies.net:9999',
        'http://josopbjoimytqqr103387-zone-resi-region-nl-session-nzgar3R8ibAn-sessTime-1440:ugykowwaay@resi-eu.lightningproxies.net:9999',
        # Добавьте другие прокси
    ]

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36", # 55
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", # 54
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36", # 53
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36", # 52
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36", # 51
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36", # 50
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36", # New account
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36", # New account
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", # New account
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36", # New account
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36", # New account
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36", # New account
        # Добавьте другие User-Agent для разнообразия
    ]

    tasks = []
    for user_id, proxy, user_agent in zip(user_ids, socks5_proxy_list, user_agents):
        tasks.append(asyncio.ensure_future(connect_to_wss(proxy, user_id, user_agent)))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
