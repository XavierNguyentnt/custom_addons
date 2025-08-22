# -*- coding: utf-8 -*-
{
    'name': "Project Task Custom",
    'version': '18.0.1.0.0',
    'depends': ['project'],   # cần module project
    'author': "Your Name",
    'website': "http://yourcompany.com",
    'category': 'Project',
    'summary': "Customize Task Tree View",
    'description': """
Hiển thị thêm các cột mặc định trong list view Task của Project
    """,
    'data': [
        'views/project_task_view.xml',
    ],
    'installable': True,
    'application': False,
    'depends': ['project', 'hr_timesheet'],
}
