from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, ValidationError
from wtforms.validators import DataRequired
from flask import Flask, redirect, render_template
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
alphabet = {' ', 'а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у',
            'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я'}


def check(form, field):
    if form.choice.data == "coord":
        for i in [" ", ",", ";", "+", "-"]:
            t = field.data.split(i)
            if len(t) == 2:
                break
        if len(t) == 1:
            return
        resp = requests.get(f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&"
                            f"geocode={t}&format=json").json()["response"]["GeoObjectCollection"]["featureMember"]
        if len(resp) == 0:
            raise ValidationError("Места с такими координатами не существует!")
    else:
        t = "+".join(field.data.split(" "))
        resp = requests.get(f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&"
                            f"geocode={t}&format=json").json()["response"]["GeoObjectCollection"]["featureMember"]
        if len(resp) == 0:
            raise ValidationError("Места с таким именем не существует!")


class SearchForm(FlaskForm):
    choice = SelectField("Выберете параметр поиска", choices=[("coord", "Координаты"),
                                                              ("name", "Название места")])
    input = StringField("Введите параметр")
    submit = SubmitField("Отправить")
    ans_name = StringField("Название места: ")
    ans_coord = StringField("Координаты места: ")
    map_global = StringField("Метка на глобальной карте")
    map_local = StringField("Метка на локальной карте")


@app.route('/')
def index():
    return redirect('/hubpage')


@app.route("/hubpage", methods=['GET', 'POST'])
def home():
    form = SearchForm()
    form.input.errors = []
    if form.is_submitted():
        if form.input.data == "":
            form.input.errors.append("Ничего не написано!")
            return render_template("hubpage.html", form=form)
        if form.choice.data == "coord":
            for i in [" ", ",", ";", "+", "-"]:
                code = form.input.data.split(i)
                if len(code) == 2:
                    break
            if len(code) == 1:
                form.input.errors.append("Непонятные координаты")
                return render_template("hubpage.html", form=form)
            code = ",".join(code)
            resp = requests.get(f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&"
                                f"geocode={code}&format=json").json()
            resp = resp["response"]["GeoObjectCollection"]["featureMember"]
            if len(resp) == 0:
                form.input.errors.append("Места с такими координатами не существует!")
                return render_template("hubpage.html", form=form)
            form.ans_name.errors = "Вот результат"
            form.ans_coord.errors = 1
            resp = resp[0]['GeoObject']
            form.ans_name.data = f"{resp['metaDataProperty']['GeocoderMetaData']['text']}"
            form.ans_coord.data = f"{' '.join(code.split(','))}"
            form.map_global = f"https://static-maps.yandex.ru/1.x/?ll={code}&spn=90,90&l=map&pt={code},flag"
            form.map_local = f"https://static-maps.yandex.ru/1.x/?ll={code}&spn=10,10&l=map&pt={code},flag"
        else:
            t = set()
            for i in form.input.data.lower():
                t.add(i)
            if len(t - alphabet) > 0:
                form.input.errors.append("В названии есть непонятные символы")
                return render_template("hubpage.html", form=form)
            code = "+".join(form.input.data.split(" "))
            resp = requests.get(f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&"
                                f"geocode={code}&format=json").json()
            resp = resp["response"]["GeoObjectCollection"]["featureMember"]
            if len(resp) == 0:
                form.input.errors.append("Места с таким именем не существует!")
                return render_template("hubpage.html", form=form)
            form.ans_name.errors = "Вот результат"
            form.ans_coord.errors = 1
            resp = resp[0]['GeoObject']
            form.ans_name.data = f"{resp['metaDataProperty']['GeocoderMetaData']['text']}"
            coord = resp['Point']['pos']
            form.ans_coord.data = f"{coord}"
            coord = ','.join(coord.split(' '))
            form.map_global = f"https://static-maps.yandex.ru/1.x/?ll={coord}&" \
                              f"spn=90,90&l=map&pt={coord},flag"
            form.map_local = f"https://static-maps.yandex.ru/1.x/?ll={coord}&spn=10,10&l=map&" \
                             f"pt={coord},flag"
    form.input.data = ""
    return render_template("hubpage.html", form=form)


@app.route("/help")
def help_page():
    return render_template("help.html")


@app.route("/ok")
def good():
    return "Worked!"


if __name__ == '__main__':
    logined = False
    app.run(port=8080, host='127.0.0.1')
