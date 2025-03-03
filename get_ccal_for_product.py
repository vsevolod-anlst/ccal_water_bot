# import requests
#
#
# def get_food_info(product_name):
#     url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         products = data.get('products', [])
#         if products:  # Проверяем, есть ли найденные продукты
#             first_product = products[0]
#             return {
#                 'name': first_product.get('product_name', 'Неизвестно'),
#                 'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
#             }
#         return None
#     print(f"Ошибка: {response.status_code}")
#     return None
import aiohttp


async def get_food_info(product_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    if products:  # Проверяем, есть ли найденные продукты
                        first_product = products[0]
                        return {
                            'name': first_product.get('product_name', 'Неизвестно'),
                            'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
                        }
                    return "Продукт не найден"
                else:
                    print(f"Ошибка: статус код {response.status}")
                    return None
    except aiohttp.ClientError as e:
        print(f"Ошибка клиента: {e}")
        return None
