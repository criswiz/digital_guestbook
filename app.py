from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from flask_bootstrap import Bootstrap

# Flask WTF
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email


class GuestbookForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])


app = Flask(__name__)

# Configure the SQLite database URI
# SQLite database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///guestbook.db'
app.secret_key = '8abb191586453f50cd47b9f13caa2ae8'

db = SQLAlchemy(app)

# Initialize Flask-Bootstrap
bootstrap = Bootstrap(app)

# Define the model for your guestbook entries


class GuestEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)


@app.route('/', methods=['GET', 'POST'])
def guestbook_form():
    form = GuestbookForm()
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        message = request.form['message']

        # Perform server-side validation here
        if not email or not name or not message:
            flash('All fields are required', 'error')
        else:
            # Data is valid, insert it into the database
            try:
                entry = GuestEntry(email=email, name=name, message=message)
                db.session.add(entry)
                db.session.commit()
                flash('Entry added to the guestbook', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('An error occurred while adding the entry', 'error')

        return redirect(url_for('guestbook_form'))

    return render_template('guestbook_form.html', form=form)


@app.route('/view_guestbook', methods=['GET'])
def view_guestbook():
    filter_name = request.args.get('filter')
    sort_option = request.args.get('sort')

    entries_query = GuestEntry.query

    if filter_name:
        entries_query = entries_query.filter(func.lower(
            GuestEntry.name).contains(filter_name.lower()))

    if sort_option == 'name_asc':
        entries_query = entries_query.order_by(GuestEntry.name)
    elif sort_option == 'name_desc':
        entries_query = entries_query.order_by(GuestEntry.name.desc())
    elif sort_option == 'date_asc':
        entries_query = entries_query.order_by(GuestEntry.id)
    elif sort_option == 'date_desc':
        entries_query = entries_query.order_by(GuestEntry.id.desc())

    entries = entries_query.all()

    return render_template('view_guestbook.html', entries=entries)


if __name__ == '__main__':
    app.run(debug=True)
