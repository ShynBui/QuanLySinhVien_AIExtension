import cloudinary.uploader

from saleapp.models import UserRole, UserReceipt
from saleapp import app, db, untils
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import request, redirect, jsonify
from datetime import datetime


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and \
            (current_user.userRole == UserRole.NHANVIEN or current_user.userRole == UserRole.SYSADMIN)


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated

class ChatAdmin(BaseView):
    @expose('/')
    def index(self):

        room = untils.get_unreply_room()
        # print(room)

        return self.render('admin/chat_admin.html', room=room, user=untils.get_user_by_id(current_user.id))

    def is_accessible(self):
        return current_user.is_authenticated and \
            (current_user.userRole == UserRole.NHANVIEN or current_user.userRole == UserRole.SYSADMIN)

class Stat(BaseView):
    @expose('/')
    def index(self):
        return self.render('stat.html', admin=UserRole.SYSADMIN)

    def is_accessible(self):
        return current_user.is_authenticated and \
            (current_user.userRole == UserRole.NHANVIEN or current_user.userRole == UserRole.SYSADMIN)

class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

class ViewUserDetail(BaseView):
    @expose('/')
    def index(self):
        student = untils.get_all_sinhvien()
        mssv = request.args.get('value')

        if mssv:
            student = untils.get_sinhvien_by_id(mssv)
            return self.render('admin/sinhviendetail.html', student=student,
                               user=untils.get_user_by_id(current_user.id))

        return self.render('admin/sinhviendetail.html', student=student, user=untils.get_user_by_id(current_user.id))
    def is_accessible(self):
        return current_user.is_authenticated and \
            (current_user.userRole == UserRole.NHANVIEN or current_user.userRole == UserRole.SYSADMIN)

class DeleteView(BaseView):
    @expose('/')
    def index(self):
        id = request.args.get('value')
        pay = request.args.get('payment')

        product = untils.get_product_by_id2(id)

        all_product = untils.get_all_product()

        quote = ''

        if id and not product:
            quote = 'Không có sản phẩm hợp lệ!'

        if product:
            return self.render('admin/delete.html', id=id, products=all_product, product=product, pay = pay, quote=quote)
        if pay:
            quote = 'Xóa thành công'
            untils.delete_product_by_id(pay)
            # return redirect('/admin/deleteview')

        return self.render('admin/delete.html', products=untils.get_all_product(), product=product, pay=pay, quote=quote)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.userRole == UserRole.SYSADMIN


class PayView(BaseView):
    @expose('/')
    def __index__(self):

        id = request.args.get('value')
        receipt = untils.get_all_receipt_not_pay(id)
        pay = request.args.get('payment')

        # time = untils.get_time(id)

        out_date = untils.get_all_receipt_out_of_date()
        # print(out_date)

        if receipt:
            buyer_name = untils.get_user_name(id)
            date = untils.get_date_receipt(id)
            total = untils.get_total_price_by_id(id)

            return self.render('admin/payment.html', receipt=receipt, user=current_user, name=buyer_name, date=date,
                               total=total, id=id, success=None)

        if pay:
            user_receipt = UserReceipt(user_id=int(current_user.id), receipt_id=int(pay))
            untils.change_receipt_payment_by_id(pay)
            receipt = untils.get_receipt_by_id(pay)

            for i in receipt:
                untils.minus_product_quality(i[4], i[2])

            receipt = None

        return self.render('admin/payment.html', receipt=receipt, user=current_user, success=1, id=id, out_date=out_date, time= datetime.now())

    def is_accessible(self):
        return current_user.is_authenticated and (
                    current_user.userRole == UserRole.SYSADMIN or current_user.userRole == UserRole.NHANVIEN)


class ImportView(BaseView):
    @expose('/')
    def __index__(self):

        name = request.args.get('name')
        quantity = request.args.get('soluong')
        mota = request.args.get('mota')
        price = request.args.get('gia')
        avatar_path = 'https://cdn.tgdd.vn/Products/Images/42/235838/Galaxy-S22-Ultra-Burgundy-600x600.jpg'

        avatar = request.files.get('avatar')
        if avatar:
            res = cloudinary.uploader.upload(avatar)
            avatar_path = res['secure_url']

        if name:
            category = request.args.get('theloai')
            tacgia = request.args.get('tacgia')

            return self.render('admin/import.html', min=untils.get_rule_value('MINIMUM_IMPORT'),
                               quote=untils.add_product(name=name, category=category, author=tacgia, quantity=quantity,
                                                        price=price, mota=mota, avatar=avatar_path))

        return self.render('admin/import.html', min=untils.get_rule_value('MINIMUM_IMPORT'))

    def is_accessible(self):
        return current_user.is_authenticated and (
                    current_user.userRole == UserRole.SYSADMIN or current_user.userRole == UserRole.NHANVIEN)

class Register(BaseView):
    @expose('/')
    def __index__(self):

        return redirect('/register')

    def is_accessible(self):
        return current_user.is_authenticated and (
                    current_user.userRole == UserRole.SYSADMIN or current_user.userRole == UserRole.NHANVIEN)

admin = Admin(app=app, name='QUẢN TRỊ SINH VIÊN', template_mode='bootstrap4',
              index_view=MyAdminIndex())

admin.add_view(ChatAdmin(name='Chat Admin'))
admin.add_view(ViewUserDetail(name='User Detail'))
admin.add_view(Stat(name='Thống kê'))
admin.add_view(DeleteView(name='Xóa sách'))
admin.add_view(ImportView(name='Thêm sách'))
admin.add_view(PayView(name='Hóa đơn'))
admin.add_view(Register(name='Đăng kí'))
admin.add_view(LogoutView(name='Logout'))
