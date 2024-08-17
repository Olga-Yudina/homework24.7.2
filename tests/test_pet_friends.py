from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Simych', animal_type='chupacabra',
                                     age='4', pet_photo='images/pet.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Shpyl", "melkokosh", "4", "images/pet2.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Sima', animal_type='cat', age=4):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password): #1
    """ Проверяем что запрос api ключа с использованием несуществующих логина и пароля возвращает статус 403"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status
    status, _ = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403




def test_add_new_pet_with_valid_data_without_photo(name='Simych', animal_type='chupacabra',
                                     age='4'): #2
    """Проверяем что можно добавить питомца с корректными данными без фото"""


    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_add_photo_of_pet(name='Simych', animal_type='chupacabra',
                                     age='4', pet_photo='images/pet.jpg'): #3
    '''Проверяем что можно добавить фото питомца'''

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то ищем питомца с заданным именем
    pet_id = -1
    if len(my_pets['pets']) > 0:
        for pet in my_pets['pets']:
            if pet['name'] == name:
                pet_id = pet['id']

    # Если питомец не найден, создаем питомца без фото
    if pet_id == -1:
        status, result = pf.add_pet_without_photo(auth_key, name, animal_type, age)
        assert status == 200
        assert result['name'] == name
        pet_id = result['id']

    # Добавляем фото к питомцу
    status, result = pf.add_photo_of_pet(auth_key, pet_id, pet_photo)
    assert status == 200
    assert result['pet_photo']


def test_get_api_key_for_invalid_email(email=invalid_email, password=valid_password): #4
    """ Проверяем что запрос api ключа с использованием несуществующего логина возвращает статус 403"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status
    status, _ = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403


def test_get_api_key_for_invalid_password(email=valid_email, password=invalid_password): #5
    """ Проверяем что запрос api ключа с использованием несуществующего пароля возвращает статус 403"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status
    status, _ = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403


def test_delete_pet_with_invalid_auth_key(): #6
    """Проверяем возможность удаления питомца c использованием некорректного ключа auth_key"""

    # Сохраняем некорректный auth_key в переменную и запрашиваем список своих питомцев
    auth_key = {'key': 'invalid'}
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = '0'
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Проверяем что статус ответа равен 403
    assert status == 403


def test_add_new_pet_with_invalid_auth_key_without_photo(name='Simych', animal_type='chupacabra',
                                     age='4'): #7
    """Проверяем что нельзя добавить питомца с использованием некорректного auth_key"""

    # Сохраняем некорректный auth_key в переменную
    auth_key = {'key': 'invalid'}

    # Добавляем питомца
    status, _ = pf.add_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 403


def test_get_all_pets_with_invalid_key(filter=''): #8
    """ Проверяем что невозможно получить список питомцев используя некорректный auth_key """

    # Сохраняем некорректный auth_key в переменную и пытаемся получить список своих питомцев
    auth_key = {'key': 'invalid'}
    status, _ = pf.get_list_of_pets(auth_key, filter)

    assert status == 403

def test_update_self_pet_info_with_invalid_auth_key(name='Sima', animal_type='cat', age=4): #9
    """Проверяем невозможность обновления информации о питомце при использовании некорректного auth_key"""

    # Сохраняем некорректный ключ auth_key в переменную и запрашиваем список своих питомцев
    auth_key = {'key': 'invalid'}

    # 
    status, _ = pf.update_pet_info(auth_key, '0', name, animal_type, age)

    # Проверяем что статус ответа = 403
    assert status == 403


def test_add_new_pet_with_invalid_data(name='Simych', animal_type='chupacabra',
                                     age='4', pet_photo='images/pet.jpg'): #10
    """Проверяем что нельзя добавить питомца с использованием некорректного auth_key"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Сохраняем некорректный auth_key в переменную
    auth_key = {'key': 'invalid'}

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 403
