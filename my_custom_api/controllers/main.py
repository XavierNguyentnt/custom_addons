# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json

class MyApiController(http.Controller):

    # --- API Endpoint 1: Test kết nối (Không thay đổi) ---
    @http.route('/api/v1/test', type='http', auth='public', methods=['GET'], cors='*')
    def test_connection(self, **kw):
        response_data = {'message': 'Hello from your Odoo API!'}
        return Response(json.dumps(response_data), status=200, content_type='application/json')

    # --- API Endpoint 2: Lấy danh sách Partners (Không thay đổi) ---
    @http.route('/api/v1/partners', type='http', auth='user', methods=['GET'], cors='*')
    def get_partners(self, **kw):
        try:
            fields_to_get = ['id', 'name', 'email', 'phone']
            partners = request.env['res.partner'].search_read(domain=[], fields=fields_to_get, limit=10)
            return Response(json.dumps(partners, default=str), status=200, content_type='application/json')
        except Exception as e:
            return self._handle_error(e)

    # --- Lấy danh sách Tasks ---
    @http.route('/api/v1/tasks', type='http', auth='user', methods=['GET'], cors='*')
    def get_tasks(self, **kw):
        try:
            fields_to_get = [
                'id', 'name', 'project_id', 'user_ids', 'date_deadline', 
                'progress', 'stage_id', 'tag_ids' 
                # Có thể rút gọn bớt các trường không cần thiết để tăng tốc độ
            ]
            tasks = request.env['project.task'].search_read([], fields=fields_to_get, limit=80)
            return Response(json.dumps(tasks, default=str), status=200, content_type='application/json')
        except Exception as e:
            # GỌI HÀM XỬ LÝ LỖI TẬP TRUNG
            return self._handle_error(e)

    # --- Lấy thông tin chi tiết của MỘT nhiệm vụ ---
    @http.route('/api/v1/tasks/<int:task_id>', type='http', auth='user', methods=['GET'], cors='*')
    def get_task_detail(self, task_id, **kw):
        try:
            # search_read vẫn là lựa chọn tốt ở đây
            task = request.env['project.task'].search_read([('id', '=', task_id)], limit=1)
            if not task:
                # CẢI THIỆN: Trả về lỗi 404 đúng chuẩn
                return Response(json.dumps({'error': 'Task not found'}), status=404, content_type='application/json')
            return Response(json.dumps(task[0], default=str), status=200, content_type='application/json')
        except Exception as e:
            return self._handle_error(e)

    # --- Tạo một nhiệm vụ MỚI ---
    @http.route('/api/v1/tasks', type='json', auth='user', methods=['POST'], cors='*')
    def create_task(self, **kw):
        data = request.jsonrequest
        if not data.get('name'):
            # CẢI THIỆN: Trả về lỗi 400 Bad Request khi thiếu dữ liệu
            return Response(json.dumps({'error': 'Task name is required'}), status=400, content_type='application/json')
        
        try:
            vals = {
                'name': data.get('name'),
                'project_id': data.get('project_id'),
                'user_ids': [(6, 0, data.get('user_ids', []))], # Cú pháp đặc biệt cho Many2many
                'date_deadline': data.get('date_deadline'),
                'description': data.get('description'),
            }
            new_task = request.env['project.task'].create(vals)
            # CẢI THIỆN: Trả về dữ liệu vừa tạo với status 201 Created
            created_data = {'id': new_task.id, 'name': new_task.name}
            return Response(json.dumps(created_data), status=201, content_type='application/json')
        except Exception as e:
            # self._handle_error sẽ trả về Response, nên ở đây ta không thể dùng trực tiếp
            # vì hàm này có type='json' và yêu cầu trả về dict.
            # Ta sẽ trả về lỗi theo cách của Odoo cho JSON RPC
            return {'error': 'Internal Server Error', 'message': str(e)}

    # --- Cập nhật một nhiệm vụ đã có ---
    @http.route('/api/v1/tasks/<int:task_id>', type='json', auth='user', methods=['PUT'], cors='*')
    def update_task(self, task_id, **kw):
        try:
            task = request.env['project.task'].browse(task_id)
            if not task.exists():
                # CẢI THIỆN: Trả về lỗi 404 khi không tìm thấy
                # Tuy nhiên, trong type='json', việc trả về Response phức tạp hơn.
                # Cách tốt nhất là raise một exception và để Odoo xử lý.
                # from odoo.exceptions import UserError
                # raise UserError('Task not found')
                return {'error': 'Task not found'} # Tạm thời vẫn trả về dict

            data = request.jsonrequest
            task.write(data)
            return {'message': 'Task {} updated successfully'.format(task_id)}
        except Exception as e:
            return {'error': 'Internal Server Error', 'message': str(e)}
            
    # --- Hàm xử lý lỗi tập trung cho type='http' ---
    def _handle_error(self, e):
        error_response = {'error': 'Internal Server Error', 'message': str(e)}
        return Response(json.dumps(error_response), status=500, content_type='application/json')