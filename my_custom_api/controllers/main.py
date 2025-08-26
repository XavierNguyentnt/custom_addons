# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json

class MyApiController(http.Controller):

    # --- API Endpoint 1: Đơn giản để test kết nối ---
    @http.route('/api/v1/test', type='http', auth='public', methods=['GET'], cors='*')
    def test_connection(self, **kw):
        """
        Endpoint công khai (public), không cần đăng nhập.
        Mục tiêu: Chỉ để React gọi thử và xác nhận kết nối thành công.
        """
        response_data = {'message': 'Hello from your Odoo API!'}
        return Response(
            json.dumps(response_data),
            status=200,
            content_type='application/json'
        )

    # --- API Endpoint 2: Lấy dữ liệu thật (Code của bạn) ---
    @http.route('/api/v1/partners', type='http', auth='user', methods=['GET'], cors='*')
    def get_partners(self, **kw):
        """
        Endpoint yêu cầu đăng nhập (user).
        Mục tiêu: Lấy dữ liệu đối tác thật sau khi đã xác thực.
        """
        try:
            fields_to_get = ['id', 'name', 'email', 'phone']
            partners = request.env['res.partner'].search_read(
                domain=[],
                fields=fields_to_get,
                limit=10
            )
            return Response(
                json.dumps(partners, default=str), # Thêm default=str để xử lý kiểu dữ liệu ngày tháng nếu có
                status=200,
                content_type='application/json'
            )
        except Exception as e:
            error_response = {
                'error': 'Internal Server Error',
                'message': str(e)
            }
            return Response(
                json.dumps(error_response),
                status=500,
                content_type='application/json'
            )
         # --- PROJECTS ---
    @http.route('/api/v1/tasks', type='http', auth='user', methods=['GET'], cors='*')
    def get_tasks(self, **kw):
        """
        Endpoint để lấy danh sách các Nhiệm vụ (Tasks).
        Yêu cầu người dùng phải đăng nhập.
        """
        try:
            # Danh sách các trường cần lấy dựa trên hình ảnh của bạn
            fields_to_get = [
                'id', 'name', 'project_id', 'partner_id', 'parent_id', 'user_ids', 
                'allocated_hours', 'effective_hours', 'subtask_effective_hours', 
                'total_hours_spent', 'remaining_hours', 'progress', 'date_deadline', 
                'activity_ids', 'my_activity_date_deadline', 'tag_ids', 
                'date_last_stage_update', 'stage_id', 'personal_stage_type_id'
            ]
            
            # Lưu ý: model là 'project.task'
            tasks = request.env['project.task'].search_read(
                [],
                fields=fields_to_get,
                limit=80 
            )
            return Response(
                json.dumps(tasks, default=str), # default=str để xử lý ngày tháng
                status=200,
                content_type='application/json'
            )
        except Exception as e:
            error_response = {
                'error': 'Internal Server Error',
                'message': str(e)
            }
            return Response(
                json.dumps(error_response),
                status=500,
                content_type='application/json'
            )
            pass
        #TEST
        # --- Lấy thông tin chi tiết của MỘT nhiệm vụ ---
    @http.route('/api/v1/tasks/<int:task_id>', type='http', auth='user', methods=['GET'], cors='*')
    def get_task_detail(self, task_id, **kw):
        task = request.env['project.task'].search_read(
            [('id', '=', task_id)],
            limit=1
        )
        if not task:
            return Response(json.dumps({'error': 'Task not found'}), status=404, content_type='application/json')
        return Response(json.dumps(task[0], default=str), status=200, content_type='application/json')

    # --- Tạo một nhiệm vụ MỚI ---
    @http.route('/api/v1/tasks', type='json', auth='user', methods=['POST'], cors='*')
    def create_task(self, **kw):
        data = request.jsonrequest
        # Cần thêm validation cho các trường bắt buộc như 'name'
        if not data.get('name'):
            return {'error': 'Title is required'}
        
        # Tạo record mới
        new_task = request.env['project.task'].create({
            'name': data.get('name'),
            'project_id': data.get('project_id'),
            'user_ids': [(6, 0, data.get('user_ids', []))], # Cú pháp đặc biệt cho Many2many
            'date_deadline': data.get('date_deadline'),
            'description': data.get('description'),
        })
        return {'id': new_task.id, 'name': new_task.name}

    # --- Cập nhật một nhiệm vụ đã có ---
    @http.route('/api/v1/tasks/<int:task_id>', type='json', auth='user', methods=['PUT'], cors='*')
    def update_task(self, task_id, **kw):
        task = request.env['project.task'].browse(task_id)
        if not task.exists():
            # Cần set status code là 404
            return {'error': 'Task not found'}
        
        data = request.jsonrequest
        task.write(data)
        return {'message': 'Task updated successfully'}