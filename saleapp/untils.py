from saleapp.models import User, UserRole, Room, Message, SinhVien, HocKi, Lop, Nganh, KhoaHoc, Khoa,HeDaoTao, \
    GiangVien, Diem, MonHoc, Category, Rule, PhieuNhapSach, ChiTietNhapSach, Product, User, UserRole, SachTacGia, Receipt, \
    ReceiptDetail, Comment, UserReceipt, TacGia
from flask_login import current_user
from sqlalchemy import func, and_, desc, or_
from saleapp import app, db, question_answerer, model_multiple, model_gk_ck_nhapmon, summarizer
import json
from datetime import datetime, timedelta
import hashlib
from sqlalchemy.sql import extract
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from saleapp.decoding import decoding_no1
from saleapp.encoding import encoding_no1

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
    print(user)

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


def change_profile(mssv, name, dob, sex, email, phone, diachi, diemrl):
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

    sinhvien = SinhVien.query.filter(SinhVien.id == user.idPerson).first()

    sinhvien.diemRL = diemrl
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


#Quan ly thu vien
def load_categories():
    return Category.query.all()
    # return read_json(os.path.join(app.root_path, 'data/categories.json'))


def load_products(cate_id=None, name=None, page=1):
    products = Product.query.filter(Product.active.__eq__(True))

    if cate_id:
        products = products.filter(Product.category_id.__eq__(cate_id))
    if name:
        products = products.filter(Product.name.contains(name))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return products.slice(start, end).all()


def load_all_products():
    products = Product.query.filter(Product.active.__eq__(True))
    print(products)
    return products


def get_product_by_id(product_id):
    # products = read_json(os.path.join(app.root_path, 'data/products.json'))
    #
    # for p in products:
    #     if p['id'] == product_id:
    #         return p

    products = Product.query.get(product_id)

    return products


def get_all_product():
    p = db.session.query(Product.id, Product.name, Category.name, Product.quantity, Product.price) \
        .filter(Product.category_id.__eq__(Category.id))

    # print(p)

    return p.all()


def get_product_by_id2(product_id):
    p = p = db.session.query(Product.id, Product.name, Category.name, Product.quantity, Product.price) \
        .filter(Product.category_id.__eq__(Category.id), Product.id.__eq__(product_id))

    print(p.first())

    return p.first()


def get_rule_value(name):
    return Rule.query.filter(Rule.name.__eq__(name)).first().value


def delete_chi_tiet_nhap_sach_by_id(id):
    p = ChiTietNhapSach.query.filter(ChiTietNhapSach.product_id.__eq__(id)).first()

    if p:
        db.session.delete(p)
        db.session.commit()


def delete_sach_tac_gia_by_id(id):
    p = SachTacGia.query.filter(SachTacGia.product_id.__eq__(id)).first()
    if p:
        db.session.delete(p)
        db.session.commit()


def delete_receipt_detail_by_id(id):

    p = ReceiptDetail.query.filter(ReceiptDetail.product_id.__eq__(id)).all()

    if p:
        for i in p:
            db.session.delete(i)
            db.session.commit()

def delete_comment_by_id(id):
    p = Comment.query.filter(Comment.product_id.__eq__(id)).all()

    if p:
        for i in p:
            db.session.delete(i)
            db.session.commit()

def delete_product_by_id(id):
    product = Product.query.get(id)

    if product:
        delete_chi_tiet_nhap_sach_by_id(id)
        delete_receipt_detail_by_id(id)
        delete_sach_tac_gia_by_id(id)
        delete_comment_by_id(id)
        db.session.delete(product)
        db.session.commit()


def count_product(category_id=None, kw=None):
    p = Product.query.filter(Product.active.__eq__(True))
    if category_id:
        return p.filter(Product.category_id.__eq__(category_id)).count()
    if kw:
        return p.filter(Product.name.contains(kw)).count()
    return p.count()


def minus_product_quality(id, value):
    product = Product.query.filter(Product.id.__eq__(id)).first()

    product.quantity -= int(value)

    db.session.commit()


def add_user(name, username, password, diachi, queQuan, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    # print(kwargs.get('dob'))
    maso = kwargs.get('maSo')
    avatar = kwargs.get('avatar')
    lop = Lop.query.get(1)
    sv = SinhVien(idLop=lop.id)
    sv.session.add(sv)
    db.session.commit()


    user = User(name=name.strip(), username=username, password=password, email=encoding_no1(kwargs.get('email')),diachi=diachi, queQuan=queQuan,
                 dob=kwargs.get('dob'), sdt=kwargs.get('phone'), idPerson=sv.id, maSo=maso,joined_date=datetime.now(), userRole=UserRole.SINHVIEN,
                avatar=avatar)

    db.session.add_all([user])

    db.session.commit()

    room = Room(name="Room của " + name.strip())

    db.session.add(room)

    db.session.commit()

    message = Message(room_id=room.id, user_id=user.id)

    db.session.add(message)

    db.session.commit()
    print("a")

def get_date_receipt(id):
    return Receipt.query.filter(Receipt.id.__eq__(id)).first().created_date


def get_user_name(id):
    id = UserReceipt.query.filter(UserReceipt.receipt_id.__eq__(id)).first().user_id

    return User.query.filter(User.id.__eq__(id)).first().name


def get_time(id):
    receipt = get_date_receipt(id)
    # print(receipt)
    # print(receipt + timedelta(hours=48))
    # print(datetime.now())
    # print(datetime.now() > receipt + timedelta(hours=48))

def get_all_receipt_out_of_date():
    hours = get_rule_value('TIME')
    time = datetime.now() - timedelta(hours=hours)
    print(time)
    p = Receipt.query.filter(Receipt.payment.__eq__(False), (Receipt.created_date < time))

    return p.all()

def get_all_receipt_not_pay(id=None):
    receipt = Receipt.query.filter(Receipt.id.__eq__(id)).first()
    hours = get_rule_value('TIME')

    # print(receipt.created_date)
    # print(datetime.now())
    # print(receipt.created_date + timedelta(hours=48))
    # print(receipt.created_date + timedelta(hours=48) < datetime.now())

    if receipt:
        if receipt.payment == False:
            if (receipt.created_date + timedelta(hours=hours) > datetime.now()):
                p = db.session.query(Product.name, Category.name, ReceiptDetail.quantity, ReceiptDetail.unit_price,
                                     Product.id) \
                    .join(Product, Product.id.__eq__(ReceiptDetail.product_id)) \
                    .filter(
                    and_(
                        ReceiptDetail.receipt_id.__eq__(id)),
                    Category.id.__eq__(Product.category_id),
                )

                # print(p.all())
                return p.all()


def get_receipt_by_id(id):
    p = db.session.query(Product.name, Category.name, ReceiptDetail.quantity, ReceiptDetail.unit_price, Product.id) \
        .join(Product, Product.id.__eq__(ReceiptDetail.product_id)) \
        .filter(
        and_(
            ReceiptDetail.receipt_id.__eq__(id)),
        Category.id.__eq__(Product.category_id)
    )

    # print(p.all())
    return p.all()


def get_total_price_by_id(id):
    p = db.session.query(ReceiptDetail.receipt_id, func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .filter(ReceiptDetail.receipt_id.__eq__(id)) \
        .group_by(ReceiptDetail.receipt_id)
    return p.first()[1]


def add_phieunhapsach():
    phieu = PhieuNhapSach()
    db.session.add(phieu)
    db.session.commit()

    return phieu


def add_chitietnhapsach(product, phieu, quantity):
    chitet = ChiTietNhapSach(product_id=product.id, phieunhapsach_id=phieu.id, quantity=quantity)

    db.session.add(chitet)
    db.session.commit()
    return chitet


def add_sachtacgia(product, tacgia):
    sactacgia = SachTacGia(product_id=product.id, tacgia_id=tacgia.id)
    db.session.add(sactacgia)
    db.session.commit()

    return sactacgia


def add_product(name, category, author, quantity, mota, avatar, price, **kwargs):
    soluong = get_rule_value('MINIMUM_IMPORT')
    limit = get_rule_value('MINIMUM_LIMIT')

    product = Product.query.filter(Product.name.__eq__(name)).first()

    if not product:
        cate = add_category(category)
        tacgia = add_author(author)

        product = Product(name=name, category_id=cate.id, quantity=quantity, description=mota, image=avatar,
                          price=price)
        db.session.add(product)
        phieu = add_phieunhapsach()
        chitiet = add_chitietnhapsach(product=product, phieu=phieu, quantity=quantity)
        sactacgia = add_sachtacgia(product=product, tacgia=tacgia)

        db.session.commit()

        return 'Nhập thành công'
    else:
        if product.quantity < limit:
            product.quantity += int(quantity)
            db.session.commit()
            return 'Thêm số lượng thành công'
        else:
            return 'Số lượng trong kho lớn hơn 300'


def add_author(name):
    tacgia = TacGia.query.filter(TacGia.name.__eq__(name)).first()

    if not tacgia:
        tacgia = TacGia(name=name)
        db.session.add(tacgia)
        db.session.commit()

    return tacgia


def add_category(name):
    cate = Category.query.filter(Category.name.__eq__(name)).first()

    if not cate:
        cate = Category(name=name)
        db.session.add(cate)
        db.session.commit()

    return cate


def category_stats():
    '''
    SELECT c.id, c.name, count(p.id)
    FROM category c left outer join product p on c.id = p.id
    Group by c.name, c.id
    '''

    # return Category.query.join(Product, Product.category_id.__eq__(Category.id)).add_columns(func.count(Product.id)).group_by(Category.id, Category.name).all()
    with app.app_context():
        return db.session.query(Category.id, Category.name, func.count(Product.id)) \
            .join(Product, Product.category_id.__eq__(Category.id), isouter=True) \
            .group_by(Category.id).all()


def products_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Product.id, Product.name, func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .join(ReceiptDetail, ReceiptDetail.product_id.__eq__(Product.id), isouter=True) \
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id)) \
        .group_by(Product.id, Product.name)

    # print(p)

    if kw:
        p = p.filter(Product.name.contains(kw))
    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date))
    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date))

    return p.all()


def change_receipt_payment_by_id(id):
    r = Receipt.query.filter(Receipt.id.__eq__(int(id))).first()

    r.payment = True

    db.session.commit()


def add_receipt(cart, payment=1):
    if cart:
        # receipt = Receipt(user=current_user)
        receipt = Receipt(payment=payment)

        user_receipt = UserReceipt(user=current_user, receipt=receipt)

        db.session.add(receipt)
        db.session.add(user_receipt)

        for c in cart.values():
            d = ReceiptDetail(receipt=receipt,
                              product_id=c['id'],
                              quantity=c['quantity'],
                              unit_price=c['price'])
            db.session.add(d)

    db.session.commit()

    return receipt


def count_cart(cart):
    total_quantity, total_amount = 0, 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        'total_amount': total_amount,
        'total_quantity': total_quantity
    }


def add_comment(content, product_id):
    c = Comment(content=content, product_id=product_id, user=current_user)

    db.session.add(c)
    db.session.commit()

    return c


def get_comments(product_id, page=1):
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return Comment.query.filter(Comment.product_id.__eq__(product_id)).order_by(-Comment.id).slice(start,
                                                                                                   start + page_size).all()


def product_month_stats(year):
    p = db.session.query(extract('month', Receipt.created_date),
                         func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .join(ReceiptDetail, ReceiptDetail.receipt_id.__eq__(Receipt.id)) \
        .filter(extract('year', Receipt.created_date).__eq__(year)) \
        .group_by(extract('month', Receipt.created_date)) \
        .order_by(extract('month', Receipt.created_date))
    # print(p)
    return p.all()


def count_comment(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).count()


def total_price_month(month=12):
    p = db.session.query(extract('month', Receipt.created_date),
                         func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id)) \
        .filter(
        and_(
            extract('month', Receipt.created_date).__eq__(month),
            Receipt.payment.__eq__(1)
        )
    ) \
        .group_by(extract('month', Receipt.created_date)).all()

    print(p)
    return p


def category_month_stats(month=12):
    total = total_price_month(month)

    if total:
        p = db.session.query(Category.name, func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price),
                             func.sum(ReceiptDetail.quantity),
                             func.round(
                                 func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price) / total[0][1] * 100), 3) \
            .join(Product, Product.id.__eq__(ReceiptDetail.product_id)) \
            .join(Category, Category.id.__eq__(Product.category_id)) \
            .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id)) \
            .filter(
            and_(
                extract('month', Receipt.created_date).__eq__(month),
                Receipt.payment.__eq__(1)
            )
        ) \
            .group_by(Category.name)

        print(p)
        return p.all()

    return {}


def total_product_month(month):
    p = db.session.query(extract('month', Receipt.created_date),
                         func.sum(ReceiptDetail.quantity)) \
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id)) \
        .filter(
        and_(
            extract('month', Receipt.created_date).__eq__(month),
            Receipt.payment.__eq__(1)
        )
    ) \
        .group_by(extract('month', Receipt.created_date)).all()

    return p


def product_count_month_stats(month=12):
    total = total_product_month(month)

    if total:
        p = db.session.query(Product.name, Category.name, func.sum(ReceiptDetail.quantity),
                             func.round(func.sum(ReceiptDetail.quantity) / total[0][1] * 100), 3) \
            .join(Product, Product.category_id.__eq__(Category.id)) \
            .join(ReceiptDetail, Product.id.__eq__(ReceiptDetail.product_id)) \
            .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id)) \
            .filter(
            and_(
                extract('month', Receipt.created_date).__eq__(month),
                Receipt.payment.__eq__(1)
            )
        ) \
            .group_by(Product.name, Category.name)

        print(p)
        return p.all()

    return {}