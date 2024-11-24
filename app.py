from datetime import datetime
from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import random
from models import Dosen_2395114030, JadwalKuliah_2395114030, db, Mahasiswa_2395114030, generate_nidn, generate_nim

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/testing_uas'

db.init_app(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login_mahasiswa'

#User Loader
@login_manager.user_loader
def load_user(user_id):
      # Coba muat user sebagai Mahasiswa
    user = Mahasiswa_2395114030.query.filter_by(nim=user_id).first()
    if user:
        return user
    # Coba muat sebagai jadwal
    jadwal = JadwalKuliah_2395114030.query.filter_by(id_jadwal=user_id).first()
    if jadwal:
        return jadwal
    # Jika tidak ditemukan, coba sebagai Dosen
    return Dosen_2395114030.query.filter_by(nidn=user_id).first()

# def generate_nim():
#     """Generate NIM otomatis dengan awalan 23 dan total panjang 10 digit."""
#     random_digits = random.randint(10000000, 99999999)
#     return int(f"23{random_digits}")

@app.route("/")
def index():
    return render_template("index.html")

#Register Mahasiswa
@app.route('/register_mahasiswa', methods=['GET', 'POST'])
def register_mahasiswa():
    if request.method == 'POST':
        nama_mahasiswa = request.form['nama_mahasiswa']
        alamat_mahasiswa = request.form['alamat_mahasiswa']
        tanggal_lahir = request.form['tanggal_lahir']
        jenis_kelamin = request.form['jenis_kelamin']

        if not nama_mahasiswa or not alamat_mahasiswa or not tanggal_lahir or not jenis_kelamin:
            flash('Semua field harus diisi.', 'danger')
            return redirect(url_for('register_mahasiswa'))

        # Generate NIM otomatis
        nim = generate_nim()

        new_user = Mahasiswa_2395114030(
            nim=nim,
            nama_mahasiswa=nama_mahasiswa,
            alamat_mahasiswa=alamat_mahasiswa,
            tanggal_lahir=tanggal_lahir,
            jenis_kelamin=jenis_kelamin,
        )

        db.session.add(new_user)
        db.session.commit()

        session['nim'] = nim

        flash(f'Registrasi berhasil! NIM Anda: {nim}', 'success')
        return redirect(url_for('register_mahasiswa_success'))
    return render_template('templates_mahasiswa/register_mahasiswa.html')

#Login Mahasiswa
@app.route('/login_mahasiswa', methods=['GET', 'POST'])
def login_mahasiswa():
    if request.method == 'POST':
        nim = request.form.get('nim')

        # Validasi input pengguna
        if not nim:
            flash('NIM harus diisi.', 'danger')
            return redirect(url_for('login_mahasiswa'))

        # Cari user berdasarkan NIM
        user = Mahasiswa_2395114030.query.filter_by(nim=nim).first()
        if user: 
            login_user(user)
            flash('Login berhasil!', 'success')
            return redirect(url_for('profile_mahasiswa'))
        else:
            flash('NIM atau salah.', 'danger')
            return redirect(url_for('login_mahasiswa'))

    return render_template('templates_mahasiswa/login_mahasiswa.html')

#Edit Mahasiswa 
@app.route('/edit_mahasiswa', methods=['GET', 'POST'])
@login_required
def edit_mahasiswa():
    # Menggunakan current_user untuk mendapatkan mahasiswa yang sedang login
    mahasiswa = current_user

    if request.method == 'POST':
        # Ambil data dari form
        nama_mahasiswa = request.form.get('nama_mahasiswa')
        alamat_mahasiswa = request.form.get('alamat_mahasiswa')
        tanggal_lahir = request.form.get('tanggal_lahir')
        jenis_kelamin = request.form.get('jenis_kelamin')

        # Validasi input
        if not nama_mahasiswa or not alamat_mahasiswa or not tanggal_lahir or not jenis_kelamin:
            flash('Semua field harus diisi.', 'danger')
            return redirect(url_for('edit_mahasiswa'))

        try:
            # Update data mahasiswa
            mahasiswa.nama_mahasiswa = nama_mahasiswa
            mahasiswa.alamat_mahasiswa = alamat_mahasiswa
            mahasiswa.tanggal_lahir = datetime.strptime(tanggal_lahir, '%Y-%m-%d').date()
            mahasiswa.jenis_kelamin = jenis_kelamin

            db.session.commit()
            flash('Data mahasiswa berhasil diperbarui.', 'success')
            return redirect(url_for('profile_mahasiswa'))
        except Exception as e:
            flash(f'Kesalahan: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('templates_mahasiswa/edit_mahasiswa.html', mahasiswa=mahasiswa)



#Profile Mahasiswa
@app.route('/profile_mahasiswa')
@login_required
def profile_mahasiswa():
    # Ambil semua jadwal milik mahasiswa yang sedang login
    jadwal_list = current_user.jadwal_kuliah
    
    # Hitung total durasi
    total_minutes = 0
    for jadwal in jadwal_list:
        jam_mulai = datetime.strptime(str(jadwal.jam_mulai), '%H:%M:%S')
        jam_selesai = datetime.strptime(str(jadwal.jam_selesai), '%H:%M:%S')
        duration = (jam_selesai - jam_mulai).seconds // 60  # Dalam menit
        total_minutes += duration
    
    total_hours = total_minutes // 60
    remaining_minutes = total_minutes % 60

    return render_template(
        'templates_mahasiswa/profile_mahasiswa.html',
        jadwal_list=jadwal_list,
        total_hours=total_hours,
        remaining_minutes=remaining_minutes
    )


#Sukses register mahasiswa
@app.route('/register_mahasiswa_success')
def register_mahasiswa_success():
    nim = session.get('nim')
    return render_template('templates_mahasiswa/register_mahasiswa_success.html', nim=nim)



#Register Dosen
@app.route('/register_dosen', methods=['GET', 'POST'])
def register_dosen():
    if request.method == 'POST':
        nama_dosen = request.form['nama_dosen']
        alamat_dosen = request.form['alamat_dosen']
        no_telp_dosen = request.form['no_telp_dosen']

        if not nama_dosen or not  alamat_dosen or not no_telp_dosen:
            flash('Semua field harus diisi.', 'danger')
            return redirect(url_for('register_mahasiswa'))

        # Generate NIDN otomatis
        nidn = generate_nidn()

        new_user = Dosen_2395114030(
            nidn=nidn,
            nama_dosen=nama_dosen,
            alamat_dosen=alamat_dosen,
            no_telp_dosen=no_telp_dosen,
        )

        db.session.add(new_user)
        db.session.commit()

        session['nidn'] = nidn

        flash(f'Registrasi berhasil! NIDN Anda: {nidn}', 'success')
        return redirect(url_for('register_dosen_success'))
    return render_template('templates_dosen/register_dosen.html')


#Login Dosen
@app.route('/login_dosen', methods=['GET', 'POST'])
def login_dosen():
    if request.method == 'POST':
        nidn = request.form.get('nidn')

        # Validasi input pengguna
        if not nidn :
            flash('NIM harus diisi.', 'danger')
            return redirect(url_for('login_dosen'))

        # Cari user berdasarkan NIM
        user = Dosen_2395114030.query.filter_by(nidn=nidn).first()
        if user :  
            login_user(user)
            flash('Login berhasil!', 'success')
            print(f"Logged in user: {current_user.nama_dosen}") 
            return redirect(url_for('profile_dosen'))
        else:
            flash('NIDN salah.', 'danger')
            return redirect(url_for('login_dosen'))

    return render_template('templates_dosen/login_dosen.html')


#Edit dosen
# Edit Dosen
@app.route('/edit_dosen/<int:nidn>', methods=['GET', 'POST'])
@login_required
def edit_dosen(nidn):
    # Cari dosen berdasarkan NIDN
    dosen = Dosen_2395114030.query.get_or_404(nidn)

    # Periksa apakah pengguna saat ini memiliki akses
    if current_user.nidn != dosen.nidn:
        flash('Anda tidak memiliki akses untuk mengedit data ini.', 'danger')
        return redirect(url_for('profile_dosen'))

    if request.method == 'POST':
        # Ambil data dari form
        nama_dosen = request.form.get('nama_dosen')
        alamat_dosen = request.form.get('alamat_dosen')
        no_telp_dosen = request.form.get('no_telp_dosen')

        # Validasi input
        if not nama_dosen or not alamat_dosen or not no_telp_dosen:
            flash('Semua field harus diisi.', 'danger')
            return redirect(url_for('edit_dosen', nidn=nidn))

        try:
            # Update data dosen
            dosen.nama_dosen = nama_dosen
            dosen.alamat_dosen = alamat_dosen
            dosen.no_telp_dosen = no_telp_dosen

            db.session.commit()
            flash('Data dosen berhasil diperbarui.', 'success')
            return redirect(url_for('profile_dosen', nidn=dosen.nidn))
        except Exception as e:
            flash(f'Kesalahan: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('templates_dosen/edit_dosen.html', dosen=dosen)


#Profile Dosen
@app.route('/profile_dosen')
@login_required
def profile_dosen():
    # Ambil semua jadwal milik mahasiswa yang sedang login
    jadwal_list = current_user.jadwal_kuliah
    
    # Hitung total durasi
    total_minutes = 0
    for jadwal in jadwal_list:
        jam_mulai = datetime.strptime(str(jadwal.jam_mulai), '%H:%M:%S')
        jam_selesai = datetime.strptime(str(jadwal.jam_selesai), '%H:%M:%S')
        duration = (jam_selesai - jam_mulai).seconds // 60  # Dalam menit
        total_minutes += duration
    
    total_hours = total_minutes // 60
    remaining_minutes = total_minutes % 60

    return render_template(
        'templates_dosen/profile_dosen.html',
        jadwal_list=jadwal_list,
        total_hours=total_hours,
        remaining_minutes=remaining_minutes
    )

#Register Dosen Success
@app.route('/register_dosen_success')
def register_dosen_success():
    nidn = session.get('nidn')
    return render_template('templates_dosen/register_dosen_success.html', nidn=nidn)


#Jadwal Kuliah

#Add jadwal 
@app.route('/add_jadwal', methods=['GET', 'POST'])
@login_required
def add_jadwal():
    if request.method == 'POST':
        print(f"Form data: {request.form}")
        print(f"Current user: {current_user}")
        hari = request.form.get('hari')
        jam_mulai = request.form.get('jam_mulai')
        jam_selesai = request.form.get('jam_selesai')

        # Validasi input
        if not hari or not jam_mulai or not jam_selesai:
            flash('Semua field harus diisi.', 'danger')
            return redirect(url_for('add_jadwal'))

        # Konversi waktu
        try:
            jam_mulai_obj = datetime.strptime(jam_mulai, '%H:%M').time()
            jam_selesai_obj = datetime.strptime(jam_selesai, '%H:%M').time()
        except ValueError:
            flash('Format waktu salah. Gunakan format HH:MM.', 'danger')
            return redirect(url_for('add_jadwal'))

        if jam_mulai_obj >= jam_selesai_obj:
            flash('Jam mulai harus lebih kecil dari jam selesai.', 'danger')
            return redirect(url_for('add_jadwal'))

        # Buat jadwal baru
        jadwal = JadwalKuliah_2395114030(
            hari=hari,
            jam_mulai=jam_mulai_obj,
            jam_selesai=jam_selesai_obj
        )
        db.session.add(jadwal)
        db.session.commit()

        # Hubungkan jadwal dengan user yang login
        if isinstance(current_user, Mahasiswa_2395114030):
            current_user.jadwal_kuliah.append(jadwal)
        elif isinstance(current_user, Dosen_2395114030):
            current_user.jadwal_kuliah.append(jadwal)
        else:
            flash('Tipe user tidak valid.', 'danger')
            return redirect(url_for('add_jadwal'))

        db.session.commit()
        flash('Jadwal berhasil ditambahkan.', 'success')

        # Redirect ke halaman profil sesuai tipe user
        if isinstance(current_user, Mahasiswa_2395114030):
            return redirect(url_for('profile_mahasiswa'))
        elif isinstance(current_user, Dosen_2395114030):
            return redirect(url_for('profile_dosen'))

    return render_template('templates_jadwal/add_jadwal.html')

#Edit jadwal
@app.route('/edit_jadwal/<int:jadwal_id>', methods=['GET', 'POST'])
@login_required
def edit_jadwal(jadwal_id):
    # Cari jadwal berdasarkan ID
    jadwal = JadwalKuliah_2395114030.query.get_or_404(jadwal_id)

    # Periksa apakah user yang sedang login memiliki hak untuk mengedit jadwal
    if isinstance(current_user, Mahasiswa_2395114030) and jadwal not in current_user.jadwal_kuliah:
        flash('Anda tidak memiliki akses untuk mengedit jadwal ini.', 'danger')
        return redirect(url_for('profile_mahasiswa'))
    if isinstance(current_user, Dosen_2395114030) and jadwal not in current_user.jadwal_kuliah:
        flash('Anda tidak memiliki akses untuk mengedit jadwal ini.', 'danger')
        return redirect(url_for('profile_dosen'))

    if request.method == 'POST':
        hari = request.form.get('hari')
        jam_mulai = request.form.get('jam_mulai')
        jam_selesai = request.form.get('jam_selesai')

        # Validasi input
        if not hari or not jam_mulai or not jam_selesai:
            flash('Semua field harus diisi.', 'danger')
            return redirect(url_for('edit_jadwal', jadwal_id=jadwal_id))

        # Konversi waktu
        try:
            jam_mulai_obj = datetime.strptime(jam_mulai, '%H:%M').time()
            jam_selesai_obj = datetime.strptime(jam_selesai, '%H:%M').time()
        except ValueError:
            flash('Format waktu salah. Gunakan format HH:MM.', 'danger')
            return redirect(url_for('edit_jadwal', jadwal_id=jadwal_id))

        if jam_mulai_obj >= jam_selesai_obj:
            flash('Jam mulai harus lebih kecil dari jam selesai.', 'danger')
            return redirect(url_for('edit_jadwal', jadwal_id=jadwal_id))

        # Update data jadwal
        jadwal.hari = hari
        jadwal.jam_mulai = jam_mulai_obj
        jadwal.jam_selesai = jam_selesai_obj

        db.session.commit()
        flash('Jadwal berhasil diperbarui.', 'success')

        # Redirect ke halaman profil sesuai tipe user
        if isinstance(current_user, Mahasiswa_2395114030):
            return redirect(url_for('profile_mahasiswa'))
        elif isinstance(current_user, Dosen_2395114030):
            return redirect(url_for('profile_dosen'))

    return render_template('templates_jadwal/edit_jadwal.html', jadwal=jadwal)


#Hapus jadwal
@app.route('/delete_jadwal/<int:jadwal_id>', methods=['POST'])
@login_required
def delete_jadwal(jadwal_id):
    # Cari jadwal berdasarkan ID
    jadwal = JadwalKuliah_2395114030.query.get_or_404(jadwal_id)

    # Validasi: Pastikan hanya user terkait yang bisa menghapus jadwal
    if isinstance(current_user, Mahasiswa_2395114030) and jadwal not in current_user.jadwal_kuliah:
        flash('Anda tidak berhak menghapus jadwal ini.', 'danger')
        return redirect(url_for('profile_mahasiswa'))

    if isinstance(current_user, Dosen_2395114030) and jadwal not in current_user.jadwal_kuliah:
        flash('Anda tidak berhak menghapus jadwal ini.', 'danger')
        return redirect(url_for('profile_dosen'))

    # Hapus jadwal dari database
    db.session.delete(jadwal)
    db.session.commit()

    flash('Jadwal berhasil dihapus.', 'success')

    # Redirect sesuai tipe user
    if isinstance(current_user, Mahasiswa_2395114030):
        return redirect(url_for('profile_mahasiswa'))
    elif isinstance(current_user, Dosen_2395114030):
        return redirect(url_for('profile_dosen'))
    else:
        return redirect(url_for('index'))


#Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Buat tabel di database
    app.run(debug=True)
