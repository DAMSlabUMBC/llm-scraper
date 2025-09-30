import asyncio
from playwright.async_api import async_playwright

URL = 'https://www.amazon.com/Amazon-vibrant-helpful-routines-Charcoal/dp/B09B8V1LZ3/ref=sr_1_1?crid=1FILQKC6UQ9B5&dib=eyJ2IjoiMSJ9.z0kBrN5J4yDwE3Z69yvpFvmwHHypkHHD1EEB0Tq7d-twKIMmrd6CdpzAKHt3QwCIqpCGWOtUGso25ArgjUeQiby0wRAtPziXyEv_Tf6qw3ScIhyK8WiI5tvRhkwcaZAYJpqeIDTu_m3cf2k1gyY2IF6h7Q-TpQpXqLkVlwxHcP1Ckn7GRQitYbsIXzmMdVt_vBDTTWAeeARk7Yo7VrzCI4_YLLlMbjp_5sTMWrY7dRA.M_EhWcOAkjfHtGyy6bJoS1n8Dh5KYN-aTbt1Uez3DW0&dib_tag=se&keywords=echo%2Bdot&qid=1759097324&sprefix=echo%2Bdo%2Cspecialty-aps%2C87&sr=8-1-catcorr&srs=17938598011&ufe=app_do%3Aamzn1.fos.74097168-0c10-4b8a-b96b-8388a1a12daf&th=1'
async def main(url: str) -> list | None:
        async with async_playwright() as pw:
            try:

                browser = await pw.firefox.launch(headless=False)
                page = await browser.new_page()
                await page.goto(url, wait_until='domcontentloaded')

                await page.wait_for_timeout(5000)

                title = await page.locator("#productTitle").inner_text()
                features = await page.locator("#feature-bullets").inner_text()

                return [title, features]
            except:
                return None
            finally:
                await browser.close()


if __name__ == '__main__':
    print(asyncio.run(main(URL)))