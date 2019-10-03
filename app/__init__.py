from flask import Flask, redirect, url_for, flash, render_template, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import login_required, logout_user, current_user, login_user
from sqlalchemy import desc
from sqlalchemy.orm.exc import NoResultFound
from app.config import Config
from app.models import db, login_manager, User, Token, Module, Profile, Order, Series, ModuleSeries, Image, ModuleReview
from app.oauth import blueprint
from app.cli import create_db
from data import rawdata
from datetime import datetime
import random
import uuid
from statistics import mean 


app = Flask(__name__)

CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config.from_object(Config)
app.register_blueprint(blueprint, url_prefix="/login")
app.cli.add_command(create_db)
db.init_app(app)
login_manager.init_app(app)

Migrate(app, db)


@app.route("/logout")
@login_required
def logout():
    token = Token.query.filter_by(user_id=current_user.id).first()
    if token:
        db.session.delete(token)
        db.session.commit()
        logout_user()
        resp = {'status': 200}
    else:
        resp = {'status': 300,
                'message': 'cannot log out'}
    return jsonify(resp)


@app.route('/test')
@login_required
def test():
    return jsonify({
        "status": 200,
        "message": "Success",
        "user_id": current_user.id,
        "user_name": current_user.name,
        "role": current_user.role,
        "first_name": current_user.profile.first_name,
        "img": current_user.profile.img
    })


@app.route('/register', methods=['GET', 'POST'])
def register():
    data = request.get_json()
    check_user = User.query.filter_by(email=data['email']).first()
    if check_user:
        return jsonify({
            "status": 400,
            "message": "User already exists"
        })
    new_user = User(email=data['email'],
                    name=data['name'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    new_profile = Profile(user_id=new_user.id)
    db.session.add(new_profile)
    db.session.commit()

    return jsonify({
        "status": 200})


@app.route('/login', methods=['GET', 'POST'])
def login():
    data = request.get_json('')
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        token = Token.query.filter_by(user_id=current_user.id).first()
        if not token:
            token = Token(user_id=current_user.id, uuid=str(uuid.uuid4().hex))
            db.session.add(token)
            db.session.commit()
        resp = {
            "status": 200,
            "token": token.uuid,
            'user': {'id': current_user.id,
                     'name': current_user.name,
                     'email': current_user.email}}

    else:
        resp = {"status": 400,
                "message": "Incorrect email/password"}
    return jsonify(resp)


@app.route('/modules')
@login_required
def modules():
    modules = Module.query.filter((Module.start_date > datetime.now()
                                   )).order_by(Module.start_date).all()
    # modules = Module.query.order_by(desc(Module.start_date)).all()
    resp = {
        "status": 200,
        'modules': [{'id': i.id,
                     'title': i.title,
                     'description': i.description,
                     'start_date': i.start_date,
                     'end_date': i.end_date,
                     'mentor': i.users.name,
                     'mentor_id': i.users.id,
                     'img': i.default_img,
                     } for i in modules]
    }
    return jsonify(resp)


@app.route('/create_a_json_object')
def create_moduless():
    modules = Module.query.all()
    resp = [{
        'title': i.title,
        'description': i.description,
        'price': i.price,
        'mentor_id': i.mentor_id,
        'end_date': i.end_date,
        'start_date': i.start_date,
        'default_img': i.default_img,
        'syllabus': i.syllabus
    } for i in modules]
    return jsonify(resp)


@app.route('/addsomething')
def addseomthing():
    for i in rawdata:
        new_users = User(name=i['first_name'],
                            email=i['email'],
                            password_hash=i['password'],
                            role="user",
                            )
        db.session.add(new_users)
        db.session.commit()

        new_profiles = Profile(user_id=new_user.id,
                                first_name=i['first_name'],
                                last_name=i['last_name'],
                                img=i['img'],
                                about=i['about'])

        db.session.add(new_profiles)
        db.session.commit()
    return 'ok'
# NOT WORKING


@app.route('/create_module', methods=['POST'])
@login_required
def create_module():
    module_data=request.get_json()
    new_module=Module(title=module_data['title'],
                        description=module_data['description'],
                        syllabus=module_data['syllabus'],
                        start_date=datetime.strptime(
                            module_data['startDate'], '%d-%m-%Y'),
                        end_date=datetime.strptime(
                            module_data['endDate'], '%d-%m-%Y'),
                        price=module_data['price'],
                        mentor_id=current_user.id,
                        default_img=module_data['img_url'])
    db.session.add(new_module)
    db.session.commit()

    resp={
        "status": 201,
        "message": "New module created"}

    return jsonify(resp)


@app.route('/modules/<id>', methods=['POST', 'GET'])
@login_required
def single_module(id):
    # module_data = request.get_json()
    module=Module.query.filter_by(id=id).first()
    if module:
        resp={
            "status": 200,
            'module': {'id': module.id,
                       'title': module.title,
                       'description': module.description,
                       'start_date': module.start_date,
                       'end_date': module.end_date,
                       'mentor': module.users.name,
                       'mentor_id': module.users.id,
                       'img': module.default_img,
                       'price': module.price,
                       "syllabus": module.syllabus}
        }

    else:
        resp={
            "status": 401,
            "message": "Error"}
    return jsonify(resp)


@app.route('/modules/<id>/edit', methods=['POST', 'GET'])
@login_required
def edit_module(id):
    edit_module=Module.query.filter_by(id=id).first()
    module_data=request.get_json()
    edit_module.title=module_data['title']
    edit_module.description=module_data['description']
    edit_module.syllabus=module_data['syllabus']
    edit_module.start_date=module_data['start_date']
    edit_module.end_date=module_data['end_date']
    edit_module.price=module_data['price']
    edit_module.mentor_id=current_user.id
    edit_module.default_img=module_data['img_url']
    db.session.commit()

    resp={
        "status": 201,
        "message": "Module successfully edited"}


@app.route('/modules/<id>/delete', methods=['POST', 'GET'])
@login_required
def delete_module(id):
    delete_module=Module.query.filter_by(id=id).first()
    if delete_module:
        db.session.delete(delete_module)
        db.session.commit()
        resp={
            "status": 200,
            "message": "Module has been deleted. Forever!"
        }
    else:
        resp={
            "status": 401,
            "message": "Error"}
    return jsonify(resp)

#list of the modules the target user has taught 
# mudles  = module filter by (mentor = target user.id).all()

#average review received for that target user
        #materials  from ModuleReview 
        #mentor_interaction
        #mentor_knowledge
@app.route('/profiles/<id>', methods=['GET'])
def profile(id):
    profile=Profile.query.filter_by(user_id=id).first()
    mod = Module.query.filter_by(mentor_id=id).all()
    if profile:
 
        resp = {
            "status": 200,
            'profile': {'id': profile.id,
                        'first_name': profile.first_name,
                        'last_name': profile.last_name,
                        'img': profile.img,
                        'about': profile.about,
                        'email': profile.email,
                        'role': profile.users.role
                        },
            'modules': [{'id': i.id,
                     'title': i.title,
                     'description': i.description,
                     'start_date': i.start_date,
                     'end_date': i.end_date,
                     'comments': [{'comments': x.comments, 'name': x.user.profile.first_name, 'img': x.user.profile.img} for x in i.module_review],
                     'reviews': {'materials': mean([j.materials if j.materials else 0 for j in i.module_review]) if len(i.module_review)>0 else 0,
                                    'knowledge': mean([j.mentor_knowledge if j.mentor_knowledge else 0 for j in i.module_review]) if len(i.module_review)>0 else 0 ,
                                    'interaction':mean([j.mentor_interaction if j.mentor_interaction else 0 for j in i.module_review]) if len(i.module_review)>0 else 0}
                                    # for j in i.module_review]
                    } for i in mod]
        }
        
        print(resp)
        return jsonify(resp)

    else:
        resp={
            "status": 401,
            "message": "Error"}
        return jsonify(resp)
    print(res)
    return "ok"


@app.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    profile=request.get_json()
    edited_profile=Profile(user_id=current_user.id,
                             first_name=profile['title'],
                             last_name=profile['last_name'],
                             img=profile['img'],
                             about=profile['about'],
                             email=profile['email'],
                             )
    db.session.add(edited_profile)
    db.session.commit()

    resp={
        "status": 201,
        "message": "Profile has been updated"}

    return jsonify(resp)


@app.route("/facebook-login")
def index():
    return redirect(url_for("facebook.login"))


@app.route('/reviews', methods=['GET'])
def asdad():
    datas = rawdata

    for i in range(100):
        reviews = ModuleReview(student_id=random.randint(15,76),
                                    module_id=random.randint(1,30),
                                    mentor_interaction=random.randint(7,11),
                                    mentor_knowledge=random.randint(7,11),
                                    materials=random.randint(7,11)
                                    )
        db.session.add(reviews)
        db.session.commit()
    
    return 'reviews addedddd'


    # for data in datas:
    #     new_user = User(email=data['email'],
    #                     name=data['first_name'])
    #     new_user.set_password(data['password'])
    #     db.session.add(new_user)
    #     db.session.commit()

    #     db.session.add(new_profile)
    #     db.session.commit()