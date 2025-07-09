import inspect
import logging
# create logger
class ClassNameFilter(logging.Filter):
    def filter(self, record):
        # Получаем текущий стек вызовов
        frame = inspect.currentframe()
        while frame:
            # Пропускаем фреймы, связанные с самим логированием и обработчиками
            module_name = frame.f_globals.get("__name__")
            # Пропускаем модули logging и текущий модуль (где определён фильтр)
            if module_name not in ("logging", __name__):
                # Если в локальных переменных есть self, значит, мы в методе класса
                if 'self' in frame.f_locals:
                    # Извлекаем имя класса
                    record.class_name = frame.f_locals['self'].__class__.__name__
                    break
            frame = frame.f_back
        else:
            # Если стек не содержит класса, задаём значение по умолчанию
            record.class_name = 'N/A'
        return True

# Настройка логгера
logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)

# Добавляем обработчик
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# Настраиваем формат вывода
formatter = logging.Formatter('%(asctime)s - %(class_name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Добавляем фильтр для записи информации о классе
handler.addFilter(ClassNameFilter())
logger.addHandler(handler)

# logger.disabled=True