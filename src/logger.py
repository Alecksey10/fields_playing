import logging

# Создание логгера
logger = logging.getLogger("parser_app")
logger.setLevel(logging.DEBUG)

# Форматтер
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# # Обработчик для файла
# file_handler = logging.FileHandler("app.log")
# file_handler.setFormatter(formatter)
# file_handler.setLevel(logging.DEBUG)

if not hasattr(logger, 'handles'):
    logger.handles = []
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.handles.append(handler)

# Обработчик для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Добавляем обработчики к логгеру
# logger.addHandler(file_handler)
logger.addHandler(console_handler)