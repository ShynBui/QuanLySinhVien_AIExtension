from saleapp.models import User, UserRole, Room, Message, SinhVien, HocKi, Lop, Nganh, KhoaHoc, Khoa, HeDaoTao, \
    GiangVien, Diem, MonHoc
from flask_login import current_user
from sqlalchemy import func, and_, desc, or_
from saleapp import app, db, question_answerer, model_multiple, model_gk_ck_nhapmon, summarizer
import json
from datetime import datetime
import hashlib
from sqlalchemy.sql import extract
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def get_id_by_username(username):
    id = User.query.filter(User.username.__eq__(username))

    return id.first()


def add_user(name, username, password, diachi, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    print(kwargs.get('dob'))
    maSo1 = kwargs.get('email').split('@')[0]
    maso = ''
    for i in maSo1:
        if i.isnumeric():
            maso = maso + i

    print(maso)

    sinhvien = SinhVien(idLop=1)
    db.session.add(sinhvien)
    db.session.commit()

    user = User(name=name.strip(), username=username, password=password, diachi=diachi,
                email=kwargs.get('email'), avatar=kwargs.get('avatar'), maSo=maso, userRole=UserRole.SINHVIEN,
                idPerson=sinhvien.id, dob=kwargs.get('dob'))

    # user1 = User(name="Bùi Tiến Phát", maSo="2051052096", username="2051052096phat@ou.edu.vn",
    #              password=password, email="2051052096phat@ou.edu.vn", joined_date=datetime.now(),
    #              diachi="Gò Vấp", userRole=UserRole.SINHVIEN, idPerson=sv1.id,
    #              dob=datetime.strptime("24-06-2002", '%d-%m-%Y').date(), avatar='')

    db.session.add(user)
    db.session.commit()

    room = Room(name="Room của " + name.strip())

    db.session.add(room)

    db.session.commit()

    message = Message(room_id=room.id, user_id=user.id)

    db.session.add(message)

    db.session.commit()


def save_chat_message(room_id, message, user_id):
    message = Message(content=message, room_id=room_id, user_id=user_id)

    db.session.add(message)

    db.session.commit()


def load_message(room_id):
    message = Message.query.filter(Message.room_id.__eq__(room_id))

    return message.all()


def load_user_send(room_id):
    message = Message.query.filter(Message.room_id.__eq__(room_id))

    return message.all()


def get_chatroom_by_user_id(id):
    id_room = Message.query.filter(Message.user_id.__eq__(id))

    print(id_room)
    return id_room.first()


def get_chatroom_by_room_id(id):
    id_room = Message.query.filter(Message.room_id.__eq__(id))

    print(id_room.first())
    return id_room.first()


def get_chat_room_by_user_id(id):
    message = Message.query.filter(Message.user_id == id).first()

    room = Room.query.filter(Room.id == message.room_id)

    return room.first()


def change_room_status(id, change):
    id_room = Room.query.filter(Room.id.__eq__(id)).first()

    id_room.is_reply = change

    db.session.commit()


def check_login(username, password, role=UserRole.SINHVIEN):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username),
                                 User.password.__eq__(password),
                                 User.userRole.__eq__(role)).first()


def check_admin_login(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username),
                                 User.password.__eq__(password),
                                 User.userRole != UserRole.SINHVIEN).first()


def get_unreply_room():
    room = Room.query.filter(Room.is_reply.__eq__(False)) \
        .order_by(Room.date.desc())

    return room.all()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_all_sinhvien():
    p = db.session.query(SinhVien.id, User.maSo, User.name, User.dob, SinhVien.gpa, Lop.name.label('tenlop'),
                         Nganh.name.label('nganh'), SinhVien.diemRL) \
        .join(SinhVien, User.idPerson == SinhVien.id).join(Lop, SinhVien.idLop == Lop.id) \
        .join(Nganh, Lop.idNganh == Nganh.id) \
        .filter(User.userRole == UserRole.SINHVIEN)
    return p.all()


def get_sinhvien_by_id(id):
    p = db.session.query(SinhVien.id, SinhVien.soTinChiDaHoc, User.idPerson, User.maSo, User.name, User.dob,
                         SinhVien.gpa, Lop.name.label('tenlop'), Nganh.name.label('nganh'),
                         SinhVien.diemRL, SinhVien.diemHeMuoi) \
        .join(SinhVien, User.idPerson == SinhVien.id).join(Lop, SinhVien.idLop == Lop.id) \
        .join(Nganh, Lop.idNganh == Nganh.id) \
        .filter(User.userRole == UserRole.SINHVIEN, User.maSo == id)
    return p.all()


def get_host_room_avatar(room_id):
    user = Message.query.filter(Message.room_id.__eq__(room_id),
                                Message.content.__eq__('')).first()

    username = get_user_by_id(user.user_id);

    return username.avatar


def get_chatroom_by_id(id):
    id_room = Room.query.filter(Room.id.__eq__(id))
    id_room[0]

    return id_room.first();


def get_profile(mssv):
    p = db.session.query(User.id.label('user_id'), User.avatar, User.email, User.name, User.sdt, User.diachi,
                         SinhVien.gpa,
                         User.maSo, SinhVien.diemHeMuoi, SinhVien.soTinChiDaHoc,
                         SinhVien.diemRL, User.dob, User.sex, KhoaHoc.name.label('nienkhoa'), Nganh.name.label('nganh'),
                         Khoa.name.label('khoa'), User.facebook, Nganh.sumTinChi, Lop.name.label('lop'),
                         Khoa.id.label('idKhoa')) \
        .join(User, SinhVien.id == User.idPerson) \
        .join(Lop, SinhVien.idLop == Lop.id) \
        .join(KhoaHoc, Lop.idKhoaHoc == KhoaHoc.id) \
        .join(Nganh, Lop.idNganh == Nganh.id) \
        .join(HeDaoTao, Lop.idHeDaoTao == HeDaoTao.id) \
        .join(Khoa, Nganh.idKhoa == Khoa.id) \
        .filter(User.maSo.__eq__(mssv), User.userRole == UserRole.SINHVIEN)

    return p.first()


def change_profile(mssv, name, dob, sex, email, phone, diachi):
    user = User.query.filter(User.maSo.__eq__(mssv)).first()

    user.name = name
    user.dob = datetime.strptime(dob, "%Y-%m-%d").date()
    if sex == '1':
        user.sex = True
    else:
        user.sex = False
    db.session.commit()
    user.email = email
    user.sdt = phone
    user.diachi = diachi

    db.session.commit()

    return True


def get_all_nganh(khoa=None):
    if khoa:
        p = Nganh.query.filter(Nganh.idKhoa == khoa)
        return p.all()

    p = Nganh.query.all()

    return p


def get_all_lop(nganh=None):
    if nganh:
        p = Lop.query.filter(Lop.idNganh == nganh)
        return p.all()

    p = Lop.query.all()

    return p


def get_user_by_idPerSon(idPerson):
    user = User.query.filter(User.idPerson == idPerson)

    return user.first()


def get_SinhVien_by_id(id):
    sv = SinhVien.query.get(id)

    return sv


def save2(mssv, idLop):
    sinhvien = get_sinhvien_by_id(mssv)[0]
    sinhvienTrue = get_SinhVien_by_id(sinhvien.id)

    sinhvienTrue.idLop = idLop

    db.session.commit()
    return True


def get_all_khoa():
    p = Khoa.query.all()

    return p


def get_khoahoc_by_id(id):
    p = KhoaHoc.query.filter(KhoaHoc.id == id)

    return p.first()


def get_top_mon_theo_ky(idmon, idhocky):
    monhoc = MonHoc.query.filter(MonHoc.idHocKi.__eq__(idhocky),
                                 MonHoc.id.__eq__(idmon)).first()

    if monhoc:
        diem = db.session.query(Diem.diem, Diem.isMidTerm, MonHoc.tiLeGiuaKi, MonHoc.name, MonHoc.id) \
            .join(MonHoc, Diem.idMonHoc.__eq__(MonHoc.id)) \
            .filter(Diem.idMonHoc.__eq__(monhoc.id))
    else:
        return []

    return diem.all()


def get_nganh_by_id(id):
    p = Nganh.query.filer(Nganh.id == id)

    return p.first()


def get_lop_by_id_lop(id):
    p = Lop.query.filter(Lop.id == id)

    return p.first()


def get_id_mon_by_id_string(idString):
    p = MonHoc.query.filter(MonHoc.idString.__eq__(idString))

    if p.first():
        return p.first().id
    return None


def get_sinh_vien_theo_khoa():

    sinhvien = db.session.query(db.func.count(SinhVien.id).label('count'), Khoa.name.label('tenkhoa')) \
        .join(Lop, Lop.id == SinhVien.idLop) \
        .join(Nganh) \
        .join(Khoa) \
        .group_by(Khoa.name).order_by(db.func.count(SinhVien.id).desc())
    print(sinhvien.all())

    return sinhvien.all()


def get_mon_by_string(chuoi):
    p = MonHoc.query.filter(or_(MonHoc.idString.like('%{}%'.format(chuoi)),
                                MonHoc.name.like('%{}%'.format(chuoi)))).all()

    # print("Mon tim", p)
    return p


def update_diem_by_maSo(mssv, diemHeMuoi, diemHeBon, tongTinChi):
    id = User.query.filter(User.maSo.__eq__(mssv)).first().idPerson

    p = SinhVien.query.filter(SinhVien.id == id).first()

    p.gpa = diemHeBon
    p.diemHeMuoi = diemHeMuoi
    p.soTinChiDaHoc = tongTinChi
    db.session.commit()


def get_all_hocki():
    hocki = HocKi.query.all()

    return hocki


def xem_all_diem_gk_by_ma_so(maSo, maMon=None):
    sinhvien = User.query.filter(User.maSo.__eq__(maSo)).first()

    p = Diem.query.filter(sinhvien.idPerson == Diem.idSinhVien, Diem.isMidTerm.__eq__(True))

    if maMon:
        s = get_id_mon_by_id_string(maMon)
        if s:
            p = Diem.query.filter(sinhvien.idPerson == Diem.idSinhVien, Diem.isMidTerm.__eq__(True),
                                  int(s) == Diem.idMonHoc)
            if p.first():
                return [p.first()]

    if p.all():
        return p.all()
    return []


def xoa_mon(mssv, mon):
    mon = MonHoc.query.filter(MonHoc.idString.__eq__(mon)).first()

    sinhvien = get_sinhvien_by_id(mssv)[0]

    diem = Diem.query.filter(Diem.idMonHoc == mon.id, Diem.idSinhVien == sinhvien.id).all()

    print(diem)

    db.session.delete(diem[0])
    db.session.delete(diem[1])
    db.session.commit()

    return True


def them_mon(mssv, mon):
    mon = MonHoc.query.filter(MonHoc.idString.__eq__(mon)).first()

    sinhvien = get_sinhvien_by_id(mssv)[0]

    diem1 = Diem(idSinhVien=sinhvien.id, idMonHoc=mon.id, diem=0, isMidTerm=True)
    diem2 = Diem(idSinhVien=sinhvien.id, idMonHoc=mon.id, diem=0, isMidTerm=False)

    db.session.add_all([diem1, diem2])
    db.session.commit()

    return True


def update_diem(mon, mssv, giuaki, cuoiki):
    mon = MonHoc.query.filter(MonHoc.idString.__eq__(mon)).first()

    sinhvien = get_sinhvien_by_id(mssv)[0]

    diemGiuaKi = Diem.query.filter(Diem.idSinhVien == sinhvien.id, Diem.idMonHoc == mon.id,
                                   Diem.isMidTerm.__eq__(True)).first()
    diemCuoiKi = Diem.query.filter(Diem.idSinhVien == sinhvien.id, Diem.idMonHoc == mon.id,
                                   Diem.isMidTerm.__eq__(False)).first()

    diemGiuaKi.diem = giuaki
    diemCuoiKi.diem = cuoiki

    db.session.commit()
    return True


def xem_all_diem_ck_by_ma_so(maSo, maMon=None):
    sinhvien = User.query.filter(User.maSo == maSo).first()

    p = Diem.query.filter(sinhvien.idPerson == Diem.idSinhVien, Diem.isMidTerm.__eq__(False))
    if maMon:
        s = get_id_mon_by_id_string(maMon)
        if s:
            p = Diem.query.filter(sinhvien.idPerson == Diem.idSinhVien, Diem.isMidTerm.__eq__(False),
                                  s == Diem.idMonHoc)
            if p.first():
                return [p.first()]
    if p.all():
        return p.all()
    return []


def get_mon_hoc_by_ma_diem(id):
    p = MonHoc.query.filter(MonHoc.id == id)

    return p.first()


def get_ten_hoc_ki_by_id(id):
    hocki = HocKi.query.filter(HocKi.id.__eq__(id)).first()

    return hocki


def get_all_mon_hoc(idKhoa=None):
    if idKhoa:
        p = MonHoc.query.filter(MonHoc.idKhoa.__eq__(idKhoa))
        return p.all()

    p = MonHoc.query.all()

    return p


def delete_user(mssv):
    user = User.query.filter(User.maSo.__eq__(mssv)).first()

    sinhvien = SinhVien.query.filter(SinhVien.id == user.idPerson).first()

    diem = Diem.query.filter(Diem.idSinhVien == sinhvien.id).all()

    message = Message.query.filter(Message.user_id == user.id).all()

    room = Room.query.filter(Room.id == message[0].room_id).first()

    for i in message:
        db.session.delete(i)
        db.session.commit()

    for i in diem:
        db.session.delete(i)
        db.session.commit()

    db.session.delete(user)
    db.session.commit()
    db.session.delete(room)
    db.session.commit()
    db.session.delete(sinhvien)

    db.session.commit()

    return True


def predict_question_answering(context, question, answer0, answer1, answer2, answer3):
    answers = [answer0, answer1, answer2, answer3]
    key = question_answerer(question=question, context=context)['answer']

    embedding_answer = model_multiple.encode(answers)
    embedding_key = model_multiple.encode(key)

    result = cosine_similarity(
        [embedding_key],
        embedding_answer
    )

    index = 0
    max = -999

    for i in range(len(answers)):
        if (result[0][i] > max):
            max = result[0][i]
            index = i

    return chr(ord('A') + index) + ". " + answers[index]


def predict_question(context, question):
    key = question_answerer(question=question, context=context)['answer']

    return key


def predict_gk_ck_nhapmon(diemGK):
    return model_gk_ck_nhapmon.predict(np.array([diemGK]).reshape(-1, 1))[0]


def summary(text):
    return summarizer(text, max_length=100, min_length=20, do_sample=False)[0]['summary_text']


def addTen(data, mssv, hoten):
    for i in range(len(data)):
        if data.iloc[i].maso not in mssv:
            mssv.append(data.iloc[i].maso)
            hoten.append(data.iloc[i].ho + " " + data.iloc[i].ten)

    return [mssv, hoten]


def changedata(data, data1):
    mssv = []
    diem = []
    for i in range(len(data1)):
        mssv.append(data1.iloc[i].maso)
        diem.append(data1.iloc[i].diem)

    for i in range(len(data)):
        if data.iloc[i].mssv in mssv:
            data.loc[data['mssv'] == data.iloc[i].mssv, 'diem'] = float(
                data.loc[data['mssv'] == data.iloc[i].mssv, 'diem']) + diem[mssv.index(data.iloc[i].mssv)]
        else:
            data.loc[data['mssv'] == data.iloc[i].mssv, 'diem'] = float(
                data.loc[data['mssv'] == data.iloc[i].mssv, 'diem']) + min(diem)
