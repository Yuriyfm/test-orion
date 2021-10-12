import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_db():
    """"Фукнция создает БД на основе данных db_user и db_password и db_name."""
    try:
        # Устанавливаем соединение с postgres
        db_user = "postgres"
        db_password = "qwerty"
        db_name = 'oriondatabase'
        connection = psycopg2.connect(user=db_user, password=db_password)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # Создаем курсор для выполнения операций с базой данных
        cursor = connection.cursor()
        # Создаем базу данных
        sql_create_database = cursor.execute(f'create database {db_name}')
        # Закрываем соединение
        cursor.close()
        connection.close()
        return ('База данных oriondb успешно создана')
    # ловим ошибку если БД с таким именем уже существует
    except psycopg2.errors.DuplicateDatabase:
        return ('База данных с таким именем уже существует')
    except psycopg2.OperationalError:
        return ('Указан неверный db_user или db_password')



print(create_db())




