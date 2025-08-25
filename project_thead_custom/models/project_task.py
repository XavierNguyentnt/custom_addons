# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime

class ProjectTask(models.Model):
    """
    Kế thừa model project.task để tự động hóa hoàn toàn việc tính toán thời gian.
    """
    _inherit = "project.task"

    # ===================================================================
    # GHI ĐÈ: Thay đổi nhãn gốc của trường partner_id
    # Thao tác này sẽ thay đổi "Customer" thành "Reviewer" ở MỌI NƠI
    # trong hệ thống cho model project.task.
    # ===================================================================
    partner_id = fields.Many2one(string=_('Reviewer'))

    # ===================================================================
    # Trạng thái Deadline
    # ===================================================================
    deadline_status = fields.Selection(
        [
            ('on_time', _('In Progress')),
            ('late', _('Overdue')),
            ('done_early', _('Done Ahead of Schedule')),
            ('done_on_time', _('Done On Time')),
            ('done_late', _('Done Late')),
        ],
        string=_("Deadline Status"),
        compute='_compute_deadline_status',
        store=True,
        help=_("Status of the task in relation to its deadline.")
    )

    # Các trường tính toán thời gian tự động
    planned_hours = fields.Float(
        string=_("Planned Hours"),
        compute='_compute_planned_hours',
        store=True,
        readonly=True,
        help=_("Estimated time, calculated automatically = Deadline - Assignment Time.")
    )
    time_spent = fields.Float(
        string=_("Time Spent (Elapsed)"),
        compute='_compute_time_spent_elapsed',
        store=False,
        help=_("Time elapsed since the task was assigned. Updates on page reload.")
    )
    time_remaining = fields.Float(
        string=_("Time Remaining"),
        compute='_compute_time_remaining_realtime',
        store=False,
        help=_("Remaining time until the deadline. Updates on page reload.")
    )

    @api.depends('stage_id.fold', 'date_deadline', 'date_end')
    def _compute_deadline_status(self):
        now = datetime.now()
        for task in self:
            if task.stage_id and task.stage_id.fold:
                if not task.date_deadline or not task.date_end:
                    task.deadline_status = 'done_on_time'
                elif task.date_end.date() < task.date_deadline.date():
                    task.deadline_status = 'done_early'
                elif task.date_end.date() > task.date_deadline.date():
                    task.deadline_status = 'done_late'
                else:
                    task.deadline_status = 'done_on_time'
            else:
                if task.date_deadline and task.date_deadline < now:
                    task.deadline_status = 'late'
                else:
                    task.deadline_status = 'on_time'

    @api.depends('date_deadline', 'date_assign')
    def _compute_planned_hours(self):
        for task in self:
            if task.date_deadline and task.date_assign:
                delta = task.date_deadline - task.date_assign
                task.planned_hours = max(0.0, delta.total_seconds() / 3600.0)
            else:
                task.planned_hours = 0.0

    @api.depends('date_assign', 'date_end')
    def _compute_time_spent_elapsed(self):
        now = datetime.now()
        for task in self:
            if task.date_assign and not task.date_end:
                delta = now - task.date_assign
                task.time_spent = max(0.0, delta.total_seconds() / 3600.0)
            elif task.date_assign and task.date_end:
                delta = task.date_end - task.date_assign
                task.time_spent = max(0.0, delta.total_seconds() / 3600.0)
            else:
                task.time_spent = 0.0

    @api.depends('date_deadline', 'date_end')
    def _compute_time_remaining_realtime(self):
        now = datetime.now()
        for task in self:
            if task.date_deadline and not task.date_end:
                if task.date_deadline > now:
                    delta = task.date_deadline - now
                    task.time_remaining = delta.total_seconds() / 3600.0
                else:
                    delta = now - task.date_deadline
                    task.time_remaining = - (delta.total_seconds() / 3600.0)
            else:
                task.time_remaining = 0.0