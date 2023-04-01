from saleapp.models import User, UserRole, Room, Message, SinhVien, Lop, Nganh, KhoaHoc, Khoa, HeDaoTao, GiangVien, Diem, MonHoc
from flask_login import current_user
from sqlalchemy import func, and_, desc, or_
from saleapp import app, db
import json
from datetime import datetime
import hashlib
from sqlalchemy.sql import extract


def get_id_by_username(username):
    id = User.query.filter(User.username.__eq__(username))

    return id.first()

def add_user(name, username, password, diachi, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(), username=username, password=password, diachi=diachi,
                email=kwargs.get('email'), avatar=kwargs.get('avatar'))



    db.session.add(user)
    db.session.commit()

    room = Room(name="Room của " + name.strip())

    db.session.add(room)

    db.session.commit()

    message = Message(room_id = room.id, user_id= user.id)

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
    room = Room.query.filter(Room.is_reply.__eq__(False))\
            .order_by(Room.date.desc())

    return room.all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_all_sinhvien():

    p = db.session.query(SinhVien.id, User.maSo, User.name, User.dob, SinhVien.gpa, Lop.name.label('tenlop'), Nganh.name.label('nganh'), SinhVien.diemRL)\
        .join(SinhVien, User.idPerson == SinhVien.id).join(Lop, SinhVien.idLop == Lop.id)\
        .join(Nganh, Lop.idNganh == Nganh.id)\
        .filter(User.userRole == UserRole.SINHVIEN)
    print(p.all()[0])
    return p.all()

def get_sinhvien_by_id(id):
    p = db.session.query(SinhVien.id, SinhVien.soTinChiDaHoc, User.idPerson, User.maSo, User.name, User.dob,
                         SinhVien.gpa, Lop.name.label('tenlop'), Nganh.name.label('nganh'),
                         SinhVien.diemRL, SinhVien.diemHeMuoi)\
        .join(SinhVien, User.idPerson == SinhVien.id).join(Lop, SinhVien.idLop == Lop.id)\
        .join(Nganh, Lop.idNganh == Nganh.id)\
        .filter(User.userRole == UserRole.SINHVIEN, User.maSo == id)
    return p.all()

def get_profile(mssv):
    p = db.session.query(User.avatar, User.email, User.name, User.sdt, User.diachi, SinhVien.gpa,
                         User.maSo, SinhVien.diemHeMuoi, SinhVien.soTinChiDaHoc,
                         SinhVien.diemRL, User.dob, User.sex, KhoaHoc.name.label('nienkhoa'), Nganh.name.label('nganh'),
                         Khoa.name.label('khoa'), User.facebook, Nganh.sumTinChi, Lop.name.label('lop'),
                         Khoa.id.label('idKhoa'))\
        .join(User, SinhVien.id == User.idPerson)\
        .join(Lop, SinhVien.idLop == Lop.id)\
        .join(KhoaHoc, Lop.idKhoaHoc == KhoaHoc.id)\
        .join(Nganh, Lop.idNganh == Nganh.id)\
        .join(HeDaoTao, Lop.idHeDaoTao == HeDaoTao.id)\
        .join(Khoa, Nganh.idKhoa == Khoa.id)\
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

    diemGiuaKi = Diem.query.filter(Diem.idSinhVien == sinhvien.id, Diem.idMonHoc == mon.id, Diem.isMidTerm.__eq__(True)).first()
    diemCuoiKi = Diem.query.filter(Diem.idSinhVien == sinhvien.id, Diem.idMonHoc == mon.id, Diem.isMidTerm.__eq__(False)).first()

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

def get_all_mon_hoc():
    p = MonHoc.query.all()

    return p

def delete_user(mssv):

    return True