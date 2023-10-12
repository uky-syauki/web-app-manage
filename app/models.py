from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    def __repr__(self):
        return self.username
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return Admin.query.get(int(id))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    jumlah_hadir = db.Column(db.Integer, default=0)
    dataset = db.Column(db.Boolean(), default=False)
    face_prediksi = db.Column(db.Integer, default=0)
    absensi = db.relationship('Absen', back_populates='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'
    def daftar_user(self):
        daftar = User.query.all()


class Pertemuan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)
    materi = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    absensi = db.relationship('Absen', back_populates='pertemuan', lazy='dynamic')

    def __repr__(self):
        return f'<Pertemuan {self.title}>'


class Absen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean, default=False)
    pertemuan_id = db.Column(db.Integer, db.ForeignKey('pertemuan.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    pertemuan = db.relationship('Pertemuan', back_populates='absensi')
    user = db.relationship('User', back_populates='absensi')

    def __repr__(self):
        return f'<Absen {self.pertemuan} - {self.user}>'



