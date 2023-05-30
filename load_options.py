import streamlit as st
import requests
from urllib.parse import urlparse

def from_url():
    image_url = st.text_input("Введите URL изображения:")
    if image_url:
        parsed_url = urlparse(image_url)
        if not parsed_url.scheme:
            st.error("Некорректный URL-адрес. Проверьте, что вы включили схему (например, 'https://').")
        else:
            try:
                response = requests.get(image_url)
                return response.content
            except:
                st.error("Не удалось загрузить изображение. Проверьте ссылку или попробуйте другое изображение.")


def from_device():
    with st.form("Загрузка файла с устройства:", clear_on_submit=True):
        uploaded_file = st.file_uploader(label="Выберите изображениe для распознавания:", type=['png', 'jpg', 'jpeg'])
        submitted = st.form_submit_button("Загрузить")
        if submitted and uploaded_file is not None:
            return uploaded_file
        elif submitted and uploaded_file is None:
            st.error("Файл не выбран")


def from_camera():
    with st.form("Загрузка с камеры", clear_on_submit=True):
        uploaded_file = st.camera_input("Сделайте снимок: ")
        submitted = st.form_submit_button("Загрузить")
        if submitted and uploaded_file is not None:
            return uploaded_file