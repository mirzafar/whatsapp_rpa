import asyncio
from datetime import datetime

import httpx

from client import ClientDriver
from settings import settings


async def main():
    driver_client = ClientDriver()

    # open whatsapp and send pin code to telegram
    flag = await driver_client.activate_whatsapp()

    error_count, error_time, error_name = 0, None, None
    while flag:
        try:
            async with httpx.AsyncClient() as session:
                url = settings['base_url']
                # response = await session.get(url)
                # messages = response.json()
                messages = {
                    'items': [
                        {'phone': '77021557436', 'state': 0,
                         'message': 'Erlan Erke дүкенінен 🛍️ сатып алғаныңызға рахмет.\n                        Құттықтаймыз 🎉! Сізге бонустық ұпайлар берілді💰.\n                        Сіз оларды келесі сатып алуларыңызда пайдалана аласыз.\n                        Біз сізді күтеміз! \U0001faf6🏻\n                        Инстаграм парақшамыз https://www.instagram.com/erlan_erke_astana \n                        \n                        Спасибо за покупку 🛍️ в Erlan Erke. \n                        Поздравляем 🎉 ! Вам начислено бонусные баллы💰\n                        Вы можете их использовать в следующих покупках.\n                        Мы ждем Вас! \U0001faf6🏻\n                        Наш инстаграм https://www.instagram.com/erlan_erke_astana',
                         'id': 744}

                    ]
                }

                send_ids = []
                for message in (messages.get('items') or []):
                    print('new message', message)

                    _, phone = driver_client.validate_phone(message.get('phone'))
                    text = await driver_client.validate_message(message.get('message'))
                    if all([
                        phone,
                        text,
                        message.get('id'),
                    ]):
                        try:
                            # open chat client and write text
                            await driver_client.open_url(
                                f'{settings["whatsapp"]["url"]}send?phone={phone}&text={text}', 10
                            )

                            # click to send button
                            await driver_client.click_send_button()
                            send_ids.append(message['id'])

                        except (Exception,) as e:
                            error_name = str(e)
                            flag = False
                            print(f'main$session() -> error: {str(e)}')

                            break
                    else:
                        print('message not sent', message)

                if send_ids:
                    print(await session.get(url, params={
                        'action': 'set_as_sent',
                        'item_ids': send_ids
                    }))

        except (Exception,) as e:
            error_name = str(e)
            flag = False
            print(f'main() -> error: {str(e)}')

        if flag is False:
            await driver_client.send_message(f'main() -> error: {error_name}')
            print(f'error_count: {error_count}')
            if error_count > 8:
                raise ConnectionError()
            elif error_count > 5:
                await main()
            else:
                flag = True
                if error_time and int((datetime.now() - error_time).total_seconds() / 60) > 10:
                    error_count = 0
                else:
                    error_count += 1
                    error_time = datetime.now()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
