import tempfile

from PIL import Image
import fer.exceptions
from fer import FER
from io import BytesIO
import matplotlib.pyplot as plt
import streamlit as st
import load_options

with open("webFer.css") as source_design:
    st.markdown(f"<style>{source_design.read()}</style>", unsafe_allow_html=True)

ems = {
    "happy": "Радость",
    "angry": "Гнев",
    "disgust": "Отвращение",
    "surprise": "Удивление",
    "fear": "Страх",
    "sad": "Грусть",
    "neutral": "Нейтральность"
}

OPTIONS = ["С устройства", "С камеры", "По ссылке URL"]

if 'chosen' not in st.session_state:
    st.session_state['chosen'] = None
if 'img' not in st.session_state:
    st.session_state['img'] = None
if 'photo' not in st.session_state:
    st.session_state['photo'] = None


@st.cache_resource
def load_model():
    return FER(mtcnn=True)


def recognize_emotions(image, detector):
    captured_emotions = detector.detect_emotions(image)
    dominant_emotion, emotion_score = detector.top_emotion(image)
    return captured_emotions, dominant_emotion, emotion_score


def print_emotions(emotions, top_emotion, top_percent):
    if emotions:
        em = emotions[0]["emotions"]

        st.write("Наиболее вероятная эмоция:")
        st.write(f"{ems[top_emotion]} ({top_percent*100}%)")
        st.write("Другие возможные варианты:")
        k = 0
        for key in em:
            if em[key] > 0 and key != top_emotion:
                k += 1
                st.write(f"{ems[key]} ({em[key]*100}%)")
        if k == 0:
            st.write("Не обнаружено")
    else:
        st.error("К сожалению, не удалось распознать эмоции на фотографии. Попробуйте другое изображение")


detector = load_model()

st.title("Распознавание эмоций на фотографии")
load_option = st.radio(
    "Выберите способ загрузки изображения:",
    ("С устройства", "С камеры", "По ссылке URL"))
st.session_state['chosen'] = load_option

if st.session_state['chosen'] == OPTIONS[0]:  # Загрузка из файла
    image_data = load_options.from_device()
    if st.session_state['photo'] is None:
        st.session_state['photo'] = image_data
elif st.session_state['chosen'] == OPTIONS[1]:  # Загрузка с камеры
    image_data = load_options.from_camera()
    if st.session_state['photo'] is None:
        st.session_state['photo'] = image_data
elif st.session_state['chosen'] == OPTIONS[2]:
    result = load_options.from_url()  # Загрузка по ссылке
    if result:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(result)
        image_data = Image.open(BytesIO(result))
        url_data = temp_file.name
        if st.session_state['photo'] is None:
            st.session_state['photo'] = image_data

image_place = st.empty()

img = st.session_state['img']
# Отображение загруженного изображения, если есть
if st.session_state['photo'] is not None:
    with image_place:
        st.image(st.session_state['photo'])
        if st.session_state['img'] is None:
            try:
                img = plt.imread(st.session_state['photo'])
            except AttributeError:
                if url_data:
                    img = plt.imread(url_data)
            st.session_state['img'] = img

if st.session_state['img'] is not None:
    result = st.button("Распознать")
    if result:
        st.header('Результаты распознавания')
        with st.spinner('Подождите, пожалуйста...'):
            try:
                img = st.session_state['img']
                print_emotions(recognize_emotions(img, detector)[0], recognize_emotions(img, detector)[1], recognize_emotions(img, detector)[2])
                st.session_state['photo'] = None
                st.session_state['img'] = None
            except fer.exceptions.InvalidImage:
                st.session_state['photo'] = None
                st.session_state['img'] = None
                st.error("Изображение не было загружено")
            except RuntimeError:
                st.session_state['photo'] = None
                st.session_state['img'] = None
                st.error("Не удалось распознать лицо на фото. Попробуйте другое изображение.")

