from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from sqlalchemy import func
import os
import uuid

from models import db, User, Course, Material, Payment, Enrollment

load_dotenv()

app = Flask(__name__)

# Config
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
    f"@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'mp4', 'avi', 'mov', 'jpg', 'jpeg', 'png', 'txt', 'docx'}

CORS(app)
jwt = JWTManager(app)
db.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Helper
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# ---------------- AUTH ---------------- #

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'error': 'Username exists'}), 400

    user = User(
        username=data.get('username'),
        email=data.get('email'),
        phone=data.get('phone'),
        role=data.get('role', 'student'),
        password_hash=generate_password_hash(data.get('password'))
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({'msg': 'Registered'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(username=data.get('username')).first()

    if user and user.check_password(data.get('password')):
        token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify({'access_token': token})

    return jsonify({'error': 'Invalid credentials'}), 401


# ---------------- DASHBOARD ---------------- #

@app.route('/api/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])

    if current_user['role'] == 'teacher':
        total_students = db.session.query(Enrollment.student_id)\
            .filter(Enrollment.course_id.in_(
                db.session.query(Course.id).filter(Course.teacher_id == user.id)
            )).distinct().count()

        total_courses = Course.query.filter_by(teacher_id=user.id).count()

        earnings = db.session.query(func.sum(Payment.amount)).filter(
            Payment.course_id.in_(
                db.session.query(Course.id).filter(Course.teacher_id == user.id)
            ),
            Payment.status == 'confirmed'
        ).scalar() or 0

        return jsonify({
            'students': total_students,
            'courses': total_courses,
            'earnings': earnings
        })

    elif current_user['role'] == 'student':
        enrolled = Enrollment.query.filter_by(student_id=user.id).count()
        return jsonify({'enrolled': enrolled})

    elif current_user['role'] == 'admin':
        return jsonify({
            'teachers': User.query.filter_by(role='teacher').count(),
            'students': User.query.filter_by(role='student').count()
        })

    return jsonify({'error': 'Unauthorized'}), 403


# ---------------- COURSES ---------------- #

@app.route('/api/courses', methods=['GET', 'POST'])
@jwt_required()
def courses():
    current_user = get_jwt_identity()

    if request.method == 'POST':
        if current_user['role'] != 'teacher':
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()

        course = Course(
            teacher_id=current_user['id'],
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price', 0)
        )

        db.session.add(course)
        db.session.commit()

        return jsonify({'id': course.id})

    courses = Course.query.all()

    return jsonify([
        {'id': c.id, 'name': c.name, 'price': c.price}
        for c in courses
    ])


# ---------------- MATERIAL UPLOAD ---------------- #

@app.route('/api/materials/upload/<int:course_id>', methods=['POST'])
@jwt_required()
def upload_material(course_id):
    current_user = get_jwt_identity()

    if current_user['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403

    course = Course.query.get_or_404(course_id)

    if course.teacher_id != current_user['id']:
        return jsonify({'error': 'Not your course'}), 403

    file = request.files.get('file')

    if not file or file.filename == '':
        return jsonify({'error': 'No file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4()}_{filename}"

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))

    material = Material(
        course_id=course_id,
        file_path=unique_name
    )

    db.session.add(material)
    db.session.commit()

    return jsonify({'msg': 'Uploaded'})


# ---------------- ENROLL ---------------- #

@app.route('/api/enroll/<int:course_id>', methods=['POST'])
@jwt_required()
def enroll(course_id):
    current_user = get_jwt_identity()

    if current_user['role'] != 'student':
        return jsonify({'error': 'Only students'}), 403

    course = Course.query.get_or_404(course_id)

    # Prevent duplicate enrollment
    existing = Enrollment.query.filter_by(
        student_id=current_user['id'],
        course_id=course_id
    ).first()

    if existing:
        return jsonify({'error': 'Already enrolled'}), 400

    enrollment = Enrollment(
        student_id=current_user['id'],
        course_id=course_id
    )

    payment = Payment(
        student_id=current_user['id'],
        course_id=course_id,
        amount=course.price
    )

    db.session.add(enrollment)
    db.session.add(payment)
    db.session.commit()

    return jsonify({'msg': 'Enrolled successfully'})


# ---------------- MAIN ---------------- #

@app.route('/')
def index():
    return "API Running 🚀"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)