import math
import datetime
from flask import render_template, request, redirect, session, jsonify, url_for
from saleapp import app, admin, login, untils, socketio
from saleapp.models import UserRole
from flask_login import login_user, logout_user, login_required, current_user
import cloudinary.uploader
from flask_socketio import SocketIO, emit, join_room
import requests
import pandas as pd
import numpy as np
from saleapp.time import *
import openpyxl

data = {'profile_id': "",
        'nganh': "",
        'khoa': "",
        'lop': ""}


@app.route("/")
def home():
    return render_template('index.html')



# socket

@app.route("/chatroom")
def chat_room():
    if current_user.is_authenticated:
        pass
    else:
        return redirect(url_for('user_signin'))

    user_name = (current_user.name)
    room = untils.get_chatroom_by_user_id(id=current_user.id)
    list_user = untils.load_message(room.room_id)

    print(room.room_id)

    user_send = [(untils.get_user_by_id(x.user_id).name) for x in list_user]

    user_image = [untils.get_user_by_id(x.user_id).avatar for x in list_user]

    user_id = [x.user_id for x in list_user]

    host_avatar = untils.get_host_room_avatar(room.room_id);

    user_send.pop(0)
    user_image.pop(0)
    user_id.pop(0)

    print(user_send)

    if user_name and room:

        # print(untils.load_message(room.room_id)[0].content)

        return render_template('chatroom.html', user_name=(user_name), room=room.room_id, name=current_user.name,
                               message=list_user, room_id=int(room.room_id),
                               user_send=user_send, n=len(user_send), user_image=user_image, user_id=user_id,
                               room_name=untils.get_chatroom_by_id(room.room_id),
                               host_avatar=host_avatar);
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

    # print(current_user.userRole)

    return render_template('profile.html', profile=pro, xh=xh, dob=dob, allNganh=allNganh,
                           allKhoa=allKhoa, room=room, admin=UserRole.SYSADMIN)

@app.route("/profile_user", methods=['post', 'get'])
def profile_user():
    data['profile_id'] = current_user.maSo
    pro = untils.get_profile(current_user.maSo)
    xh = "Xuất sắc"
    if pro.gpa >= 3.6 and pro.diemRL > 90:
        xh = "Xuất sắc"
    elif pro.gpa >= 3.2 and pro.diemRL > 80:
        xh = "Giỏi"
    elif pro.gpa >= 2.5 and pro.diemRL > 50:
        xh = "Khá"
    else:
        xhh = "Yếu"

    room = untils.get_chat_room_by_user_id(current_user.id)

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


    return render_template('xemdiem.html', diemGiuaKi=diemGiuaKi, diemCuoiKi=diemCuoiKi, n=len(diemGiuaKi),
                           monhoc=monhoc, diemHeMuoi=diemHeMuoi, diemHeBon=diemHeBon, diemChu=diemChu,
                           proFile=proFile, admin=UserRole.SYSADMIN)




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

    hocKi = []

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
            for i in temp:
                hocKi.append(untils.get_ten_hoc_ki_by_id(i.idHocKi))
            return render_template('themmon.html', proFile=proFile, monhoc=temp, hocKi=hocKi, n=len(temp))
        else:
            return render_template('themmon.html', proFile=proFile, monhoc=[], hocKi=[], n=len(temp))

    for i in monHocChuaHoc:
        hocKi.append(untils.get_ten_hoc_ki_by_id(i.idHocKi))

    return render_template('themmon.html', proFile=proFile, monhoc=monHocChuaHoc, hocKi=hocKi, n=len(monHocChuaHoc))


@app.route('/dangkimon/<mon>/hocki<int:hocki>', methods=['POST', 'get'])
def dangkimon(mon, hocki):
    untils.them_mon(data['profile_id'], mon)

    return redirect(url_for('xemdiem', profile_id=data['profile_id']))


@app.route('/delete_mon/<mon>', methods=['POST', 'get'])
def delete_mon(mon):
    untils.xoa_mon(data['profile_id'], mon)

    return redirect(url_for('xemdiem', profile_id=data['profile_id']))


@app.route('/delete_user', methods=['POST', 'get'])
def delete_user():
    untils.delete_user(data['profile_id'])

    return redirect('/admin/viewuserdetail/')


@app.route('/change_profile', methods=['POST', 'get'])
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
    diemrl = request.form.get('diemrl')

    # print(name, dob, sex, khoa, nganh, lop, email, phone, khoahoc, diachi)

    untils.change_profile(data['profile_id'], name, dob, sex, email, phone, diachi, diemrl)

    return redirect(url_for('profile', profile_id=data['profile_id']))



@app.route('/stat')
def stat():
    return render_template('stat.html', admin=UserRole.SYSADMIN)


@app.route('/stat1', methods=['post', 'get'])
def stat1():
    diemtbtheomon = []
    top = 5
    if request.method == 'POST':
        idkhoa = request.form.get('khoa')
        hocki = request.form.get('hocki')
        top = request.form.get('top')


        if top == '':
            top = 5

        allmon = untils.get_all_mon_hoc(idkhoa)

        print(allmon, hocki)

        diem = []

        for i in allmon:
            diem.append(untils.get_top_mon_theo_ky(i.id, hocki))
            print(diem[len(diem) - 1])


        for i in range(len(allmon)):
            diemtb = 0
            for j in diem[i]:
                if j.isMidTerm == True:
                    diemtb = diemtb + j.diem * j.tiLeGiuaKi
                else:
                    diemtb = diemtb + j.diem * (1 - j.tiLeGiuaKi)
            n = len(diem[i]) / 2
            try:
                diemtbtheomon.append(round(float(diemtb / n), 2))
            except:
                pass

    # print(diemtbtheomon)

    if diemtbtheomon:
        data = {
            "mon": allmon,
            "diemtb": diemtbtheomon
        }
    else:
        data = {
            "mon": [],
            "diemtb": []
        }

    pd_data = pd.DataFrame(data)

    pd_data = pd_data.sort_values(by=['diemtb'], ascending=False)

    # print(pd_data)

    khoa = untils.get_all_khoa()
    hocki = untils.get_all_hocki()

    data_mon = []
    data_diem = []


    if int(top) > len(pd_data):
        top = len(pd_data)

    top = int(top)
    for i in range(top):
        data_diem.append(pd_data.iloc[i].diemtb)
        data_mon.append(pd_data.iloc[i].mon)

    return render_template('stat1.html', khoa=khoa, hocki=hocki, data_diem=data_diem,
                           data_mon=data_mon)

@app.route('/stat2')
def stat2():

    data = untils.get_sinh_vien_theo_khoa()

    ten = []
    soluong = []

    for i in data:
        ten.append(i.tenkhoa)
        soluong.append(i.count)

    return render_template('stat2.html', ten=ten, soluong=soluong)

@app.route('/stat3')
def stat3():

    return render_template('stat3.html')

@app.route('/stat3/1')
def stat3_1():
    hk1_20_21 = pd.read_excel('data/data_thukhoa/HK1_20_21.xlsx')
    hk1_21_22 = pd.read_excel('data/data_thukhoa/HK1_21_22.xlsx')
    hk2_20_21 = pd.read_excel('data/data_thukhoa/HK2_20_21.xlsx')
    hk2_21_22 = pd.read_excel('data/data_thukhoa/HK2_21_22.xlsx')
    hk3_20_21 = pd.read_excel('data/data_thukhoa/HK3_20_21.xlsx')
    hk3_21_22 = pd.read_excel('data/data_thukhoa/HK3_21_22.xlsx')

    hk3_20_21['diem'] = hk3_20_21['diem'].astype(np.float64)

    hk1_20_21['label'] = 0
    hk1_21_22['label'] = 1
    hk2_20_21['label'] = 2
    hk2_21_22['label'] = 3
    hk3_20_21['label'] = 4
    hk3_21_22['label'] = 5

    mssv = []
    hoten = []

    untils.addTen(hk1_20_21, mssv, hoten)
    untils.addTen(hk2_20_21, mssv, hoten)
    untils.addTen(hk3_20_21, mssv, hoten)
    untils.addTen(hk1_21_22, mssv, hoten)
    untils.addTen(hk2_21_22, mssv, hoten)
    untils.addTen(hk3_21_22, mssv, hoten)

    diem = np.zeros(len(hoten), dtype='float')

    data = pd.DataFrame({
        'mssv': mssv,
        'hoten': hoten,
        'diem': diem.tolist()
    })

    untils.changedata(data, hk1_20_21)
    untils.changedata(data, hk2_20_21)
    untils.changedata(data, hk3_20_21)
    untils.changedata(data, hk1_21_22)
    untils.changedata(data, hk2_21_22)
    untils.changedata(data, hk3_21_22)

    data['diem'] = round(data['diem'] / 6, 2)

    print(data.sort_values('diem', ascending=False))

    sort_data = data.sort_values('diem', ascending=False)


    data_diem = []
    data_ten = []
    data_mssv = []

    for i in range(5):
        data_ten.append(sort_data.iloc[i].hoten)
        data_diem.append(sort_data.iloc[i].diem)
        data_mssv.append(sort_data.iloc[i].mssv)


    return render_template('stat3_sub.html', data_ten=data_ten,data_mssv=data_mssv,data_diem=data_diem, sort_data=sort_data,
                           n=len(data_mssv), len_sort_data=len(sort_data.mssv), nganh="Công nghệ thông tin")

@app.route('/stat3/2')
def stat3_2():
    hk1_20_21 = pd.read_excel('data/data_thukhoa1/HK1_20_21.xlsx')
    hk1_21_22 = pd.read_excel('data/data_thukhoa1/HK1_21_22.xlsx')
    hk2_20_21 = pd.read_excel('data/data_thukhoa1/HK2_20_21.xlsx')
    hk2_21_22 = pd.read_excel('data/data_thukhoa1/HK2_21_22.xlsx')
    hk3_20_21 = pd.read_excel('data/data_thukhoa1/HK3_20_21.xlsx')
    hk3_21_22 = pd.read_excel('data/data_thukhoa1/HK3_21_22.xlsx')

    hk3_20_21['diem'] = hk3_20_21['diem'].astype(np.float64)

    hk1_20_21['label'] = 0
    hk1_21_22['label'] = 1
    hk2_20_21['label'] = 2
    hk2_21_22['label'] = 3
    hk3_20_21['label'] = 4
    hk3_21_22['label'] = 5

    mssv = []
    hoten = []

    untils.addTen(hk1_20_21, mssv, hoten)
    untils.addTen(hk2_20_21, mssv, hoten)
    untils.addTen(hk3_20_21, mssv, hoten)
    untils.addTen(hk1_21_22, mssv, hoten)
    untils.addTen(hk2_21_22, mssv, hoten)
    untils.addTen(hk3_21_22, mssv, hoten)

    diem = np.zeros(len(hoten), dtype='float')

    data = pd.DataFrame({
        'mssv': mssv,
        'hoten': hoten,
        'diem': diem.tolist()
    })

    untils.changedata(data, hk1_20_21)
    untils.changedata(data, hk2_20_21)
    untils.changedata(data, hk3_20_21)
    untils.changedata(data, hk1_21_22)
    untils.changedata(data, hk2_21_22)
    untils.changedata(data, hk3_21_22)

    data['diem'] = round(data['diem'] / 6, 2)

    print(data.sort_values('diem', ascending=False))

    sort_data = data.sort_values('diem', ascending=False)


    data_diem = []
    data_ten = []
    data_mssv = []

    for i in range(5):
        data_ten.append(sort_data.iloc[i].hoten)
        data_diem.append(sort_data.iloc[i].diem)
        data_mssv.append(sort_data.iloc[i].mssv)


    return render_template('stat3_sub.html', data_ten=data_ten,data_mssv=data_mssv,data_diem=data_diem, sort_data=sort_data,
                           n=len(data_mssv), len_sort_data=len(sort_data.mssv), nganh='Hệ thống thông tin quản lý')

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

    if (current_user.userRole == UserRole.SYSADMIN or current_user.userRole == UserRole.NHANVIEN):
        untils.change_room_status(data['room'], 1)

    if (current_user.userRole == UserRole.SINHVIEN):
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
        name = request.form.get('firstname') + " " + request.form.get('lastname')
        password = request.form.get('password')
        email = request.form.get('email')
        username = email
        sex = request.form.get('sex')
        dob = request.form.get('dob')
        phone = request.form.get('phone')
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
                            avatar=avatar_path,
                            sex=sex,
                            dob=dob,
                            phone=phone)

            return redirect(url_for('user_signin'))
        else:
            err_msg = "Mat khau khong khop"
            # print(err_msg)
    except Exception as ex:
        pass
        # err_msg = 'He thong ban' + str(ex)
        # print(err_msg)

    return render_template('register.html', err_msg=err_msg)


@app.route('/question_answering', methods=['post', 'get'])
def question_answering():
    predict = ''
    context = ''
    question = ''
    answer0 = ''
    answer1 = ''
    answer2 = ''
    answer3 = ''

    if request.method == 'POST':
        context = request.form.get('context').strip()
        question = request.form.get('question').strip()
        answer0 = request.form.get('answer1').strip()
        answer1 = request.form.get('answer2').strip()
        answer2 = request.form.get('answer3').strip()
        answer3 = request.form.get('answer4').strip()

        if context and question and answer0 and answer1 and answer2 and answer3:
            predict = untils.predict_question_answering(context, question, answer0, answer1, answer2, answer3)
        else:
            predict = "Please input fully"

    return render_template('question_answering.html', predict=predict,
                           question=question, context=context, answer0=answer0,
                           answer1=answer1, answer2=answer2, answer3=answer3)


@app.route('/question', methods=['post', 'get'])
def question():
    predict = ''
    context = ''
    question = ''

    if request.method == 'POST':
        context = request.form.get('context').strip()
        question = request.form.get('question').strip()

        if context and question:
            predict = untils.predict_question(context, question)
        else:
            predict = "Please input fully"

    return render_template('question.html', predict=predict,
                           question=question, context=context)


@app.route('/predict', methods=['post', 'get'])
def predict():
    predict = ''
    diem = 0
    from_predict = ''
    to_predict = ''

    if request.method == 'POST':
        diem = request.form.get('diem')

        if diem:
            predict = round(untils.predict_gk_ck_nhapmon(float(diem)), 1)
            from_predict = round(predict - 0.5, 1)
            to_predict = round(predict + 0.5, 1)
            if from_predict < 0:
                from_predict = 0
            if to_predict > 10:
                to_predict = 10
        else:
            predict = "Please input fully"

    return render_template('predict.html', predict=predict,
                           diem=diem, from_predict=from_predict, to_predict=to_predict)


@app.route('/summary', methods=['post', 'get'])
def summary():
    summary = ''
    text = ''

    if request.method == 'POST':
        text = request.form.get('text')

        if text:
            summary = untils.summary(text)
        else:
            summary = "Please input fully"

    return render_template('sumary.html', summary=summary, text=text)


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
    session['cart'] = 0
    return redirect(url_for('home'))


@login.user_loader
def user_load(user_id):
    return untils.get_user_by_id(user_id=user_id)

@app.route('/calendar', methods=['GET'])
def calendar():
    loinhac = get_su_kien(current_user.id)

    data = []

    for i in loinhac:
        data.append({
            "id": i.id,
            "name": i.name,
            "description": i.description,
            "badge": "Sự kiện",
            "date": i.startAt,
            "type": 'event',
        })

    return render_template('calendar.html', data=data)


@app.route('/create_task', methods=['Post', 'get'])
def create_task():
    name = request.form.get('name')
    task = request.form.get('task')
    deadline = request.form.get('deadline')
    startAt = request.form.get('startAt')
    des = request.form.get('des')
    loop = request.form.get('loop')

    hour_dl = deadline.split(':')[0]
    minute_dl = deadline.split(':')[1]

    hour_sa = startAt.split(':')[0]
    minute_sa = startAt.split(':')[1]

    deadline = datetime.now().replace(hour=int(hour_dl), minute=int(minute_dl), second=0, microsecond=0)
    startAt = datetime.now().replace(hour=int(hour_sa), minute=int(minute_sa), second=0, microsecond=0)

    add_task(user_id=current_user.id, name=name, task=task, deadline=deadline, startAt=startAt, des=des, loop=loop)

    return redirect(url_for('calendar'))
@app.route('/monhoccu')
def monhoccu():
    return render_template('monhoccu.html')

#Quản lý thu vien

@app.route("/products")
def product_list():
    cates = untils.load_categories()
    cate_id = request.args.get('category_id')
    page = request.args.get('page', 1)
    kw = request.args.get('keyword')
    products = untils.load_products(cate_id, kw, page=int(page))
    count = untils.count_product(category_id=cate_id, kw=kw)
    print(count)
    return render_template('products.html', products=products, cates=cates, kw=kw,
                           pages=math.ceil(count / app.config['PAGE_SIZE']), cate_id=cate_id)

@app.route("/products/<int:product_id>")
def product_detail(product_id):
    product = untils.get_product_by_id(product_id)

    kw = request.args.get('keyword')
    cates = untils.load_categories()
    page = request.args.get('page', 1)

    comments = untils.get_comments(product_id=product_id, page=int(page))

    if kw:
        count = untils.count_product(kw=kw)
        products = untils.load_products(None, kw, page=int(page))
        return render_template('products.html', products=products, cates=cates, kw=kw,
                               pages=math.ceil(count / app.config['PAGE_INF']))

    return render_template('product_detail.html', product=product, cates=cates, comments=comments,
                           pages=math.ceil(untils.count_comment(product_id=product_id) / app.config['COMMENT_SIZE']))


@app.route('/cart')
def cart():
    cates = untils.load_categories()

    cate_id = request.args.get('category_id')
    page = request.args.get('page', 1)
    kw = request.args.get('keyword')

    if kw:
        count = untils.count_product(kw=kw)
        products = untils.load_products(None, kw, page=int(page))
        return render_template('products.html', products=products, cates=cates, kw=kw,
                               pages=math.ceil(count / app.config['PAGE_INF']))

    return render_template('cart.html', stats=untils.count_cart(session.get(cart)))


@app.route('/api/add-cart', methods=['post'])
def add_to_cart():
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')

    # import pdb
    # pdb.set_trace()

    cart = session.get('cart')
    if not cart:
        cart = {}

    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'quantity': 1
        }

    session['cart'] = cart

    return jsonify(untils.count_cart(cart))


@app.route('/api/update-cart', methods=['put'])
def update_cart():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')

    cart = session.get('cart')

    if cart and id in cart:
        cart[id]['quantity'] = quantity
        session['cart'] = cart

    return jsonify(untils.count_cart(cart))



@app.route('/api/delete-cart/<product_id>', methods=['delete'])
def delete_cart(product_id):
    cart = session.get('cart')

    if cart and product_id in cart:
        del cart[product_id]
        session['cart'] = cart

    return jsonify(untils.count_cart(cart))


@app.route('/api/comments', methods=['post'])
def add_comment():
    data = request.json
    content = data.get('content')
    product_id = data.get('product_id')


    try:
        c = untils.add_comment(content=content, product_id=product_id)
    except:
        return {'status': 404, 'err_msg': "Chuong trinh ban"}

    return {
        'status': 201,
        'comment': {
            'id': c.id,
            'content': c.content,
            'created_date': c.created_date,
            'user': {
                'username': current_user.username,
                'avatar': current_user.avatar
            }
        }
    }

@app.route('/api/pay', methods=['post'])
def pay():

    cart = session.get('cart')

    for i in cart.values():
        untils.minus_product_quality(i['id'], i['quantity'])

    try:
        untils.add_receipt(session.get('cart'))
        del session['cart']
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})


@app.route('/api/pay2', methods=['post'])
def pay2():
    try:
        receipt = untils.add_receipt(session.get('cart'), payment=0)
        del session['cart']
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200,
                    'receipt': receipt.id,
                    'time': untils.get_rule_value('TIME')})


@app.context_processor
def common_response():
    return {
        'cates': untils.load_categories(),
        'cart_stats': untils.count_cart(session.get('cart'))
    }

@app.route("/note")
def note():
    return  render_template('note.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
