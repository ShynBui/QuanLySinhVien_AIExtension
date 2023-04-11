from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship, backref
from saleapp import db, app
from datetime import datetime
from enum import Enum as UserEnum
from flask_login import UserMixin
import hashlib

class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(UserEnum):
    SINHVIEN = 1
    GIANGVIEN = 2
    NHANVIEN = 3
    SYSADMIN = 4

class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    maSo = Column(String(50), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(Text, default='https://antimatter.vn/wp-content/uploads/2022/11/anh-avatar-trang-fb-mac-dinh.jpg')
    email = Column(String(50))
    dob = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    joined_date = Column(DateTime, default=datetime.now())
    diachi = Column(String(100), nullable=False)
    userRole = Column(Enum(UserRole), default=UserRole.SINHVIEN)
    idPerson = Column(Integer, nullable=False)
    sdt = Column(String(50), default="123456789")
    queQuan = Column(String(50), default="TP.HCM")
    sex = Column(Boolean, default=True)
    facebook = Column(String(255), default="https://www.facebook.com/phat.buitien.54")

    message = relationship('Message', backref='user', lazy=True)

    def __str__(self):
        return self.name

class Room(db.Model):
    __tablename__ = 'room'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    is_reply = Column(Boolean, default=True)
    date = Column(DateTime, default=datetime.now())
    message = relationship('Message', backref='room', lazy=True)

    def __str__(self):
        return self.name

class Message(db.Model):
    __tablename__ = 'message'

    id = id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)

    content = Column(String(255), default= '')
    date = Column(DateTime, default= datetime.now())

    def __str__(self):
        return self.content

class Khoa(BaseModel):
    __tablename__ = 'khoa'

    name = Column(String(50), nullable=False)
    nganh = relationship('Nganh', backref='khoa', lazy=True)
    monhoc = relationship('MonHoc', backref='khoa', lazy=True)

    def __str__(self):
        return self.name
class Nganh(BaseModel):
    __tablename__ = 'nganh'

    name = Column(String(50), nullable=False)
    sumTinChi = Column(Integer, default=132)
    idKhoa = Column(Integer, ForeignKey(Khoa.id), nullable=False, primary_key=True)
    lop = relationship('Lop', backref='nganh', lazy=True)

    def __str__(self):
        return self.name

class HeDaoTaoRole(UserEnum):
    CHINHQUY = 1
    TUXA = 2

class HeDaoTao(BaseModel):
    __tablename__ = 'hedaotao'

    name = Column(String(50), nullable=False)
    heDaoTaoRole = Column(Enum(HeDaoTaoRole), default=HeDaoTaoRole.CHINHQUY)
    lop = relationship('Lop', backref='hetaotao', lazy=True)

    def __str__(self):
        return self.name

class KhoaHoc(BaseModel):
    __tablename__ = 'khoahoc'

    name = Column(String(50), nullable=False)
    lop = relationship('Lop', backref='khoahoc', lazy=True)
    def __str__(self):
        return self.name

class GiangVien(BaseModel):
    __tablename__ = 'giangvien'

    hocVi = Column(String(50), nullable=False)
    lop = relationship('Lop', backref='giangvien', lazy=True)
    giangvienmonhoc = relationship('GiangVienMonHoc', backref='giangvien', lazy=True)
    def __str__(self):
        return self.hocVi


class Lop(BaseModel):
    __tablename__ = 'lop'

    name = Column(String(50), nullable=False)
    idString = Column(String(50), nullable=False)
    idHeDaoTao = Column(Integer, ForeignKey(HeDaoTao.id), nullable=False)
    idNganh = Column(Integer, ForeignKey(Nganh.id), nullable=False)
    idKhoaHoc = Column(Integer, ForeignKey(KhoaHoc.id), nullable=False)
    idGiangVien = Column(Integer, ForeignKey(GiangVien.id))
    sinhvien = relationship('SinhVien', backref='lop', lazy=True)

    def __str__(self):
        return self.name

class SinhVien(BaseModel):
    __tablename__ = 'sinhvien'

    idLop = Column(Integer, ForeignKey(Lop.id), nullable=False)
    diem = relationship('Diem', backref='sinhvien', lazy=True)
    gpa = Column(Float, default=4)
    diemHeMuoi = Column(Float, default=10)
    diemRL = Column(Integer, default=100)
    soTinChiDaHoc = Column(Integer, default=0)

    def __str__(self):
        return self.name

class NhanhVien(BaseModel):
    __tablename__ = 'nhanvien'

    moTa = Column(String(255), default='')

    def __str__(self):
        return self.name


class HocKi(BaseModel):
    __tablename__= 'hocki'

    hocKi = Column(Integer, nullable=False)
    namHoc = Column(Integer, nullable=False)
    monhoc = relationship('MonHoc', backref='hocki', lazy=True)
    def __str__(self):
        return self.hocKi

class MonHoc(BaseModel):
    __tablename__= 'monhoc'

    name = Column(String(50), nullable=False)
    idString = Column(String(50), nullable=False)
    soTinChi = Column(Integer, nullable=False)
    tiLeGiuaKi = Column(Float, nullable=False)
    idKhoa = Column(Integer, ForeignKey(Khoa.id), nullable=False, primary_key=True)
    idHocKi = Column(Integer, ForeignKey(HocKi.id), nullable=False, primary_key=True)
    giangvienmonhoc = relationship('GiangVienMonHoc', backref='monhoc', lazy=True)
    diem = relationship('Diem', backref='monhoc', lazy=True)
    def __str__(self):
        return self.name

class Diem(BaseModel):
    __tablename__ = 'diem'

    idSinhVien = Column(Integer, ForeignKey(SinhVien.id), nullable=False, primary_key=True)
    idMonHoc = Column(Integer, ForeignKey(MonHoc.id), nullable=False, primary_key=True)
    diem = Column(Float, nullable=False, default=0)
    isMidTerm = Column(Boolean, default=True)

class GiangVienMonHoc(BaseModel):
    __tablename__ = 'giangvienmonhoc'

    idGiangVien = Column(Integer, ForeignKey(GiangVien.id), nullable=False, primary_key=True)
    idMonHoc = Column(Integer, ForeignKey(MonHoc.id), nullable=False, primary_key=True)


if __name__ == '__main__':
    with app.app_context():

        db.drop_all()
        db.create_all()
        password = str(hashlib.md5('1'.encode('utf-8')).hexdigest())

        hedaotao = HeDaoTao(name="Chính Quy", heDaoTaoRole=HeDaoTaoRole.CHINHQUY)
        hedaotao2 = HeDaoTao(name="Từ Xa", heDaoTaoRole=HeDaoTaoRole.TUXA)

        db.session.add_all([hedaotao, hedaotao2])
        db.session.commit()

        #Khoa
        khoa = Khoa(name="Công nghệ thông tin")
        khoa2 = Khoa(name="Tài chính ngân hàng")
        db.session.add_all([khoa, khoa2])
        db.session.commit()

        #Ngành
        nganh = Nganh(name="Công nghệ thông tin", idKhoa=khoa.id)
        nganh2 = Nganh(name="Khoa học máy tính", idKhoa=khoa.id)
        nganh3 = Nganh(name="Hệ thống thông tin quản lý", idKhoa=khoa.id)
        nganh4 = Nganh(name="Tài chính", idKhoa=khoa2.id)
        db.session.add_all([nganh, nganh2, nganh3, nganh4])
        db.session.commit()

        #KhoaHoc
        khoahoc = KhoaHoc(name="2020-2024")
        khoahoc2 = KhoaHoc(name="2021-2025")
        db.session.add_all([khoahoc, khoahoc2])
        db.session.commit()

        #HocKi
        hocki1_2019 = HocKi(hocKi= 1, namHoc=2019)
        hocki2_2019 = HocKi(hocKi=2, namHoc=2019)
        hocki3_2019 = HocKi(hocKi=3, namHoc=2019)

        hocki1_2020 = HocKi(hocKi=1, namHoc=2020)
        hocki2_2020 = HocKi(hocKi=2, namHoc=2020)
        hocki3_2020 = HocKi(hocKi=3, namHoc=2020)

        db.session.add_all([hocki1_2019, hocki2_2019,hocki3_2019,hocki1_2020,hocki2_2020,hocki3_2020])
        db.session.commit()

        #GiangVien
        giangvien = GiangVien(hocVi="Thạc sĩ")
        giangvien2 = GiangVien(hocVi="Thạc sĩ")
        giangvien3 = GiangVien(hocVi="Thạc sĩ")
        giangvien4 = GiangVien(hocVi="Thạc sĩ")

        db.session.add_all([giangvien, giangvien2, giangvien3, giangvien4])
        db.session.commit()

        #Lớp
        lop = Lop(name="DH20IT01", idString="DH20IT01", idHeDaoTao=hedaotao.id,
                  idNganh=nganh.id, idKhoaHoc=khoahoc.id, idGiangVien=giangvien.id)
        lop2 = Lop(name="DH20IT02", idString="DH20IT02", idHeDaoTao=hedaotao.id,
                  idNganh=nganh.id, idKhoaHoc=khoahoc.id, idGiangVien=giangvien.id)
        lop3 = Lop(name="DH20IT03", idString="DH20IT03", idHeDaoTao=hedaotao.id,
                  idNganh=nganh.id, idKhoaHoc=khoahoc.id, idGiangVien=giangvien.id)
        lop4 = Lop(name="DH20TN03", idString="DH20TN03", idHeDaoTao=hedaotao.id,
                   idNganh=nganh4.id, idKhoaHoc=khoahoc.id, idGiangVien=giangvien4.id)
        lop5 = Lop(name="DH20CS01", idString="DH20CS01", idHeDaoTao=hedaotao.id,
                  idNganh=nganh2.id, idKhoaHoc=khoahoc.id, idGiangVien=giangvien.id)
        lop6 = Lop(name="DH20CS02", idString="DH20CS02", idHeDaoTao=hedaotao.id,
                   idNganh=nganh2.id, idKhoaHoc=khoahoc.id, idGiangVien=giangvien.id)
        lop7 = Lop(name="DH20CS03", idString="DH20CS03", idHeDaoTao=hedaotao.id,
                   idNganh=nganh2.id, idKhoaHoc=khoahoc.id, idGiangVien=giangvien.id)
        lop8 = Lop(name="DH20IM01", idString="DH20IM01", idHeDaoTao=hedaotao.id,
                   idNganh=nganh3.id, idKhoaHoc=khoahoc.id, idGiangVien=giangvien.id)
        lop9 = Lop(name="DH20IM02", idString="DH20IM02", idHeDaoTao=hedaotao.id,
                   idNganh=nganh3.id, idKhoaHoc=khoahoc.id, idGiangVien=giangvien.id)
        db.session.add_all([lop, lop2, lop3, lop4,lop5,lop6,lop7, lop8, lop9])
        db.session.commit()

        #SinhVien
        sv1 = SinhVien(idLop=lop.id)
        sv2 = SinhVien(idLop=lop2.id)
        sv3 = SinhVien(idLop=lop3.id)
        sv4 = SinhVien(idLop=lop4.id)
        db.session.add_all([sv1,sv2,sv3, sv4])
        db.session.commit()

        #NhanVien
        nhanvien = NhanhVien()
        db.session.add_all([nhanvien])
        db.session.commit()

        #User
        user1 = User(name= "Bùi Tiến Phát", maSo= "2051052096", username="2051052096phat@ou.edu.vn",
                       password=password, email="2051052096phat@ou.edu.vn", joined_date=datetime.now(),
                       diachi="Gò Vấp", userRole=UserRole.SINHVIEN, idPerson=sv1.id,
                        dob=datetime.strptime("24-06-2002", '%d-%m-%Y').date(), avatar="https://scontent.fsgn15-1.fna.fbcdn.net/v/t39.30808-6/315256594_1475404026274288_2347858660450415372_n.jpg?_nc_cat=101&ccb=1-7&_nc_sid=09cbfe&_nc_ohc=ZKRXaulcyVsAX-XMJne&_nc_ht=scontent.fsgn15-1.fna&oh=00_AfAPEzBUT-I_d3sLAw7z6TJEe1BlCY0_9vPWimTpeRLvKw&oe=642B3E80")
        user2 = User(name= "Nguyễn Đức Hoàng", maSo= "2051052047", username="2051052047hoang@ou.edu.vn",
                       password=password, email="2051052047hoang@ou.edu.vn", joined_date=datetime.now(),
                       diachi="Gò Vấp", userRole=UserRole.SINHVIEN, idPerson=sv2.id,
                        dob=datetime.strptime("20-05-2002", '%d-%m-%Y').date(), avatar= "https://scontent.fsgn2-9.fna.fbcdn.net/v/t39.30808-6/326782477_505120801748865_4716764403425983353_n.jpg?_nc_cat=105&ccb=1-7&_nc_sid=09cbfe&_nc_ohc=Vnrbr54EYEsAX-s5KmI&_nc_ht=scontent.fsgn2-9.fna&oh=00_AfBNRAvnPTwPNLKO0gdDsJfSbtPVk8-O5rHg6Gz9mC7HqA&oe=64292660")
        user3 = User(name= "Nguyễn Văn A", maSo= "2051052069", username="2051052069a@ou.edu.vn",
                       password=password, email="2051052069phat@ou.edu.vn", joined_date=datetime.now(),
                       diachi="Gò Vấp", userRole=UserRole.SINHVIEN, idPerson=sv3.id,
                        dob=datetime.strptime("24-06-2002", '%d-%m-%Y').date())
        user4 = User(name= "Dương Hữu Thành", maSo= "GV01", username="GV01@ou.edu.vn",
                       password=password, email="GV01@ou.edu.vn", joined_date=datetime.now(),
                       diachi="Gò Vấp", userRole=UserRole.GIANGVIEN, idPerson=giangvien.id,
                        dob=datetime.strptime("24-06-2002", '%d-%m-%Y').date())
        user5 = User(name= "Nguyễn Văn Công", maSo= "GV02", username="GV02@ou.edu.vn",
                       password=password, email="GV02@ou.edu.vn", joined_date=datetime.now(),
                       diachi="Gò Vấp", userRole=UserRole.GIANGVIEN, idPerson=giangvien2.id,
                        dob=datetime.strptime("24-06-2002", '%d-%m-%Y').date())
        user7 = User(name="Lưu Quang Phuương", maSo="GV03", username="GV03@ou.edu.vn",
                     password=password, email="GV03@ou.edu.vn", joined_date=datetime.now(),
                     diachi="Gò Vấp", userRole=UserRole.GIANGVIEN, idPerson=giangvien3.id,
                     dob=datetime.strptime("24-06-1980", '%d-%m-%Y').date())
        user6 = User(name= "Bùi Tiến Phát", maSo= "ADMIN1", username="u1",
                       password=password, email="PHAT@ou.edu.vn", joined_date=datetime.now(),
                       diachi="Gò Vấp", userRole=UserRole.SYSADMIN, idPerson=nhanvien.id,
                        dob=datetime.strptime("24-06-2002", '%d-%m-%Y').date())
        user8 = User(name="Nguyễn Thị Y", maSo="2051052123", username="2051052123y@ou.edu.vn",
                     password=password, email="2051052123y@ou.edu.vn", joined_date=datetime.now(),
                     diachi="Gò Vấp 3", userRole=UserRole.SINHVIEN, idPerson=sv4.id,
                     dob=datetime.strptime("02-01-2002", '%d-%m-%Y').date(), sex=0)
        user9 = User(name="Cô Dạy Nguyên L", maSo="GV04", username="GV04@ou.edu.vn",
                     password=password, email="GV04@ou.edu.vn", joined_date=datetime.now(),
                     diachi="Gò Vấp 3", userRole=UserRole.GIANGVIEN, idPerson=giangvien4.id,
                     dob=datetime.strptime("21-01-1990", '%d-%m-%Y').date(), sex=0)
        db.session.add_all([user1, user2, user3, user4, user5, user6, user7, user8, user9])
        db.session.commit()

        #room
        room = Room(name="Room của " + user1.name.strip())
        room2 = Room(name="Room của " + user2.name.strip())
        room3 = Room(name="Room của " + user3.name.strip())
        room4 = Room(name="Room của " + user8.name.strip())

        db.session.add_all([room, room2, room3, room4])
        db.session.commit()

        #Message
        message = Message(room_id=room.id, user_id=user1.id)
        message2 = Message(room_id=room2.id, user_id=user2.id)
        message3= Message(room_id=room3.id, user_id=user3.id)
        message4 = Message(room_id=room4.id, user_id=user8.id)

        db.session.add_all([message, message2, message3, message4])
        db.session.commit()

        #Môn học
        monhoc = MonHoc(name="Lập trình cơ sở dữ liệu", idString="ITEC3406", soTinChi=3,
                        tiLeGiuaKi=0.4, idKhoa=khoa.id, idHocKi=hocki1_2019.id)
        monhoc2 = MonHoc(name="Lập trình hướng đối tượng", idString="ITEC2504", soTinChi=3,
                        tiLeGiuaKi=0.4, idKhoa=khoa.id, idHocKi=hocki1_2019.id)
        monhoc3 = MonHoc(name="An toàn hệ thống thông tin", idString="ITEC3412", soTinChi=3,
                         tiLeGiuaKi=0.4, idKhoa=khoa.id, idHocKi=hocki1_2019.id)
        monhoc4 = MonHoc(name="Nguyên lý kế toán", idString="BA3452", soTinChi=3,
                         tiLeGiuaKi=0.3, idKhoa=khoa2.id, idHocKi=hocki1_2019.id)
        db.session.add_all([monhoc, monhoc2, monhoc3, monhoc4])
        db.session.commit()

        #Điểm
        diem1 = Diem(idSinhVien=sv1.id, idMonHoc=monhoc.id, diem=10)
        diem2 = Diem(idSinhVien=sv1.id, idMonHoc=monhoc.id, diem=9, isMidTerm=False)
        diem3 = Diem(idSinhVien=sv1.id, idMonHoc=monhoc2.id, diem=10)
        diem4 = Diem(idSinhVien=sv1.id, idMonHoc=monhoc2.id, diem=7.5, isMidTerm=False)
        diem5 = Diem(idSinhVien=sv1.id, idMonHoc=monhoc3.id, diem=9)
        diem6 = Diem(idSinhVien=sv1.id, idMonHoc=monhoc3.id, diem=8, isMidTerm=False)
        db.session.add_all([diem1, diem2, diem3, diem4, diem5, diem6])
        db.session.commit()

        #Giảng viên dạy môn học
        gvmh1 = GiangVienMonHoc(idGiangVien=giangvien2.id, idMonHoc=monhoc.id)
        gvmh2 = GiangVienMonHoc(idGiangVien=giangvien.id, idMonHoc=monhoc2.id)
        gvmh3 = GiangVienMonHoc(idGiangVien=giangvien3.id, idMonHoc=monhoc3.id)
        gvmh4 = GiangVienMonHoc(idGiangVien=giangvien4.id, idMonHoc=monhoc4.id)
        db.session.add_all([gvmh1, gvmh2, gvmh3, gvmh4])
        db.session.commit()

        db.session.commit()
