from odoo import models, fields, api, _
import pandas as pd


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    def import_project_task_stage(self, file=None):
        if file:
            print("File ---------------", file)
            # raise
            # Load the Excel file
            df = pd.read_excel(file)

            project_task_type = self.env['project.task.type']
            res_users = self.env['res.users']
            count = 0
            for index, row in df.iterrows():
                # Mapping fields from the Excel to Odoo fields
                sequence = row['Sequence']
                name = row['Name']
                fold = row['Folded in Kanban']
                # Handle cases where Stage Owner might be empty
                owner_name = row['Stage Owner'] if pd.notna(row['Stage Owner']) else False
                print("==========", sequence, name, owner_name, fold)

                # If Stage Owner is provided, attempt to find the user
                user_id = False
                if owner_name:
                    user = res_users.sudo().search([('name', '=', owner_name)], limit=1)
                    if user:
                        user_id = user.id

                # Creating the record in project.task.type model
                count += 1
                task_stage_type_vals = {
                    'sequence': sequence,
                    'name': name,
                    'fold': False if fold in ['False', 'FALSE'] else True,
                    'user_id': user_id
                }
                print("Task Stage Created --->>>>", task_stage_type_vals)
                # project_task_type.sudo().create(task_stage_type_vals)
            print("Total Count for stages --->>>", count)
