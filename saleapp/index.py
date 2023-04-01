import math
import datetime
from flask import render_template, request, redirect, session, jsonify, url_for
from saleapp import app, admin, login, untils, socketio
from saleapp.models import UserRole
from flask_login import login_user, logout_user, login_required, current_user
import cloudinary.uploader
from flask_socketio import SocketIO, emit, join_room
import requests

data = {'profile_id': "",
        'nganh': "",
        'khoa': "",
        'lop': ""}

@app.route("/")
def home():
    return render_template('index.html')

#socket

@app.route("/chatroom")
def chat_room():
    user_name = current_user.name
    room = untils.get_chatroom_by_user_id(id=current_user.id)

    # print(room.room_id)

    user_send = [untils.get_user_by_id(x.user_id).name for x in untils.load_message(room.room_id)]

    user_image = [untils.get_user_by_id(x.user_id).avatar for x in untils.load_message(room.room_id)]

    user_id = [x.user_id for x in untils.load_message(room.room_id)]

    user_send.pop(0)
    user_image.pop(0)
    user_id.pop(0)

    print(user_send)

    if user_name and room:

        print(untils.load_message(room.room_id)[0].content)
        return render_template('chatroom.html', user_name=user_name, room=room.room_id, name= current_user.name,
                               message=untils.load_message(room.room_id), room_id = int(room.room_id),
                               user_send= user_send, n=len(user_send), user_image=user_image, user_id=user_id)
    else:
        return redirect(url_for('home'))


@app.route("/profile/<profile_id>", methods=['post', 'get'])
def profile(profile_id):
    data['profile_id'] = profile_id
    pro = untils.get_profile(profile_id)
    xh = "Xuất sắc"
    if pro.gpa >= 3.6 and pro.diemRL > 90:
        xh = "Xuất sắc"
    elif pro.gpa >= 3.2 and pro.diemRL > 80:
        xh = "Giỏi"
    elif pro.gpa >= 2.5 and pro.diemRL > 50:
        xh = "Khá"
    else:
        xhh = "Yếu"

    room = untils.get_chat_room_by_user_id(pro.user_id)

    dob = str(pro.dob.year) + "-" + str(pro.dob.month).zfill(2) + "-" + str(pro.dob.day).zfill(2)

    allNganh = untils.get_all_nganh(pro.idKhoa)
    allKhoa = untils.get_all_khoa()

    return render_template('profile.html', profile=pro, xh=xh, dob=dob, allNganh=allNganh,
                           allKhoa=allKhoa, room=room)

@app.route('/save_khoa')
def save_khoa():
    pro = untils.get_profile(data['profile_id'])
    xh = "Xuất sắc"
    if pro.gpa >= 3.6 and pro.diemRL > 90:
        xh = "Xuất sắc"
    elif pro.gpa >= 3.2 and pro.diemRL > 80:
        xh = "Giỏi"
    elif pro.gpa >= 2.5 and pro.diemRL > 50:
        xh = "Khá"
    else:
        xhh = "Yếu"


    room = untils.get_chat_room_by_user_id(pro.user_id)

    dob = str(pro.dob.year) + "-" + str(pro.dob.month).zfill(2) + "-" + str(pro.dob.day).zfill(2)

    allNganh = untils.get_all_nganh(pro.idKhoa)
    allKhoa = untils.get_all_khoa()

    return render_template('save_khoa.html', profile=pro, xh=xh, dob=dob, allNganh=allNganh,
                           allKhoa=allKhoa, room=room)

@app.route('/save_nganh', methods=['POST', 'get'])
def save_nganh():
    data['khoa'] = request.form.get('khoa')
    khoa = request.form.get('khoa')
    allNganh = untils.get_all_nganh(khoa)
    pro = untils.get_profile(data['profile_id'])
    xh = "Xuất sắc"
    if pro.gpa >= 3.6 and pro.diemRL > 90:
        xh = "Xuất sắc"
    elif pro.gpa >= 3.2 and pro.diemRL > 80:
        xh = "Giỏi"
    elif pro.gpa >= 2.5 and pro.diemRL > 50:
        xh = "Khá"
    else:
        xhh = "Yếu"

    dob = str(pro.dob.year) + "-" + str(pro.dob.month).zfill(2) + "-" + str(pro.dob.day).zfill(2)

    allKhoa = untils.get_all_khoa()

    return render_template('save_nganh.html', profile=pro, xh=xh, dob=dob, allNganh=allNganh,
                           allKhoa=allKhoa)

@app.route('/save_lop', methods=['POST'])
def save_lop():
    data['nganh'] = request.form.get('nganh')
    nganh = request.form.get('nganh')
    allLop = untils.get_all_lop(nganh)
    pro = untils.get_profile(data['profile_id'])
    xh = "Xuất sắc"
    if pro.gpa >= 3.6 and pro.diemRL > 90:
        xh = "Xuất sắc"
    elif pro.gpa >= 3.2 and pro.diemRL > 80:
        xh = "Giỏi"
    elif pro.gpa >= 2.5 and pro.diemRL > 50:
        xh = "Khá"
    else:
        xhh = "Yếu"

    dob = str(pro.dob.year) + "-" + str(pro.dob.month).zfill(2) + "-" + str(pro.dob.day).zfill(2)

    allKhoa = untils.get_all_khoa()

    return render_template('save_lop.html', profile=pro, xh=xh, dob=dob, allLop=allLop,
                           allKhoa=allKhoa)

@app.route("/save_change2", methods=['post'])
def save_change2():
    data['lop'] = request.form.get('lop')

    print(data['khoa'], data['nganh'], data['lop'])
    untils.save2(data['profile_id'], int(data['lop']))

    return redirect(url_for('profile', profile_id=data['profile_id']))

@app.route("/xemdiem/<profile_id>")
def xemdiem(profile_id):
    data['profile_id'] = profile_id
    mon = request.args.get('mon')
    diemGiuaKi = untils.xem_all_diem_gk_by_ma_so(maSo=profile_id)
    diemCuoiKi = untils.xem_all_diem_ck_by_ma_so(maSo=profile_id)
    proFile = untils.get_sinhvien_by_id(profile_id)[0]

    if mon:
        diemGiuaKi = untils.xem_all_diem_gk_by_ma_so(maSo=profile_id, maMon=mon.upper())
        diemCuoiKi = untils.xem_all_diem_ck_by_ma_so(maSo=profile_id, maMon=mon.upper())

    monhoc = []

    for i in diemGiuaKi:
        monhoc.append(untils.get_mon_hoc_by_ma_diem(i.idMonHoc))

    diemHeMuoi = []
    for i in range(len(diemGiuaKi)):
        diemHeMuoi.append(round(diemGiuaKi[i].diem * monhoc[i].tiLeGiuaKi + diemCuoiKi[i].diem * (1 - monhoc[i].tiLeGiuaKi), 1))

    diemHeBon = []
    diemChu = []
    for i in diemHeMuoi:
        if (i >= 8.5):
            diemHeBon.append(4.0)
            diemChu.append('A+')
        elif i >= 8:
            diemHeBon.append(3.5)
            diemChu.append('A')
        elif i >= 7:
            diemHeBon.append(3)
            diemChu.append('B+')
        elif i >= 6:
            diemHeBon.append(2.5)
            diemChu.append('B')
        elif i >= 5:
            diemHeBon.append(2)
            diemChu.append('C')
        elif i >= 4:
            diemHeBon.append(1.5)
            diemChu.append('D+')
        elif i >= 2:
            diemHeBon.append(1)
            diemChu.append('D+')
        else:
            diemHeBon.append(0)
            diemChu.append('F')

    return render_template('xemdiem.html', diemGiuaKi=diemGiuaKi, diemCuoiKi=diemCuoiKi, n=len(diemGiuaKi),
                           monhoc=monhoc, diemHeMuoi=diemHeMuoi, diemHeBon=diemHeBon, diemChu=diemChu,
                           proFile=proFile)

@app.route("/xemdiem/change/<mamon>")
def xemdiem_change(mamon):

    diemGiuaKi = untils.xem_all_diem_gk_by_ma_so(maSo=data['profile_id'], maMon=mamon.upper())
    diemCuoiKi = untils.xem_all_diem_ck_by_ma_so(maSo=data['profile_id'], maMon=mamon.upper())
    proFile = untils.get_sinhvien_by_id(data['profile_id'])[0]

    monhoc = []

    for i in diemGiuaKi:
        monhoc.append(untils.get_mon_hoc_by_ma_diem(i.idMonHoc))

    diemHeMuoi = []
    for i in range(len(diemGiuaKi)):
        diemHeMuoi.append(round(diemGiuaKi[i].diem * monhoc[i].tiLeGiuaKi + diemCuoiKi[i].diem * (1 - monhoc[i].tiLeGiuaKi), 1))

    diemHeBon = []
    diemChu = []
    for i in diemHeMuoi:
        if (i >= 8.5):
            diemHeBon.append(4.0)
            diemChu.append('A+')
        elif i >= 8:
            diemHeBon.append(3.5)
            diemChu.append('A')
        elif i >= 7:
            diemHeBon.append(3)
            diemChu.append('B+')
        elif i >= 6:
            diemHeBon.append(2.5)
            diemChu.append('B')
        elif i >= 5:
            diemHeBon.append(2)
            diemChu.append('C')
        elif i >= 4:
            diemHeBon.append(1.5)
            diemChu.append('D+')
        elif i >= 2:
            diemHeBon.append(1)
            diemChu.append('D+')
        else:
            diemHeBon.append(0)
            diemChu.append('F')

    return render_template('xemdiem_change.html', diemGiuaKi=diemGiuaKi, diemCuoiKi=diemCuoiKi, n=len(diemGiuaKi),
                           monhoc=monhoc, diemHeMuoi=diemHeMuoi, diemHeBon=diemHeBon, diemChu=diemChu,
                           proFile=proFile)

@app.route('/process_change/<mon>', methods=['POST'])
def process_change(mon):

    diemGiuaKi = request.form.get('diemgiuaki')
    diemCuoiKi = request.form.get('diemcuoiki')

    untils.update_diem(mon, data['profile_id'], diemGiuaKi, diemCuoiKi)

    return redirect(url_for('xemdiem', profile_id=data['profile_id']))

@app.route('/themmon', methods=['post', 'get'])
def themmon():
    mon = request.args.get('mon')
    proFile = untils.get_sinhvien_by_id(data['profile_id'])[0]
    diemGiuaKi = untils.xem_all_diem_gk_by_ma_so(maSo=data['profile_id'])

    monhoc = []

    for i in diemGiuaKi:
        monhoc.append(untils.get_mon_hoc_by_ma_diem(i.idMonHoc))

    allMonHoc = untils.get_all_mon_hoc()

    monHocChuaHoc = []

    for i in allMonHoc:
        if i not in monhoc:
            monHocChuaHoc.append(i)

    # print("mch", monHocChuaHoc)

    if mon:
        monTimKiem = untils.get_mon_by_string(mon)

        temp = []

        for i in monHocChuaHoc:
            if i in monTimKiem:
                temp.append(i)

        # print(temp)
        if len(temp) > 0:
            return render_template('themmon.html', proFile=proFile, monhoc=temp)
        else:
            return render_template('themmon.html', proFile=proFile, monhoc=[])

    return render_template('themmon.html', proFile=proFile, monhoc=monHocChuaHoc)

@app.route('/dangkimon/<mon>', methods=['POST', 'get'])
def dangkimon(mon):

    untils.them_mon(data['profile_id'], mon)

    return redirect(url_for('xemdiem', profile_id=data['profile_id']))

@app.route('/delete_mon/<mon>', methods=['POST', 'get'])
def delete_mon(mon):

    untils.xoa_mon(data['profile_id'], mon)

    return redirect(url_for('xemdiem', profile_id=data['profile_id']))

@app.route('/delete_user', methods=['POST', 'get'])
def delete_user():


    return redirect('/admin/viewuserdetail/')

@app.route('/change_profile', methods=['POST'])
def change_profile():
    profile_id = data['profile_id']
    data['profile_id'] = profile_id

    name = request.form.get("name")
    dob = request.form.get('dob')
    sex = request.form.get('sex')
    khoa = request.form.get('khoa')
    nganh = request.form.get('nganh')
    lop = request.form.get('class')
    email = request.form.get('email')
    phone = request.form.get('phone')
    khoahoc = request.form.get('khoahoc')
    diachi = request.form.get('diachi')

    # print(name, dob, sex, khoa, nganh, lop, email, phone, khoahoc, diachi)

    untils.change_profile(data['profile_id'], name, dob, sex, email, phone, diachi)

    return redirect(url_for('profile', profile_id=data['profile_id']))

@app.route('/process', methods=['POST'])
def process():
    profile_id = data['profile_id']
    data['profile_id'] = profile_id
    print(profile_id)
    mon = request.args.get('mon')
    diemGiuaKi = untils.xem_all_diem_gk_by_ma_so(maSo=profile_id)
    diemCuoiKi = untils.xem_all_diem_ck_by_ma_so(maSo=profile_id)

    if mon:
        diemGiuaKi = untils.xem_all_diem_gk_by_ma_so(maSo=profile_id, maMon=mon)
        diemCuoiKi = untils.xem_all_diem_ck_by_ma_so(maSo=profile_id, maMon=mon)

    monhoc = []

    for i in diemGiuaKi:
        monhoc.append(untils.get_mon_hoc_by_ma_diem(i.idMonHoc))

    diemHeMuoi = []
    for i in range(len(diemGiuaKi)):
        diemHeMuoi.append(
            round(diemGiuaKi[i].diem * monhoc[i].tiLeGiuaKi + diemCuoiKi[i].diem * (1 - monhoc[i].tiLeGiuaKi), 1))

    diemHeBon = []
    diemChu = []
    for i in diemHeMuoi:
        if (i >= 8.5):
            diemHeBon.append(4.0)
            diemChu.append('A+')
        elif i >= 8:
            diemHeBon.append(3.5)
            diemChu.append('A')
        elif i >= 7:
            diemHeBon.append(3)
            diemChu.append('B+')
        elif i >= 6:
            diemHeBon.append(2.5)
            diemChu.append('B')
        elif i >= 5:
            diemHeBon.append(2)
            diemChu.append('C')
        elif i >= 4:
            diemHeBon.append(1.5)
            diemChu.append('D+')
        elif i >= 2:
            diemHeBon.append(1)
            diemChu.append('D+')
        else:
            diemHeBon.append(0)
            diemChu.append('F')

    try:
        avgHeMuoi = round(sum(diemHeMuoi) / len(diemHeMuoi), 2)
        avgHeBon = round(sum(diemHeBon) / len(diemHeBon), 2)
    except:
        avgHeMuoi = 0
        avgHeBon = 0
    tongTinChi = 0
    for i in monhoc:
        tongTinChi = tongTinChi + i.soTinChi

    print(avgHeBon, avgHeMuoi, tongTinChi)

    untils.update_diem_by_maSo(profile_id, avgHeMuoi, avgHeBon, tongTinChi)

    return redirect(url_for('xemdiem', profile_id=data['profile_id']))

@app.route("/admin/chatadmin/<int:room_id>")
def chat_room_admin(room_id):
    if current_user.userRole == UserRole.SYSADMIN or current_user.userRole == UserRole.NHANVIEN:
        print(room_id)
        user_name = current_user.name
        room = untils.get_chatroom_by_room_id(id=room_id)
        list_user = untils.load_message(room.room_id)

        user_send = [(untils.get_user_by_id(x.user_id).name) for x in list_user]

        user_image = [untils.get_user_by_id(x.user_id).avatar for x in list_user]

        user_id = [x.user_id for x in list_user]

        user_send.pop(0)
        user_image.pop(0)
        user_id.pop(0)

        host_avatar = untils.get_host_room_avatar(room.room_id);

        if user_name and room:
            return render_template('chatroom.html', user_name=user_name, room=room.room_id, name=current_user.name,
                                   message=list_user, room_id=int(room.room_id),
                                   user_send=user_send, n=len(user_send), user_image=user_image, user_id=user_id,
                                   room_name=untils.get_chatroom_by_id(room.room_id),
                                   host_avatar=host_avatar);

    return redirect(url_for('home'));


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'],
                                                                    data['message']))

    app.logger.info("{}".format(data['user_avatar']))
    socketio.emit('receive_message', data, room=data['room'])

@socketio.on('save_message')
def handle_save_message_event(data):
    # app.logger.info("2.all_mess: " + str(data['all_message']))
    app.logger.info("2.room_id: " + str(data['room']))

    untils.save_chat_message(room_id=int(data['room']), message=data['message'], user_id=current_user.id)

    if (current_user.user_role == UserRole.ADMIN):
        print("Dd")
        untils.change_room_status(data['room'], 1)

    if (current_user.user_role == UserRole.USER):
        print("Dd1")
        untils.change_room_status(data['room'], 0)


@socketio.on('join_room')
def handle_send_room_event(data):
    app.logger.info(data['username'] + " has sent message to the room " + data['room'] + ": ")
    join_room(data['room'])

    socketio.emit('join_room_announcement', data, room=data['room'])


@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        diachi = request.form.get('diachi')
        confirm = request.form.get('confirm')
        avatar_path = None

    try:
        if str(password) == str(confirm):
            avatar = request.files.get('avatar')
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']

            untils.add_user(name=name,
                            username=username,
                            password=password,
                            diachi=diachi,
                            email=email,
                            avatar=avatar_path)
            return redirect(url_for('user_signin'))
        else:
            err_msg = "Mat khau khong khop"
            # print(err_msg)
    except Exception as ex:
        pass
        # err_msg = 'He thong ban' + str(ex)
        # print(err_msg)

    return render_template('register.html', err_msg=err_msg)


@app.route('/user-login', methods=['get', 'post'])
def user_signin():
    err_msg = ""

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = untils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            next = request.args.get('next', 'home')
            return redirect(url_for(next))
        else:
            err_msg = "Sai tên đăng nhập hoặc mật khẩu"

    return render_template('login.html', err_msg=err_msg)


@app.route('/admin-login', methods=['post'])
def signin_admin():
    username = request.form.get('username')
    password = request.form.get('password')

    # user = untils.check_login(username=username, password=password, role=UserRole.ADMIN)
    user = untils.check_admin_login(username=username, password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('home'))


@login.user_loader
def user_load(user_id):
    return untils.get_user_by_id(user_id=user_id)




if __name__ == '__main__':
    socketio.run(app, debug=True)
