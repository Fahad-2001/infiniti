from odoo import fields, models, _
from odoo.exceptions import UserError


class TaskStageMassUpdateWizard(models.TransientModel):
    _name = "task.stage.mass.update.wizard"
    _description = "Mass Update Stage for Tasks"

    stage_id = fields.Many2one(
        "project.task.type",
        string="Stage",
        required=True,
        help="Stage to apply to selected tasks."
    )

    def action_apply_stage(self):
        tasks = self.env["project.task"].browse(self.env.context.get("active_ids", []))
        if not tasks:
            raise UserError("No tasks selected.")

        for task in tasks:
            # Ensure the stage exists for that project
            if self.stage_id not in task.project_id.type_ids:
                raise UserError(
                    f"Stage '{self.stage_id.name}' is not available for project '{task.project_id.name}'."
                )
            task.write({"stage_id": self.stage_id.id})