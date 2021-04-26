from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from flask import Flask, redirect, render_template
import requests


#  Запуск и настройка приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
#  Все валидные символы
alphabet = {' ', 'а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у',
            'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я'}


#  Здесь создаётся форма для сайта
class SearchForm(FlaskForm):
    choice = SelectField("Выберете параметр поиска", choices=[("coord", "Координаты"),
                                                              ("name", "Название места")])
    input = StringField("Введите параметр")
    submit = SubmitField("Отправить")
    ans_name = StringField("Название места: ")
    ans_coord = StringField("Координаты места: ")
    map_global = StringField("Метка на глобальной карте")
    map_local = StringField("Метка на локальной карте")


#  Здесь перенаправляется на основную страницу при переходе по ссылке
@app.route('/')
def index():
    return redirect('/hubpage')


#  Основная часть программы
@app.route("/hubpage", methods=['GET', 'POST'])
def home():
    #  Создание формы
    form = SearchForm()
    # Очищение списка ошибок
    form.input.errors = []
    # Проверяет отправленна ли форма
    if form.is_submitted():
        #  Проверяет написано ли что-нибудь
        if form.input.data == "":
            form.input.errors.append("Ничего не написано!")
            return render_template("hubpage.html", form=form)
        #  Проверяет какой выбран параметр поиска
        if form.choice.data == "coord":
            #  Переводит полученную информацию в лист для дальнейшей обработки
            for i in [" ", ",", ";", "+", "-"]:
                code = form.input.data.split(i)
                # Если строка превратилась в лист с двумя элементами, то заканчивает цикл
                if len(code) == 2:
                    break
            #  Проверяет получился ли лист с двумя элементами
            if len(code) == 1:
                form.input.errors.append("Непонятные координаты")
                return render_template("hubpage.html", form=form)
            #  Проверяет цифры ли это
            if code[0].isdigit() is False or code[1].isdigit() is False:
                form.input.errors.append("Непонятные координаты")
                return render_template("hubpage.html", form=form)
            #  Получает информацию о месте
            code = ",".join(code)
            resp = requests.get(f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&"
                                f"geocode={code}&format=json").json()
            resp = resp["response"]["GeoObjectCollection"]["featureMember"]
            #  Проверяет выдали ли нам ответ на данный запрос
            if len(resp) == 0:
                form.input.errors.append("Места с такими координатами не существует!")
                return render_template("hubpage.html", form=form)
            #  Передача полученной информации в форму
            form.ans_name.errors = "Вот результат"
            form.ans_coord.errors = 1
            resp = resp[0]['GeoObject']
            form.ans_name.data = f"{resp['metaDataProperty']['GeocoderMetaData']['text']}"
            form.ans_coord.data = f"{' '.join(code.split(','))}"
            #  Передача ссылок на картинки с картой
            form.map_global = f"https://static-maps.yandex.ru/1.x/?ll={code}&spn=90,90&l=map&pt={code},flag"
            form.map_local = f"https://static-maps.yandex.ru/1.x/?ll={code}&spn=10,10&l=map&pt={code},flag"
        else:
            #  Подготовка к проверке
            t = set()
            for i in form.input.data.lower():
                t.add(i)
            #  Проверка на непонятные символы
            if len(t - alphabet) > 0:
                form.input.errors.append("В названии есть непонятные символы")
                return render_template("hubpage.html", form=form)
            #  Получает информацию о месте
            code = "+".join(form.input.data.split(" "))
            resp = requests.get(f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&"
                                f"geocode={code}&format=json").json()
            resp = resp["response"]["GeoObjectCollection"]["featureMember"]
            #  Проверяет выдали ли нам ответ на данный запрос
            if len(resp) == 0:
                form.input.errors.append("Места с таким именем не существует!")
                return render_template("hubpage.html", form=form)
            #  Передача полученной информации в форму
            form.ans_name.errors = "Вот результат"
            form.ans_coord.errors = 1
            resp = resp[0]['GeoObject']
            form.ans_name.data = f"{resp['metaDataProperty']['GeocoderMetaData']['text']}"
            coord = resp['Point']['pos']
            form.ans_coord.data = f"{coord}"
            #  Передача ссылок на картинки с картой
            coord = ','.join(coord.split(' '))
            form.map_global = f"https://static-maps.yandex.ru/1.x/?ll={coord}&" \
                              f"spn=90,90&l=map&pt={coord},flag"
            form.map_local = f"https://static-maps.yandex.ru/1.x/?ll={coord}&spn=10,10&l=map&" \
                             f"pt={coord},flag"
    #  Обнуление поля ввода
    form.input.data = ""
    return render_template("hubpage.html", form=form)


#  Сайт с небольшой сводкой
@app.route("/help")
def help_page():
    return render_template("help.html")


#  Запуск приложения
if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
