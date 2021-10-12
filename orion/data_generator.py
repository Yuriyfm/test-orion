from mimesis import Generic
from mimesis.builtins import RussiaSpecProvider
from mimesis.enums import Gender, FileType
from random import choice, randint
import json
from pprint import pprint

person = Generic('ru')
genders = (Gender.MALE, Gender.FEMALE)

def get_person(gender):
    """Функция с помощью библиотеки mimesis генерирует случайные данные о пользователе и возвращает их в виде словаря"""
    full_name = ' '.join(person.person.full_name(gender).split()[::-1]) + ' ' \
                + RussiaSpecProvider().patronymic(gender=gender)
    file_path = '/media/profile_images/' + person.file.file_name(FileType.IMAGE)
    person_gender = 'Мужской' if gender == Gender.MALE else 'Женский'
    birthday = person.datetime.date(start=1941, end=2003)
    address = f'{person.address.city()}, {person.address.street_name().replace(".", "а")},' \
              f' д. {randint(0, 500)}, кв. {randint(0, 500)}'
    phone_number = choice([person.person.telephone().replace("-", ""),
                           f'+7(391){person.person.telephone()[9:].replace("-", "")}'])
    phone_type = 'Городской' if '(391)' in phone_number else 'Мобильный'
    email_address = person.person.email()
    email_type = choice(['Личная', 'Рабочая'])

    person_data = {'full_name': full_name, 'file_path': file_path, 'gender': person_gender,
                   'birthday': birthday, 'address': address,
                   'phones': [{'phone_number': phone_number, 'phone_type': phone_type}],
                   'emails': [{'email_address': email_address, 'email_type': email_type}]}
    return person_data

# Блок генерации данных в формате JSON для тестирования API.
if __name__ == "__main__":
    def json_for_add_person():
        """Функция генерирует JSON с данными Person и related сущностями для обработчика add_person."""
        json_data =[]
        for i in range(10):
            data = get_person(choice(genders))
            json_data.append(data)
        print((json.dumps(json_data, indent=2, sort_keys=True, default=str, ensure_ascii=False)))

    def json_for_update_person():
        """Функция генерирует JSON c данными Person для обработчика update_person. person_id - подставить существующий"""
        data = get_person(choice(genders))
        json_data = {'person_id': '1', 'full_name': data['full_name'], 'file_path': data['file_path'], 'gender': data['gender'],
                   'birthday': data['birthday'], 'address': data['address']}
        print((json.dumps(json_data, indent=2, sort_keys=True, default=str, ensure_ascii=False)))

    def json_for_add_phone():
        """Функция генерирует JSON c данными Phone для обработчика add_phone. person_id - подставить существующий"""
        data = get_person(choice(genders))
        for item in data['phones']:
            json_data = {'person_id': '1', 'phone_number': item['phone_number'], 'phone_type': item['phone_type']}
            print((json.dumps(json_data, indent=2, sort_keys=True, default=str, ensure_ascii=False)))

    def json_for_add_email():
        """Функция генерирует JSON c данными Phone для обработчика add_phone. person_id - подставить существующий"""
        data = get_person(choice(genders))
        for item in data['emails']:
            json_data = {'person_id': '1', 'email_address': item['email_address'], 'email_type': item['email_type']}
            print((json.dumps(json_data, indent=2, sort_keys=True, default=str, ensure_ascii=False)))

    def json_for_sort_list():
        attributes = ['person_id', 'address', 'birthday', 'email_address', 'email_type', 'file_path', 'full_name', 'gender',
                      'phone_number', 'phone_type']
        order = ['desc', 'asc']
        json_data = {'sorted_by': choice(attributes), 'order': choice(order)}
        print((json.dumps(json_data, indent=2, sort_keys=True, default=str, ensure_ascii=False)))

    # json_for_add_person()
    # json_for_update_person()
    # json_for_add_phone()
    # json_for_add_email()
    json_for_sort_list()
