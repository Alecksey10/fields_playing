import pathlib
import threading
import time
import streamlit as st
import os
from datetime import datetime
from downloader import agent
from downloader.schemas import DownloadResult, DownloadScheme
from streamlit.runtime.scriptrunner import add_script_run_ctx
# Заголовок приложения
st.title("Генератор путей к файлам")

# Боковая панель с параметрами
st.sidebar.header("Параметры")

# Поля ввода
city = st.sidebar.selectbox(
    "Выберите регион",
    [
"Белгородская область",
"Брянская область",
"Владимирская область",
"Воронежская область",
"Ивановская область",
"Калужская область",
"Костромская область",
"Курская область",
"Липецкая область",
"Московская область",
"Орловская область",
"Рязанская область",
"Смоленская область",
"Тамбовская область",
"Тверская область",
"Тульская область",
"Ярославская область",
"г.Москва",
"Республика Карелия",
"Республика Коми",
"Архангельская область",
"Вологодская область",
"Калининградская область",
"Ленинградская область",
"Мурманская область",
"Новгородская область",
"Псковская область",
"г.Санкт-Петербург",
"Республика Адыгея",
"Республика Калмыкия",
"Республика Крым",
"Краснодарский край",
"Астраханская область",
"Волгоградская область",
"Ростовская область",
"г. Севастополь",
"Республика Дагестан",
"Кабардино-Балкарская Республика",
"Карачаево-Черкесская Республика",
"Республика Северная Осетия - Алания",
"Чеченская Республика",
"Ставропольский край",
"Республика Башкортостан",
"Республика Марий Эл",
"Республика Мордовия",
"Республика Татарстан",
"Удмуртская Республика",
"Чувашская Республика",
"Пермский край",
"Кировская область",
"Нижегородская область",
"Оренбургская область",
"Пензенская область",
"Самарская область",
"Саратовская область",
"Ульяновская область",
"Курганская область",
"Свердловская область",
"Тюменская область",
"Челябинская область",
"Республика Алтай",
"Республика Бурятия",
"Республика Тыва",
"Республика Хакасия",
"Алтайский край",
"Забайкальский край",
"Красноярский край",
"Иркутская область",
"Кемеровская область",
"Новосибирская область",
"Омская область",
"Томская область",
"Республика Саха (Якутия)",
"Камчатский край",
"Приморский край",
"Хабаровский край",
"Амурская область",
"Магаданская область",
"Сахалинская область",
"Еврейская автономная область",
"Чукотский автономный округ"]
)


theme = st.sidebar.text_input(
    "Тема",
    value="Численность всего населения по полу и возрасту на 1 января текущего года"
)


year = st.sidebar.number_input(
    "Год",
    min_value=2000,
    max_value=datetime.now().year,
    value=2025
)

year_from = st.sidebar.number_input(
    "Год от",
    min_value=2000,
    max_value=datetime.now().year,
    value=2025
)

year_to = st.sidebar.number_input(
    "Год до",
    min_value=year_from,
    max_value=datetime.now().year,
    value=2025
)

document_type = st.sidebar.selectbox(
    "Формат файла",
    ["CSV", "Excel"]
)

# Базовый путь к каталогу
base_path = "/data/reports"

# Формируем имя файла из параметров
filename = f"{city}_{theme}_{year_from}-{year_to}.{document_type.lower()}"
filename = filename.replace(' ', '_')

# Формируем полный путь
file_path = os.path.join(base_path, filename)

# Отображаем результат
st.subheader("Сформированный путь:")
st.code(file_path)

if 'status' not in st.session_state:
    st.session_state.status = {'status':'wait'}
    st.session_state.last_result = None



def background_task(downloader:agent.Downloader):
    # global last_result
    print(st.session_state.status, id(st.session_state.status))
    try:
        result = downloader.do_full_logic()
        print("DONE", result.success, result)
        if(result.success):
            st.session_state.last_result = result
            st.session_state.status['status'] = 'success'
        else:
            st.session_state.status['status'] = 'error'
    except:
        st.session_state.status['status'] = 'error'


# Дополнительно можно добавить кнопку для скачивания/сохранения

if st.button("Парсить", disabled=st.session_state.status['status']=='parsing'):
    ds = DownloadScheme(download_path=str(pathlib.Path(os.getcwd()).joinpath('./download_path')), 
                    city=str(city),
                    theme=str(theme),
                    year=str(year),
                    year_from=str(year_from),
                    year_to=str(year_to),
                    document_type=str(document_type))
    print(ds)
    downloader = agent.Downloader()
    downloader.init_by_download_scheme(ds)
    
    thread = threading.Thread(target=background_task, args=(downloader,))
    add_script_run_ctx(thread)
    st.session_state.status['status'] = 'parsing'
    thread.start()

    if(st.session_state.status['status']!='wait'):
        if(st.session_state.status['status']=='success'):
            st.success(f"Данные спаршены в файл {st.session_state.last_result.path}")
        elif(st.session_state.status['status']=='error'):
            st.error(f"Проблемы")

    st.rerun()

if(st.session_state.status['status']!='wait'):
    if(st.session_state.status['status']=='success'):
        st.success(f"Данные спаршены в файл {st.session_state.last_result.path}")
        st.session_state.status['status'] = 'wait'
    elif(st.session_state.status['status']=='error'):
        st.error(f"Проблемы при парсинге")
        st.session_state.status['status'] = 'wait'
# print("datas", st.session_state.status, id(st.session_state.status))
time.sleep(1)
st.rerun()