import asyncio
from datetime import datetime

from client import ClientDriver
from request import request
from settings import settings


async def main():
    driver_client = ClientDriver()

    # open whatsapp and send pin code to telegram
    is_run = await driver_client.activate_whatsapp()

    async def run(flag):
        error_count, error_time, error_name = 0, None, None
        while flag:
            error_name = None

            flag, messages = await request(settings['base_url'])
            if flag:
                if not messages:
                    await asyncio.sleep(10)
                    continue

                send_ids = []
                for message in (messages.get('items') or []):
                    error_name = None

                    success, phone = driver_client.validate_phone(message.get('phone'))
                    if not success:
                        print(f'not validate number -> id: {message.get("id")}, number: {message.get("phone")}')

                    success, text = await driver_client.validate_message(message.get('message'))
                    if not success:
                        print(f'not validate text -> id: {message.get("id")}, text: {message.get("text")}')

                    if not message.get('id'):
                        print(f'not message id')
                        continue

                    if all([
                        phone,
                        text,
                        message['id'],
                    ]):
                        try:
                            # open chat client and write text
                            await driver_client.open_url(
                                f'{settings["whatsapp"]["url"]}send?phone={phone}&text={text}', 10
                            )

                            # click to send button
                            await driver_client.click_send_button()
                            send_ids.append(str(message['id']))

                        except (Exception,) as e:
                            error_name = str(e)
                            flag = False
                            print(f'main$session() -> error: {str(e)}')

                            break
                    else:
                        print('message not sent', message)

                if send_ids:
                    success, res = await request(settings['base_url'], params={
                        'action': 'set_as_sent',
                        'item_ids': ','.join(send_ids)
                    })
                    if not success:
                        print(f'main$send_ids() ERROR -> ids: {send_ids}')

            if flag is False:
                if error_name:
                    await driver_client.send_message(f'main$request -> error: {error_name}')
                    print(f'main$request -> error: {error_name}')
                else:
                    await driver_client.send_message(f'main$request error')
                    print(f'main$request error')

                if error_count > 8:
                    raise ConnectionError()
                else:
                    flag = True
                    if error_time and int((datetime.now() - error_time).total_seconds() / 60) > 15:
                        error_count = 0
                    else:
                        error_count += 1
                        error_time = datetime.now()

    if is_run:
        await run(is_run)

    await asyncio.sleep(600)
    await main()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
