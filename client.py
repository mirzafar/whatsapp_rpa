import asyncio
from typing import Tuple

import aiofiles
import httpx
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from settings import settings

chrome_options = Options()
chrome_options.add_argument("--start-fullscreen")


class ClientDriver:
    driver = None

    def __init__(self):
        self.driver = webdriver.Chrome(chrome_options)
        self.driver.fullscreen_window()

    async def open_url(self, url: str, time_sleep: int):
        if self.driver:
            self.driver.get(url)

            await asyncio.sleep(time_sleep)

    async def activate_whatsapp(self) -> bool:
        try:
            if self.driver:
                await self.open_url(settings['whatsapp']['url'], 10)

                button_link_by_phone = self.driver.find_element(By.XPATH, '//span[@role ="button"]')
                button_link_by_phone.click()

                await asyncio.sleep(2)
                input_text = self.driver.find_element(By.XPATH, '//input[@value = "+7 "]')
                await asyncio.sleep(2)
                input_text.send_keys('value', settings['number'])
                await asyncio.sleep(2)

                buttons = self.driver.find_elements(By.XPATH, '//div[@role = "button"]')
                await asyncio.sleep(2)
                if not buttons:
                    return False

                find_flag = False
                for button in buttons:
                    if button.text.lower() in ['далее', 'next']:
                        find_flag = True
                        button.click()

                if find_flag is False:
                    return False

                self.driver.save_screenshot('pin_code.png')
                await asyncio.sleep(3)

                code = self.driver.find_element(By.XPATH, '//div[@aria-live = "polite"]')
                chunks = code.find_elements(By.XPATH, '//span')
                pin_code = str()
                if chunks:
                    for chunk in chunks:
                        if len(chunk.text) == 1:
                            pin_code += chunk.text

                await asyncio.sleep(5)

                success = await self.send_message(pin_code)
                print(f'ClientDriver$take_screenshot_and_send() -> success: {success}')
                if success:
                    await asyncio.sleep(15)

                return success

        except (Exception,) as e:
            print(f'ClientDriver$activate_whatsapp() -> error: {str(e)}')
            await self.send_message(f'ClientDriver$activate_whatsapp() -> error: {str(e)}')

        return False

    async def click_send_button(self):
        button = self.driver.find_element(By.XPATH, '//span[@data-icon ="send"]')
        button.click()

        await asyncio.sleep(4)

    def validate_phone(self, number) -> Tuple[bool, str]:
        if number and number.startswith('77') and len(number) == 11:
            return True, f'+{number}'
        elif number and number.startswith('87') and len(number) == 11:
            return True, f'+7{number[1:]}'

        elif number and number.startswith('+77') and len(number) == 12:
            return True, number

        return False, str()

    async def send_message(self, text) -> bool:
        url = f'https://api.telegram.org/bot{settings["telegram_token"]}/sendMessage'
        payload = {
            'chat_id': settings['tg_id'],
            'text': text,
        }
        try:
            async with httpx.AsyncClient() as session:
                response = await session.post(url, json=payload)
                response = response.json()

                if response.get('ok') is True:
                    return True

        except (Exception,) as e:
            print(f'send_pin_code() -> error: {e}')

        return False

    async def validate_message(self, text):
        try:
            with open('text.txt', 'w', encoding='utf-8') as file:
                file.write(str(text))

            async with aiofiles.open('text.txt', 'r', encoding='utf-8') as file:
                print('success')
                return str(await file.read())

        except (Exception,) as e:
            print(f'ClientDriver$validate_message() -> ERROR: {e}')
            return None
