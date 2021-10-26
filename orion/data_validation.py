from typing import List
from pydantic import BaseModel, EmailStr, validator
from datetime import date
import re

# блок с регулярными выражениями для проверки валидности данных
from pydantic.class_validators import Optional

file_path_validation_regexp = "^\\/([а-яА-Яa-zA-Z-_]+\\/)+([а-яА-Яa-zA-Z-_]+)(\\.)([a-zA-Z]{3,4})$"
full_name_validation_regexp = "^[А-ЯЁ][а-яёА-ЯЁ\\-]{0,}\\s[А-ЯЁ][а-яёА-ЯЁ\\-]{1,}(\\s[А-ЯЁ][а-яёА-ЯЁ\\-]{1,})?$"
address_validation_regexp = "^([А-Я][а-яёА-Я\\-]{1,})(?: +[А-Я][а-яёА-Я\\-]{1,})?, +(?:\\d+(?:-[яЯ])? +)?([А-Я]" \
                            "[а-яёА-Я\\-]{1,})(?:( +[а-яёА-Я][а-яёА-Я\\-]{1,})|( +[а-я]))*?( +\\d+(\\-)?[а-яёА-Я])?," \
                            " +д. +\\d+[А-Я]{0,1}, +кв. +\\d+$"
phone_number_validation_regexp = '^((8|\\+7))(\\(?\\d{3}\\)?)([\\d]{7})$'
person_id_validation_regexp = "^(\\d+)$"


# определяем модели в классах библиотеки pydantic
class EmailData(BaseModel):
    email_address: EmailStr
    email_type: str
    person_id: Optional[str]
    old_email_address: Optional[EmailStr]

    @validator('email_type')
    def email_type_validator(cls, v):
        email_types = ['Личная', 'Рабочая']
        if v not in email_types:
            raise ValueError(f'Значение атрибута email_type должно соответствовать одному из вариантов -  '
                             f'{", ".join(email_types)}. Было получено - {v}')
        return v.title()

    @validator('person_id')
    def order_validator(cls, v):
        if not v.isdigit():
            raise ValueError(f'Значение атрибута person_id должно быть числовым')
        return v.title()


class PhoneData(BaseModel):
    phone_number: str
    phone_type: str
    person_id: Optional[str]
    old_phone_number: Optional[str]

    @validator('phone_type')
    def phone_type_validator(cls, v):
        phone_types = ['Городской', 'Мобильный']
        if v not in phone_types:
            raise ValueError(f'Значение атрибута phone_number должно соответствовать одному из вариантов -  '
                             f'{", ".join(phone_types)}. Было получено - {v}')
        return v.title()

    @validator('phone_number')
    def phone_number_validator(cls, v):
        if not re.match(phone_number_validation_regexp, v):
            raise ValueError(f'Неверный формат атрибута phone_number. Ожидается номер в одном из форматов -'
                             f' +7хххххххххх/+7(ххх)ххххххх/8хххххххххх/8(ххх)ххххххх. Было получено - {v}')
        return v.title()

    @validator('old_phone_number')
    def old_phone_number_validator(cls, v):
        if not re.match(phone_number_validation_regexp, v):
            raise ValueError(f'Неверный формат атрибута old_phone_number. Ожидается номер в одном из форматов -'
                             f' +7хххххххххх/+7(ххх)ххххххх/8хххххххххх/8(ххх)ххххххх. Было получено - {v}')
        return v.title()

    @validator('person_id')
    def order_validator(cls, v):
        if not v.isdigit():
            raise ValueError(f'Значение атрибута person_id должно быть числовым')
        return v.title()


class PersonData(BaseModel):
    file_path: str
    full_name: str
    gender: str
    birthday: date
    address: str
    person_id: Optional[str]
    phones: Optional[List[PhoneData]]
    emails: Optional[List[EmailData]]

    @validator('file_path')
    def file_path_validator(cls, v):
        if not re.match(file_path_validation_regexp, v):
            raise ValueError(f'Неверный формат атрибута file_path. Ожидается путь в подобном формате - '
                             f'/media/profile_images/profile_photo.jpg. Было получено - {v}')
        return v.title()

    @validator('full_name')
    def full_name_validator(cls, v):
        if not re.match(full_name_validation_regexp, v):
            raise ValueError(f'Неверный формат атрибута full_name. Ожидается ФИО в подобном формате - '
                             f'Иванов Иван Иванович. Было получено - {v}')
        return v.title()

    @validator('gender')
    def gender_validator(cls, v):
        genders = ['Мужской', 'Женский']
        if v not in genders:
            raise ValueError(f'Значение атрибута genders должно соответствовать одному из вариантов - '
                             f'{", ".join(genders)}. Было получено - {v}')
        return v.title()

    @validator('address')
    def address_validator(cls, v):
        if not re.match(address_validation_regexp, v):
            raise ValueError('Неверный формат атрибута address. Ожидается адрес в  подобном формате - '
                             'Красноярск, Мира, д. 1, кв. 3 (элементы - "город", "улица", "дом", "квартира",'
                             ' разделены запятой и пробелом, количество пробелов между элементами  и внутри'
                             ' них может быть больше одного, названия улиц и городов начинаются с заглавной '
                             f'буквы). Было получено - {v}')
        return v.title()

    @validator('person_id')
    def order_validator(cls, v):
        if not v.isdigit():
            raise ValueError(f'Значение атрибута person_id должно быть числовым')
        return v.title()


class SortedData(BaseModel):
    sorted_by: str
    order: str

    @validator('sorted_by')
    def sorted_by_validator(cls, v):
        all_attributes = ['person_id', 'address', 'birthday', 'file_path', 'full_name', 'gender',
                          'phone_type', 'phone_number', 'email_type', 'email_address']
        if v not in all_attributes:
            raise ValueError(f'Значение атрибута sorted_by должно соответствовать одному из вариантов -  '
                             f'{", ".join(all_attributes)}')
        return v.title()

    @validator('order')
    def order_validator(cls, v):
        orders = ['asc', 'desc']
        if v not in orders:
            raise ValueError(f'Значение атрибута order должно соответствовать одному из вариантов -  '
                             f'{", ".join(orders)}')
        return v.title()


class IdData(BaseModel):
    person_id: str

    @validator('person_id')
    def order_validator(cls, v):
        if not v.isdigit():
            raise ValueError(f'Значение атрибута person_id должно быть числовым')
        return v.title()

