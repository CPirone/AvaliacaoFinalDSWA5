import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name = StringField('Cadastre o novo Professor:', validators=[DataRequired()])
    role = SelectField('Disciplina associada:', choices=[('DSWA5', 'DSWA5'), ('GPSA5', 'GPSA5'), ('IHCA5', 'IHCA5'), ('SODA5', 'SODA5'), ('PJIA5', 'PJIA5'), ('TCOA5', 'TCOA5')], validators=[DataRequired()])
    submit = SubmitField('Cadastrar')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.before_first_request
def create_roles():
    roles = ['DSWA5', 'IHCA5', 'GPSA5', 'SODA5', 'PJIA5', 'TCOA5']
    for role_name in roles:
        role = Role.query.filter_by(name=role_name).first()
        if role is None:
            new_role = Role(name=role_name)
            db.session.add(new_role)
    db.session.commit()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def prontuario():
    return render_template('index.html')


@app.route('/cadastro_professores', methods=['GET', 'POST'])
def cadastro_professores():
    form = NameForm()
    user_all = User.query.all()
    role_all = Role.query.all()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user_role = Role.query.filter_by(name=form.role.data).first()
            if user_role is None:
                flash('Disciplina não encontrada.', 'danger')
            else:
                user = User(username=form.name.data, role=user_role)
                db.session.add(user)
                db.session.commit()
                flash('Professor cadastrado com sucesso!', 'success')
                session['known'] = False
        else:
            flash('Professor já existe na base de dados!', 'info')
            session['known'] = True

        session['name'] = form.name.data
        return redirect(url_for('cadastro_professores'))

    return render_template('cadastro_professores.html', form=form, name=session.get('name'),
                           known=session.get('known', False),
                           user_all=user_all,
                           role_all=role_all)


@app.route('/disciplinas')
@app.route('/alunos')
def not_available():
    return render_template('nao_disponivel.html')


if __name__ == '__main__':
    app.run(debug=True)
