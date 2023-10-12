from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, socketio
from app.forms import FormLogin, FormAddCalgot, FormPertemuan
from app.models import Admin, User, Pertemuan, Absen
from app.opencvTools import OPENCV
from werkzeug.urls import url_parse
import os
from random import randint

opencv = OPENCV()

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = FormLogin()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin is None or not admin.check_password(form.password.data):
            flash("Nama admin atau password salah!!")
            return redirect(url_for('login'))
        flash("Berhasil Login")
        login_user(admin, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form, title="Masuk")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/dasboard', methods=['GET','POST'])
@login_required
def dasboard():
    allUser = User.query.all()[::-1]
    allPertemuan = Pertemuan.query.all()[::-1]
    form = FormAddCalgot()
    if form.validate_on_submit():
        calgot = User(username=form.username.data, email=form.email.data)
        db.session.add(calgot)
        db.session.commit()
        flash(f"{form.username.data} Berhasil terdaftar")
        return redirect(url_for('dasboard'))
    return render_template('dasboard.html', form=form, allUser=allUser, pertemuan=allPertemuan, jumlah_pertemuan=len(allPertemuan), title="Dasboard")


@app.route('/pertemuan', methods=['POST', 'GET'])
@login_required
def pertemuan():
    daftar_pertemuan = Pertemuan.query.all()[::-1]
    jumlah = len(daftar_pertemuan)
    form = FormPertemuan()
    if form.validate_on_submit():
        cek = Pertemuan.query.filter_by(title=form.title.data).first()
        if cek is not None:
            flash("Title pertemuan telah ada, Gunakan yang lain..")
            return redirect(url_for('pertemuan'))
        dbpertemuan = Pertemuan(title=form.title.data, materi=form.materi.data)
        db.session.add(dbpertemuan)
        db.session.commit()
        allCalgot = User.query.all()
        for isi in allCalgot:
            absen = Absen(pertemuan_id=dbpertemuan.id, user_id=isi.id)
            db.session.add(absen)
        db.session.commit()
        flash(f"Pertemuan: title: {form.title.data}, materi: {form.materi.data}")
        return redirect(url_for('pertemuan'))
    return render_template('pertemuan.html', title='Pertemuan', form=form, daftar=daftar_pertemuan, jumlah=jumlah)


@app.route('/tambahkan_wajah/<username>', methods=['GET'])
@login_required
def tambahkan(username):
    if not os.path.exists(f'sampleimg/{username}'):
        os.mkdir(f'sampleimg/{username}')
    calgot = User.query.filter_by(username=username).first()
    return render_template('tambahkan_wajah.html', user=calgot, title="Tambahkan sample wajah")


@app.route('/absen_pertemuan/<pertemuan>')
@login_required
def absen_pertemuan(pertemuan):
    # target_pertemuan = Pertemuan.query.filter_by(title=pertemuan).first()
    return render_template('absen.html', pertemuan=pertemuan, title="Absen")



# @app.route('/scan_wajah/<username>', methods=['GET'])
# @login_required
# def scan_wajah(username):
#     calgot = User.query.filter_by(username=username).first()
#     return render_template('scan_wajah.html', user=username, title="Ferifikasi")


@app.route('/deteksi_wajah')
@login_required
def deteksi_wajah():
    global opencv
    return render_template('deteksi.html', title='tes deteksi')


@app.route('/hasil/<username>')
@login_required
def hasil(username):
    lsimgs = os.listdir(f'sampleimg/{username}')
    if len(lsimgs) < 15:
        return redirect(url_for('tambahkan', username=username))
    userObj = User.query.filter_by(username=username).first()
    global opencv
    if os.path.exists(opencv.path_sampleimg+username):
        opencv.set_dataset(userObj)
        opencv.latih_dataset()
        userObj.dataset = True
        db.session.add(userObj)
        db.session.commit()
    return render_template('hasil.html', user=userObj)


@app.route('/latih/<username>')
@login_required
def latih(username):
    global opencv
    opencv.latih_dataset()
    return redirect(url_for('hasil', username=username))


@app.route('/tes_prediksi/<username>')
@login_required
def tesprediksi(username):
    jumlah_sample = len(os.listdir('sampleimg/'+username))
    if jumlah_sample < 15:
        return redirect(url_for('tambahkan', username=username))
    return render_template('tes_deteksi.html', nama=username, title='Tes Prediksi')


@socketio.on('deteksi')
@login_required
def handle_deteksi(image_data):
    global opencv
    daftar = User.query.all()
    daftar_nama = []
    for isi in daftar:
        daftar_nama.append(isi.username)
    
    nama, prediksi = opencv.deteksi_wajah(image_data, daftar_nama)
    socketio.emit('message', {'text': f'nama: {nama} | prediksi: {prediksi}%'})
    print('[INFO deteksi]',opencv.deteksi_wajah(image_data, daftar_nama))


@socketio.on('tes_prediksi')
@login_required
def tes_prediksi(image_data, namap):
    global opencv
    daftar = User.query.all()
    daftar_nama = []
    for isi in daftar:
        daftar_nama.append(isi.username)
    nama, prediksi = opencv.deteksi_wajah(image_data, daftar_nama)
    if prediksi > 40 and nama == namap:
        user = User.query.filter_by(username=namap).first()
        if user.face_prediksi < prediksi:
            user.face_prediksi = prediksi
            db.session.add(user)
            db.session.commit()
            flash("Face prediksi berhasil di update")
        socketio.emit('message', {'text': f'nama: {nama} | prediksi: {prediksi}%'})
        print('[INFO deteksi]',opencv.deteksi_wajah(image_data, daftar_nama))



@socketio.on('image')
@login_required
def handle_image(image_data, nama):
    nama = User.query.filter_by(username=nama).first()
    global opencv
    jumlah = opencv.jumlah_sampleimg_user(nama) + 1
    print(nama)

    if opencv.jumlah_sampleimg_user(nama) >= 15:
        print("Selesai")
        socketio.emit('message', {'text': f'status jumlah: {jumlah}/10'})
        socketio.emit('redirect', {'url': url_for('hasil', username=nama.username)})
    else:
        print("Add...")
        opencv.add_sampleimg(nama, image_data)
        socketio.emit('message', {'text': f'status jumlah: {jumlah}/10'})


@socketio.on('absen')
@login_required
def absen(image_data,id_pertemuan):
    global opencv
    daftar = User.query.all()
    daftar_nama = []
    for isi in daftar:
        daftar_nama.append(isi.username)

    nama, prediksi = opencv.deteksi_wajah(image_data, daftar_nama)
    print(f'nama: {nama}, prediksi: {prediksi}%')
    socketio.emit('message', {'text': f'nama: {nama}, prediksi: {prediksi}%'})
    if prediksi >= 60:
        user_cek = User.query.filter_by(username=nama).first()
        if user_cek is None:
            print(user_cek, "Is None")
        else:
            print(user_cek, "Is True")
            current_absen = Absen.query.filter_by(pertemuan_id=id_pertemuan, user_id=user_cek.id).first()
            if current_absen.status:
                flash(f"{user_cek.username} Telah Absen")
                socketio.emit('redirect', {'url': url_for('pertemuan')})
            else:
                current_absen.status = True
                user_cek.jumlah_hadir += 1
                db.session.add(current_absen)
                db.session.add(user_cek)
                db.session.commit()

        