from flask import Flask, flash, session, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Film(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50), nullable = False)
    text = db.Column(db.Text, nullable = False)
    def __repr__(self):
        return '<Film %r>' % self.id

menu = [{'name': 'Главная', 'url': 'index'},{'name': 'Новинки', 'url': 'newfilm'},
        {'name': 'Все фильмы', 'url': 'filmlist'},{'name': 'Профиль', 'url': 'login.html'}]

users = [{'user': 'user', 'psw': 'pswrd'}]

@app.route('/')
def index():
    return render_template('index.html',menu=menu, title='Главная')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'userlogged' in session:
        return redirect(url_for('profile', username=session['userlogged']))
    elif request.method == "POST" and request.form['username'] == 'Kagi' and request.form['psw'] == '123':
        session['userlogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userlogged']))
    return render_template('login.html')


@app.route('/profile/<username>')
def profile(username):
    if 'userlogged' not in session or session['userlogged'] != username:
        abort(401)
    else:
        f"<h1> Пользователь: {username} </h1>"

@app.route('/newfilm')
def newfilm():
    return render_template('newfilm.html',menu=menu, title='Новые фильмы')

@app.route('/filmlist')
def filmlist():
    films = Film.query.order_by(Film.id).all()
    return render_template('filmlist.html',films=films ,menu=menu, title='Список фильмов')

@app.route('/filmlist/<int:id>')
def film_watch(id):
    film = Film.query.get(id)
    return render_template('filmwatch.html',film = film)


@app.route('/filmlist/<int:id>/del')
def film_del(id):
    film = Film.query.get_or_404(id)
    try:
        db.session.delete(film)
        db.session.commit()
        return redirect('/filmlist')
    except:
        return "Ошибка удаления"


@app.route('/filmlist/<int:id>/up', methods = ['POST', 'GET'])
def film_up(id):
    film = Film.query.get(id)
    if request.method == "POST":
        film.title = request.form['title']
        film.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/filmlist')
        except:
            return "Ошибка"
    else:
        return render_template('film_up.html', film=film)

@app.route('/profile/CreateFilm', methods = ['POST', 'GET'])
def CreateFilm():
    if request.method == "POST":
        title = request.form['title']
        text = request.form['text']

        film = Film(title=title, text=text)
        try:
            db.session.add(film)
            db.session.commit()
            return redirect('/filmlist')
        except:
            return "Ошибка создания"
    else:
        return render_template('CreateFilm.html',menu=menu, title='Добавление фильма')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Внимание страница не найдена', menu=menu, error = error), 404

@app.errorhandler(401)
def unauthorized(error):
    return render_template('page401.html', title='Внимание отказано в доступе', menu=menu, error=error), 401