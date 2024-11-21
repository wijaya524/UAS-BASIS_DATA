from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import event, Table
from sqlalchemy.orm import validates
from datetime import datetime, timezone
import random

db = SQLAlchemy()

# Tabel asosiasi mahasiswa-jadwal
mahasiswa_jadwal = db.Table('mahasiswa_jadwal',
    db.Column('mahasiswa_nim', db.BigInteger, db.ForeignKey('mahasiswa_2395114030.nim'), primary_key=True),
    db.Column('jadwal_id', db.Integer, db.ForeignKey('jadwal_kuliah_2395114030.id_jadwal'), primary_key=True)
)

# Tabel asosiasi dosen-jadwal
dosen_jadwal = db.Table('dosen_jadwal',
    db.Column('dosen_nidn', db.BigInteger, db.ForeignKey('dosen_2395114030.nidn'), primary_key=True),
    db.Column('jadwal_id', db.Integer, db.ForeignKey('jadwal_kuliah_2395114030.id_jadwal'), primary_key=True)
)

class Mahasiswa_2395114030(UserMixin, db.Model):
    nim = db.Column(db.BigInteger, primary_key=True, autoincrement=True, unique=True)
    nama_mahasiswa = db.Column(db.String(100), nullable=False)
    alamat_mahasiswa = db.Column(db.String(255))
    tanggal_lahir = db.Column(db.Date)
    jenis_kelamin = db.Column(db.String(10))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    jadwal_kuliah = db.relationship('JadwalKuliah_2395114030', secondary=mahasiswa_jadwal, backref='mahasiswa')


    def get_id(self):
        return self.nim


class Dosen_2395114030(UserMixin, db.Model):
    nidn = db.Column(db.BigInteger, primary_key=True, autoincrement=True, unique=True)
    nama_dosen = db.Column(db.String(100), nullable=False)
    alamat_dosen = db.Column(db.String(255))
    no_telp_dosen = db.Column(db.String(15))

    jadwal_kuliah = db.relationship('JadwalKuliah_2395114030', secondary=dosen_jadwal, backref='dosen')



    def get_id(self):
        return self.nidn


class JadwalKuliah_2395114030(db.Model):
    id_jadwal = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hari = db.Column(db.String(20), nullable=False)
    jam_mulai = db.Column(db.Time, nullable=False)
    jam_selesai = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @validates('jam_selesai')
    def validate_jam_selesai(self, key, jam_selesai):
        if self.jam_mulai and jam_selesai <= self.jam_mulai:
            raise ValueError("Jam selesai harus lebih besar dari jam mulai.")
        return jam_selesai


@event.listens_for(Mahasiswa_2395114030, 'before_insert')
def generate_nim_before_insert(mapper, connection, target):
    if not target.nim:
        target.nim = generate_nim()


@event.listens_for(Dosen_2395114030, 'before_insert')
def generate_nidn_before_insert(mapper, connection, target):
    if not target.nidn:
        target.nidn = generate_nidn()


def generate_nim():
    random_digits = random.randint(10000000, 99999999)
    return int(f"23{random_digits}")


def generate_nidn():
    random_digits = random.randint(10000000, 99999999)
    return int(f"10{random_digits}")
