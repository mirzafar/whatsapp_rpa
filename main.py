import asyncio

import httpx

from client import ClientDriver
from settings import settings


async def main():
    driver_client = ClientDriver()

    # open whatsapp and send pin code to telegram
    flag = await driver_client.activate_whatsapp()

    while flag:
        try:
            async with httpx.AsyncClient() as session:
                url = settings['base_url']
                response = await session.get(url)
                messages = response.json()

                send_ids = []
                for message in (messages.get('items') or []):
                    _, phone = driver_client.validate_phone(message.get('phone'))
                    if all([
                        phone,
                        message.get('message'),
                        message.get('id'),
                    ]):
                        try:
                            # open chat client and write text
                            await driver_client.open_url(
                                f'{settings["whatsapp"]["url"]}send?phone={phone}&text={message["message"]}', 10
                            )

                            # click to send button
                            await driver_client.click_send_button()
                            send_ids.append(message['id'])

                        except (Exception,) as e:
                            print(f'main$session() -> error: {str(e)}')
                            flag = False
                            await driver_client.send_message(f'main$session() -> error: {str(e)}')
                            break
                if send_ids:
                    print(await session.get(url, params={
                        'action': 'set_as_sent',
                        'item_ids': send_ids
                    }))

                if flag is False:
                    await main()

        except (Exception,) as e:
            print(f'main() -> error: {str(e)}')
            await driver_client.send_message(f'main() -> error: {str(e)}')
            await main()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
