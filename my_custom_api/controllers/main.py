# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json

class PartnerAPIController(http.Controller):

    @http.route('/api/partners', type='http', auth='user', methods=['GET'], cors='*')
    def get_partners(self, **kw):
        """
        Đây là API endpoint để lấy danh sách các đối tác (res.partner).
        - auth='user': Yêu cầu người dùng phải đăng nhập. Odoo sẽ tự động
                       kiểm tra 'session_id' cookie mà trình duyệt gửi lên.
        - type='http': Cho phép chúng ta toàn quyền kiểm soát response trả về.
        - cors='*': Cho phép request từ bất kỳ origin nào (quan trọng cho môi trường dev).
        """
        try:
            # 1. Truy vấn dữ liệu từ model 'res.partner'
            # Chỉ lấy các trường cần thiết để tối ưu hiệu năng
            fields_to_get = ['id', 'name', 'email', 'phone']
            partners = request.env['res.partner'].search_read(
                domain=[], # Không có điều kiện lọc, lấy tất cả
                fields=fields_to_get,
                limit=10
            )

            # 2. Tạo response thành công
            return Response(
                json.dumps(partners),
                status=200,
                content_type='application/json'
            )
        except Exception as e:
            # 3. Xử lý nếu có lỗi xảy ra
            error_response = {
                'error': 'Internal Server Error',
                'message': str(e)
            }
            return Response(
                json.dumps(error_response),
                status=500,
                content_type='application/json'
            )