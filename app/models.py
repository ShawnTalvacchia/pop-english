from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    email = db.Column(db.String(256))
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(256), default='user')
    profile = db.relationship(
        "Profile", backref="users", lazy=True, uselist=False)
    mentor_for = db.relationship("Module", backref="users", lazy=True)
    enrolled = db.relationship("Enrolled", backref="users", lazy=True)
    orders = db.relationship("Order", backref="users")
    module_reviews = db.relationship(
        "ModuleReview", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    img = db.Column(db.String(2500))
    about = db.Column(db.String(3000))
    email = db.Column(db.String(256))
    dob = db.Column(db.DateTime)

    def role(self):
        return self.users.role


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User)


class Enrolled(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey(
        'module.id'), nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey(
        'module.id'), nullable=False)
    date = db.Column(db.DateTime)
    total_bill = db.Column(db.Float)


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    description = db.Column(db.String(2000))
    syllabus = db.Column(db.String(2000))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    price = db.Column(db.Float)
    mentor_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    enrolled = db.relationship("Enrolled", backref="module")
    orders = db.relationship("Order", backref="module")
    module_review = db.relationship(
        "ModuleReview", backref="module", lazy=True)
    module_series = db.relationship(
        "ModuleSeries", backref="module", lazy=True)
    images = db.relationship("Image", backref="module", lazy=True)
    default_img = db.Column(db.String(1000))

    def enrolled(self):
        return self.enrolled.user_id


class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    description = db.Column(db.String(2000))
    module_series = db.relationship(
        "ModuleSeries", backref="series", lazy=True)
    images = db.relationship("Image", backref="series", lazy=True)


class ModuleSeries(db.Model):  # module_series
    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey(
        'series.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey(
        'module.id'), nullable=False)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    url = db.Column(db.String(3000))
    series_id = db.Column(db.Integer, db.ForeignKey(
        'series.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey(
        'module.id'), nullable=False)


class ModuleReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey(
        'module.id'), nullable=False)
    materials = db.Column(db.Integer)
    mentor_interaction = db.Column(db.Integer)
    mentor_knowledge = db.Column(db.Integer)
    comments = db.Column(db.String(2000))
    date = db.Column(db.DateTime)

    def student_name(self):
        return self.user.name

    def mentor_name(self):
        return self.module.users.mentor_for


login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.request_loader
def load_user_from_request(request):
    # Login Using our Custom Header
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Token ', '', 1)
        print('dsadsadsa', 142)
        token = Token.query.filter_by(uuid=api_key).first()
        if token:
            print('dsadsadsa', 145)

            return token.user

    return None
