from datetime import datetime
from random import randint
import sqlite3
from flask import Flask, render_template, request, redirect, flash, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
import requestsc
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Library.db'
db = SQLAlchemy(app)
app.secret_key = 'your_secret_key'
migrate = Migrate(app, db)

class Rooms(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Set as primary key
    book_name = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(75), nullable=False)
    publisher = db.Column(db.String(75), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)  # Add default value
    borrower = db.Column(db.Integer, nullable=True)
    isbn = db.Column(db.String(15), nullable=True)
    times_issued = db.Column(db.Integer, default=0)
  
class Members(db.Model):
    # Table members => | member_id | member_name | member_balance | member_borrowed | library_fees_given |
    member_id = db.Column(db.Integer , primary_key = True)
    member_name = db.Column(db.String(150))
    member_balance = db.Column(db.Float , default = 1000)
    role = db.Column(db.String(50), default='Customer,')  # New column for roles
    member_borrowed = db.Column(db.Boolean, default = False)
    library_fees_given = db.Column(db.Float , default = 0)
    password = db.Column(db.String(200), nullable=False)
  
class Transactions(db.Model):
    __tablename__ = 'transactions'
    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Add this as primary key
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    book_name = db.Column(db.String(150), nullable=False)
    member_name = db.Column(db.String(150), nullable=False)
    direction = db.Column(db.Boolean, nullable=False)  # True for return, False for issue
    time = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
@app.route('/', methods=["GET", "POST"])

def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        member = Members.query.filter_by(member_name=username).first()
        if member and check_password_hash(member.password, password):
            session['member_id'] = member.member_id
            session['role'] = member.role
            session['name'] = member.member_name
            session['pass']=    password
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')
  
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        if Members.query.filter_by(member_name=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))
        new_member = Members(member_name=username, password=hashed_password,
                             role='Customer')
        db.session.add(new_member)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/home')
def home():
    if 'role' not in session:
        return redirect(url_for('login'))
    available_books = Rooms.query.all()
    print(available_books)
    return render_template('home.html', books=available_books, session=session)


@app.route('/members', methods = ["POST" , "GET"])
def members():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        if Members.query.filter_by(member_name=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))
        new_member = Members(member_name=username, password=hashed_password,
                             role='Customer')
        db.session.add(new_member)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('members'))

    members = Members.query.filter_by(role="Customer")
    return render_template('members.html', members = members)


@app.route('/moderators', methods=["POST", "GET"])
def moderators():

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        if Members.query.filter_by(member_name=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('moderators'))
        new_member = Members(member_name=username, password=hashed_password,role='Moderator')
        db.session.add(new_member)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('moderators'))
    # no matter if the method is GET or POST e need to render the available member list.
    members = Members.query.filter_by(role="Moderator")  # Getting all the members
    return render_template('moderators.html', members=members)  # rendering the page for members


# this function loads all the transactons
@app.route('/transactions')
def transactions():
    transactions = Transactions.query.order_by(Transactions.time.desc()).all() 
    return render_template('transactions.html', transactions = transactions)


# Renders Analytics Page
@app.route('/analytics')
def analytics():
    popular_books = Rooms.query.order_by(Rooms.times_issued.desc()).limit(5).all()
    top_spenders  = Members.query.order_by(Members.library_fees_given.desc()).limit(5).all()
    return render_template('analytics.html', books = popular_books , people = top_spenders)


@app.route('/rent_out/<int:book_id>', methods=["POST", "GET"])
def rent_out(book_id):
    all_members = Members.query.filter(Members.member_borrowed == False).all()

    if request.method == "POST":
        # Check if the user is a Customer and logged in
        if session.get('role') == "Customer":
            id_of_the_member = session.get('member_id')
            if not id_of_the_member:
                flash("Member not logged in. Please log in to rent out a book.", "danger")
                return redirect(url_for('login'))
        else:
            id_of_the_member = request.form.get('id')

        # Validate member
        member = Members.query.get(id_of_the_member)
        if not member:
            return render_template('error.html', message="Invalid Member!")

        # Check member's balance
        if member.member_balance < -500:
            message = (
                f'The balance of {member.member_name} is {member.member_balance}, '
                f'which is less than -500. Please add money to your wallet before renting books.'
            )
            return render_template('error.html', message=message)

        # Check if the member has already borrowed a book
        if member.member_borrowed:
            return render_template('error.html', message="The user has already taken books.")

        # Update member and book details
        member.member_borrowed = True
        member.member_balance -= 500
        member.library_fees_given += 500

        book = Rooms.query.get(book_id)
        if not book:
            return render_template('error.html', message="Unexpected Error Occurred.")

        book.quantity = 0
        book.times_issued += 1
        book.borrower = member.member_id

        # Create a transaction
        trans = Transactions(
            book_id=book.book_id,
            member_id=member.member_id,
            book_name=book.book_name,
            member_name=member.member_name,
            direction=False
        )

        db.session.add(trans)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('rent_out.html', id=book_id, members=all_members)


@app.route('/addBooks', methods=["POST", "GET"])
def addBooks():
    if request.method == "POST":
        response = make_API_call()
        for data in response:
            book_id = int(data["bookID"])
            to_find = Rooms.query.get(book_id)
            if to_find is None:
                book = Rooms(
                    book_id=book_id,
                    book_name=data["title"],
                    author=data["authors"],
                    publisher=data["publisher"],
                    isbn=data["isbn"],
                    quantity=data.get("quantity", 1)  # Set a default value if not provided
                )
                db.session.add(book)
                db.session.commit()
                return redirect(url_for('addBooks'))
        return redirect(url_for('home'))
    return render_template("add_books.html")


@app.route('/addCustomBooks', methods=["POST"])
def add_custom_books():
    if request.method == "POST":
        book_id = request.form['book_id']
        book_name = request.form['book_name']
        author = request.form['author']
        publisher = request.form['publisher']
        isbn = request.form['isbn'] or 404
        if not book_id.isnumeric():
            return render_template(
                                'error.html',
                                message = "Please enter a valid book ID"
                                )

        book_id = int(book_id)
        if Rooms.query.get(book_id) != None:
            return render_template('error.html', message = "Book Id already Exists in DB")
        try:
            book = Rooms(
                        book_id = book_id,
                        book_name = book_name,
                        author = author,
                        publisher = publisher,
                        isbn = isbn
                        )  # I made it with good indent sir!!!

            db.session.add(book)
            db.session.commit()
            return redirect(url_for('home'))

        except:
            return render_template('error.html', message = "Unexpected Error")


    else:
        return render_template('error.html', message = "NOT AUTHORIZED")

@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        book = Rooms.query.get(book_id)
        if book:
            order = Transactions.query.filter_by(

                member_id=session['member_id'],
                book_name=book.book_name,
                direction=False
            ).first()
            if order:
                order.direction = True
                user=Members.query.filter_by(
                    member_id=session['member_id']
                ).first()
                book.borrower=-1
                book.quantity+=1
                user.member_borrowed=False
                db.session.commit()
                flash('Book returned successfully!', 'success')
                return redirect(url_for('home'))
            else:
                flash('You have not borrowed this book or it has already been returned.', 'danger')

    ordered_books = db.session.query(Rooms).join(Transactions).filter(
        Transactions.member_id == session['member_id'],
        Transactions.direction == False,
        Transactions.book_id == Rooms.book_id
    ).all()
    return render_template('return_book.html', books=ordered_books)
@app.route('/summary/<int:id>')
def summary(id):
    book = Rooms.query.get(id)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('home'))

    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for('home'))

    book.quantity = 1

    member = None
    if book.borrower != -1:
        member = Members.query.get(book.borrower)

    if not member:
        flash("Member not found or borrower ID is invalid.", "danger")
        return redirect(url_for('home'))

    old_trans = Transactions.query.filter(
        Transactions.book_id == book.book_id,
        Transactions.member_name == member.member_name,
        Transactions.direction == False
    ).first()

    if not old_trans or not old_trans.time:
        flash('Transaction not found or invalid time.', 'danger')
        return redirect(url_for('home'))
    trans = Transactions(
        book_id=book.book_id,
        book_name=book.book_name,
        member_id=member.member_id,
        member_name=member.member_name,
        direction=True,
        time=datetime.utcnow()
    )

    db.session.add(trans)
    book.borrower = -1

    charges = (datetime.utcnow() - old_trans.time).days * 10

    if member.member_balance >= charges:
        member.member_balance -= charges
        member.library_fees_given += charges
    else:
        flash('Insufficient balance to  deduct charges.', 'danger')
        return redirect(url_for('home'))

    member.member_borrowed = False
    db.session.commit()
    return render_template('summary.html', member=member)


@app.route('/delete_member/<int:id>')
def delete(id):

    try:
        task_to_delete =  Members.query.get(id)
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/members')

    except:

        return render_template('error.html', message = "Unexpected Error Occured")


@app.route('/update/<int:id>', methods = ["POST", "GET"])
def update(id):

    if request.method == "POST":
        try:

            user = Members.query.get(id)
            user.member_balance += float(request.form['amount'])
            db.session.commit()
            return redirect(url_for('members'))

        except:

            return render_template('error.html', message = "Unexpected Error Occured")
    else:
        return render_template('update.html', id = id)

def is_alphabets(s : str):
    return ''.join(s.split()).isalpha()

def remove_spaces(s : str):
    return ' '.join(s.split())


def make_API_call():
    BASE_URL = 'https://frappe.io/api/method/frappe-library?'

    title = remove_spaces(request.form['title'])
    authors = remove_spaces(request.form['author'])
    publisher = remove_spaces(request.form['publisher'])
    isbn = request.form['isbn']
    end = ''
    if title or authors or isbn or publisher:
        end = f'title={title}&authors={authors}&isbn={isbn}publisher={publisher}'
        response = requests.get(BASE_URL + end).json()['message']
    else:
        response = requests.get(BASE_URL + f'page={randint(1, 200)}').json()['message']
    return response


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
