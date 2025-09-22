from odoo import models, fields


class TimesheetWizard(models.TransientModel):
    _name = 'project.task.create.timesheet'
    _description = "Create Timesheet from task"

    _sql_constraints = [('time_positive', 'CHECK(time_spent > 0)', 'The timesheet\'s time must be positive' )]

    time_spent = fields.Float('Time', digits=(16, 2), default=0.25)
    description = fields.Char('Description')
    task_id = fields.Many2one(
        'project.task', "Task", required=True,
        default=lambda self: self.env.context.get('active_id', None),
        help="Task for which we are creating a sales order",
    )

    def save_timesheet(self):
        values = {
            'task_id': self.task_id.id,
            'project_id': self.task_id.project_id.id,
            'date': fields.Date.context_today(self),
            'name': self.description,
            'user_id': self.env.uid,
            'unit_amount': self.time_spent,
        }
        self.task_id.timer_start, self.task_id.timer_pause = 0.0,0.0
        self.task_id.is_timer_start = False
        self.task_id.is_timer_running = False
        self.task_id.is_timer_stop = False
        self.task_id.is_timer_pause = False
        self.task_id.timer_status = 'Timer Stopped'

        return self.env['account.analytic.line'].create(values)