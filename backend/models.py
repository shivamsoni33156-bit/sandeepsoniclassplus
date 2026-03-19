from backend.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


# ---------------- USER ---------------- #
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')
    phone = db.Column(db.String(15))

    # Relationships
    courses = db.relationship('Course', backref='teacher', lazy=True, cascade="all, delete")
    enrollments = db.relationship('Enrollment', backref='student', lazy=True, cascade="all, delete")
    payments = db.relationship('Payment', backref='student', lazy=True, cascade="all, delete")

    # Password Methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ---------------- COURSE ---------------- #
class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0.0)

    materials = db.relationship('Material', backref='course', lazy=True, cascade="all, delete")
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade="all, delete")
    payments = db.relationship('Payment', backref='course', lazy=True, cascade="all, delete")


# ---------------- ENROLLMENT ---------------- #
class Enrollment(db.Model):
    __tablename__ = 'enrollment'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete="CASCADE"), nullable=False)

    enrolled_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),
    )


# ---------------- MATERIAL ---------------- #
class Material(db.Model):
    __tablename__ = 'material'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete="CASCADE"), nullable=False)

    subject = db.Column(db.String(100))
    chapter = db.Column(db.String(100))

    file_path = db.Column(db.String(500))
    file_type = db.Column(db.String(50))


# ---------------- PAYMENT ---------------- #
class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete="CASCADE"), nullable=False)

    amount = db.Column(db.Float, nullable=False)

    upi_ref = db.Column(db.String(100))
    receipt_path = db.Column(db.String(500))

    status = db.Column(db.String(20), default='pending', index=True)

    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, onupdate=db.func.current_timestamp())


# ---------------- TEST ---------------- #
class Test(db.Model):
    __tablename__ = 'test'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete="CASCADE"), nullable=False)

    title = db.Column(db.String(200))
    questions = db.Column(db.Text)  # safer for MySQL compatibility