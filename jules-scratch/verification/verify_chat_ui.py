
import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Aumentar el tiempo de espera predeterminado
            page.set_default_timeout(60000)

            await page.goto("http://localhost:8000")

            # Esperar a que aparezca el campo de usuario y escribir el nombre de usuario
            await page.get_by_label("Response").click()
            await page.get_by_label("Response").fill("testuser")
            await page.get_by_label("Response").press("Enter")

            # Esperar a que aparezca el campo de contraseña y escribir la contraseña
            await page.get_by_label("Response").click()
            await page.get_by_label("Response").fill("testpassword")
            await page.get_by_label("Response").press("Enter")

            # Esperar a que aparezca el mensaje de bienvenida
            await expect(page.get_by_text("Bienvenido de nuevo, testuser a Hogar Feliz Chatbot.")).to_be_visible()

            # Esperar a que aparezca el mensaje de selección de IA y hacer clic en una opción
            await expect(page.get_by_text("Por favor, selecciona el modelo de IA para esta sesión.")).to_be_visible()
            await page.get_by_role("button", name="Local Host").click()

            # Esperar a que aparezca el resumen legal
            await expect(page.get_by_text("Resumen Legal para Contratos de Alquiler (España)")).to_be_visible()

            # Tomar una captura de pantalla de la interfaz principal del chat
            await page.screenshot(path="jules-scratch/verification/verification.png")

        except Exception as e:
            print(f"Error durante la ejecución del script de Playwright: {e}")
            # Guardar el contenido de la página para depuración
            with open("jules-scratch/verification/error_page.html", "w") as f:
                f.write(await page.content())
            await page.screenshot(path="jules-scratch/verification/error_screenshot.png")

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
