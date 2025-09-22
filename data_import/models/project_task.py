from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import pandas as pd
import numpy as np
import base64
import io, logging, traceback
import json
import os
import openpyxl

_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def import_projects_with_users(self, file=None):
        if not file:
            return {'warning': 'No file provided for import'}

        try:
            # Read the Excel file
            df = pd.read_excel(file)

            # Initialize counters
            project_count = 0
            user_count = 0

            current_project = None
            project_vals = {}

            for index, row in df.iterrows():
                # Check if this is a new project (Sequence column has a value)
                if pd.notna(row.get('Sequence')):
                    # If we have a current project being processed, create it before starting new one
                    if current_project:
                        # Create the project
                        print(f"Created project -----???: {project_vals}")
                        project = self.env['project.project'].sudo().create(project_vals)
                        print(f"project -----???: {project.name}")
                        project_count += 1

                    # Start a new project
                    project_name = row.get('Name')
                    customer = row.get('Customer')
                    start_date = row.get('Start Date')
                    expiration_date = row.get('Expiration Date')
                    project_manager = row.get('Project Manager')
                    # last_update_status = 'on_track' if row.get('Last Update Status') in ['On Track'] else 'to_define'
                    last_update_status = 'on_track'
                    description = row.get('Description')
                    active = row.get('Active')
                    # visibility = row.get('Visibility')
                    visibility = 'portal'

                    # Get project manager user
                    manager_user = self.env['res.users'].sudo().search([('name', '=', project_manager)], limit=1) if project_manager else False

                    # Prepare project values
                    project_vals = {
                        'name': project_name,
                        'partner_id': self.env['res.partner'].sudo().search([('name', '=', customer)], limit=1).id if customer else False,
                        'date_start': start_date if pd.notna(start_date) else False,
                        'date': expiration_date if pd.notna(expiration_date) else False,
                        'user_id': manager_user.id if manager_user else False,
                        'last_update_status': last_update_status,
                        'description': description,
                        'active': bool(active) if pd.notna(active) else True,
                        'privacy_visibility': visibility,
                        'user_ids': []  # Initialize empty user list
                    }

                    current_project = project_name

                    # Add first user if exists
                    user_name = row.get('Users')
                    if pd.notna(user_name):
                        user = self.env['res.users'].sudo().search([('name', '=', user_name)], limit=1)
                        if user:
                            project_vals['user_ids'].append((4, user.id))
                            user_count += 1

                else:
                    # This is a continuation line with additional users for the current project
                    user_name = row.get('Users')
                    if pd.notna(user_name) and current_project:
                        user = self.env['res.users'].sudo().search([('name', '=', user_name)], limit=1)
                        if user and user.id not in [uid for (cmd, uid) in project_vals['user_ids'] if cmd == 4]:
                            project_vals['user_ids'].append((4, user.id))
                            user_count += 1

            # Create the last project after loop ends (if there is one)
            if current_project and project_vals:
                print(f"Created project ---->>>>: {current_project}, {project_vals}")
                project = self.env['project.project'].sudo().create(project_vals)
                print(f"project -----///: {project.name}")
                project_count += 1

        except Exception as e:
            return {
                'error': f"Error during import: {str(e)}"
            }

    def import_projects_with_users_w_attachment(self, attachment_id):
        attachment = self.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            raise UserError("Attachment not found.")

        try:
            _logger.info(f"Attchment Name ----->>", attachment.name)
            excel_data = base64.b64decode(attachment.datas)
            excel_file = io.BytesIO(excel_data)
            # Read the Excel file
            df = pd.read_excel(excel_file)

            # Initialize counters
            project_count = 0
            user_count = 0

            current_project = None
            project_vals = {}

            for index, row in df.iterrows():
                # Check if this is a new project (Sequence column has a value)
                if pd.notna(row.get('Sequence')):
                    # If we have a current project being processed, create it before starting new one
                    if current_project:
                        # Create the project
                        print(f"Created project -----???: {project_vals}")
                        project = self.env['project.project'].sudo().create(project_vals)
                        print(f"project -----???: {project.name}")
                        project_count += 1

                    # Start a new project
                    project_name = row.get('Name')
                    customer = row.get('Customer')
                    start_date = row.get('Start Date')
                    expiration_date = row.get('Expiration Date')
                    project_manager = row.get('Project Manager')
                    # last_update_status = 'on_track' if row.get('Last Update Status') in ['On Track'] else 'to_define'
                    last_update_status = 'on_track'
                    description = row.get('Description')
                    active = row.get('Active')
                    # visibility = row.get('Visibility')
                    visibility = 'portal'

                    # Get project manager user
                    manager_user = self.env['res.users'].sudo().search([('name', '=', project_manager)], limit=1) if project_manager else False

                    # Prepare project values
                    project_vals = {
                        'name': project_name,
                        'partner_id': self.env['res.partner'].sudo().search([('name', '=', customer)], limit=1).id if customer else False,
                        'date_start': start_date if pd.notna(start_date) else False,
                        'date': expiration_date if pd.notna(expiration_date) else False,
                        'user_id': manager_user.id if manager_user else False,
                        'last_update_status': last_update_status,
                        'description': description,
                        'active': bool(active) if pd.notna(active) else True,
                        'privacy_visibility': visibility,
                        'user_ids': []  # Initialize empty user list
                    }

                    current_project = project_name

                    # Add first user if exists
                    user_name = row.get('Users')
                    if pd.notna(user_name):
                        user = self.env['res.users'].sudo().search([('name', '=', user_name)], limit=1)
                        if user:
                            project_vals['user_ids'].append((4, user.id))
                            user_count += 1

                else:
                    # This is a continuation line with additional users for the current project
                    user_name = row.get('Users')
                    if pd.notna(user_name) and current_project:
                        user = self.env['res.users'].sudo().search([('name', '=', user_name)], limit=1)
                        if user and user.id not in [uid for (cmd, uid) in project_vals['user_ids'] if cmd == 4]:
                            project_vals['user_ids'].append((4, user.id))
                            user_count += 1

            # Create the last project after loop ends (if there is one)
            if current_project and project_vals:
                print(f"Created project ---->>>>: {current_project}, {project_vals}")
                project = self.env['project.project'].sudo().create(project_vals)
                print(f"project -----///: {project.name}")
                project_count += 1

        except Exception as e:
            return {
                'error': f"Error during import: {str(e)}"
            }

    def update_existing_project_stages(self, file=None):
        if not file:
            return {'warning': 'No file provided for import'}

        try:
            # Read the Excel file
            df = pd.read_excel(file)


            stage = False
            for index, row in df.iterrows():
                # Check if this is a new project (Sequence column has a value)
                if pd.notna(row.get('Sequence')):
                    # If we have a current project being processed, create it before starting new one
                    project = self.env['project.project'].sudo().search([('name', '=', row.get('Projects'))], limit=1)
                    if not project:
                        continue

                    # Find the existing stage by name only
                    existing_stage = self.env['project.task.type'].sudo().search([('name', '=', row.get('Name'))
                    ], limit=1)

                    print("Project ---- Stage --->>", project.name, existing_stage.name)

                    if existing_stage:
                        stage = existing_stage
                        # Link project to stage if not already linked
                        if project.id not in existing_stage.project_ids.ids:
                            existing_stage.write({
                                'project_ids': [(4, project.id)]
                            })
                            print("If Project Linked --->>>", project.name)
                else:
                    if row.get('Projects'):
                        project = self.env['project.project'].sudo().search([('name', '=', row.get('Projects'))], limit=1)
                        print("Finding project in else??", project.name)
                        print("Stage here???", stage)
                        if not project:
                            continue

                        if stage and project.id not in stage.project_ids.ids:
                            stage.write({
                                'project_ids': [(4, project.id)]
                            })
                            print("Else Project Linked --->>>", project.name)

        except Exception as e:
            return {
                'error': f"Error during import: {str(e)}"
            }

    def update_existing_project_stages_with_attachments(self, attachment_id, active=True):
        attachment = self.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            raise UserError("Attachment not found.")

        try:
            excel_data = base64.b64decode(attachment.datas)
            excel_file = io.BytesIO(excel_data)
            # Read the Excel file
            df = pd.read_excel(excel_file)


            stage = False
            for index, row in df.iterrows():
                # Check if this is a new project (Sequence column has a value)
                if pd.notna(row.get('Sequence')):
                    # If we have a current project being processed, create it before starting new one
                    project = self.env['project.project'].sudo().search([('name', '=', row.get('Projects')), ('active', '=', active)], limit=1)
                    if not project:
                        continue

                    # Find the existing stage by name only
                    existing_stage = self.env['project.task.type'].sudo().search([('name', '=', row.get('Name'))
                    ], limit=1)

                    print("Project ---- Stage --->>", project.name, existing_stage.name)

                    if existing_stage:
                        stage = existing_stage
                        # Link project to stage if not already linked
                        if project.id not in existing_stage.project_ids.ids:
                            existing_stage.write({
                                'project_ids': [(4, project.id)]
                            })
                            print("If Project Linked --->>>", project.name)
                else:
                    if row.get('Projects'):
                        project = self.env['project.project'].sudo().search([('name', '=', row.get('Projects'))], limit=1)
                        print("Finding project in else??", project.name)
                        print("Stage here???", stage)
                        if not project:
                            continue

                        if stage and project.id not in stage.project_ids.ids:
                            stage.write({
                                'project_ids': [(4, project.id)]
                            })
                            print("Else Project Linked --->>>", project.name)

        except Exception as e:
            return {
                'error': f"Error during import: {str(e)}"
            }



class ProjectTask(models.Model):
    _inherit = 'project.task'

    def import_project_parent_task(self, file=None):
        if file:
            df = pd.read_excel(file)
            count = 0
            for index, row in df.iterrows():
                name = row.get('Name')
                stage_name = row.get('Stage')
                starred = row.get('Starred')
                task_name = row.get('Title')
                project_name = row.get('Project')
                assignees = row.get('Assignees')
                parent_task = row.get('Parent Task')
                tags = row.get('Tags')
                task_status = row.get('Task Status')
                task_type_name = row.get('Task Type/Name')
                project_platform_name = row.get('Project Platform/Name')
                deadline = row.get('Deadline')
                post_description = row.get('Post Description')
                task_temp_name = row.get('Task Temp/Name')
                description = row.get('Description')
                assigning_date = row.get('Assigning Date')
                last_stage_update = row.get('Last Stage Update')
                working_hours_to_close = row.get('Working Hours to Close')
                working_days_to_close = row.get('Working Days to Close')
                if starred in ['Important', 'IMPORTANT']:
                    priority = "1"
                else:
                    priority = "0"
                stage = self.env['project.task.type'].sudo().search([('name', '=', stage_name)], limit=1)
                if not stage:
                    stage = self.env['project.task.type'].create({'name': stage_name})
                users = self.env['res.users'].sudo().search([('name', '=', assignees)], limit=1)
                parent_task_id = self.env['project.task'].sudo().search([('name', '=', parent_task)], limit=1)
                if parent_task_id:
                    count += 1
                    vals = {
                        'name': task_name,
                        'priority': priority,
                        'parent_id': parent_task_id.id,
                        'project_id': parent_task_id.project_id.id,
                        'task_status': parent_task_id.task_status,
                        'task_type_id': parent_task_id.task_type_id.id,
                        'project_platform_id': parent_task_id.project_platform_id.id,
                        'stage_id': stage.id,
                        'post_description': post_description,
                        'description': description,
                        'date_assign': assigning_date,
                        'date_last_stage_update': last_stage_update,
                        'working_hours_close': float(working_hours_to_close),
                        'working_days_close': float(working_days_to_close),
                        'task_temp_id': parent_task_id.task_temp_id.id if parent_task_id.task_temp_id else False,
                        'user_ids': [(6, 0, users.ids)] if users else False,
                    }
                    print("Count of actual tasks", count)
                    print("\nFinal Sub Task Values =============", vals)
                    parent_task = self.env['project.task'].sudo().create(vals)
                    print("\nSub Task Created =============>>", parent_task)

    # Working Method to Use
    # def import_project_tasks(self, file=None):
    #     if not file:
    #         raise UserError('No file provided for import')
    #
    #     # Read the Excel file
    #     try:
    #         df = pd.read_excel(file)
    #         df = df.replace({np.nan: None})
    #     except Exception as e:
    #         raise UserError(f"Error reading Excel file: {str(e)}")
    #
    #     # Initialize counters
    #     task_count = 0
    #     subtask_count = 0
    #     current_main_task = None
    #
    #     for index, row in df.iterrows():
    #         # Check if this is a main task (has a value in 'Name' column)
    #         if row.get('Name'):
    #             # Create main task
    #             task_vals = self._prepare_main_task_vals(row)
    #             print("Main task values ----", task_vals)
    #             current_main_task = self.env['project.task'].sudo().create(task_vals)
    #             task_count += 1
    #             # raise
    #             # self._cr.commit()  # Commit after each main task creation
    #
    #         # Add subtask to current main task if exists
    #         elif current_main_task and row.get('Sub-tasks/Name'):
    #             subtask_vals = self._prepare_subtask_vals(row, current_main_task)
    #             print("Subtask values ----", subtask_vals)
    #             subtask = self.env['project.task'].sudo().create(subtask_vals)
    #             print(current_main_task, "================", subtask)
    #             subtask_count += 1
    #             # raise
    #
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': f"Successfully imported {task_count} main tasks and {subtask_count} subtasks",
    #             'type': 'rainbow_man',
    #         }
    #     }

    def import_project_tasks(self, attachment_id, active):
        attachment = self.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            raise UserError("Attachment not found.")

        try:
            _logger.info(f"ARCHIVED Attachment Name ----->> {attachment.name}")
            _logger.info("Attachment Name ----->>", attachment.name)
            excel_data = base64.b64decode(attachment.datas)
            excel_file = io.BytesIO(excel_data)
            # Read the Excel file
            df = pd.read_excel(excel_file)
            df = df.replace({np.nan: None})
        except Exception as e:
            raise UserError(f"Error reading Excel file: {str(e)}")

        # Initialize counters
        task_count = 0
        subtask_count = 0
        current_main_task = None
        try:
            for index, row in df.iterrows():
                # Check if this is a main task (has a value in 'Name' column)
                if row.get('Name'):
                    # Create main task
                    task_vals = self._prepare_main_task_vals(row)
                    print("Main task values ----", task_vals)
                    if active == 'no':
                        task_vals['active'] = False
                    current_main_task = self.env['project.task'].sudo().create(task_vals)
                    print("Main Task archived --->>>???", current_main_task.active)
                    task_count += 1
                    # raise
                    # self._cr.commit()  # Commit after each main task creation

                # Add subtask to current main task if exists
                elif current_main_task and row.get('Sub-tasks/Name'):
                    subtask_vals = self._prepare_subtask_vals(row, current_main_task)
                    print("Subtask values ----", subtask_vals)
                    subtask = self.env['project.task'].sudo().create(subtask_vals)
                    print(current_main_task, "================", subtask)
                    subtask_count += 1
                    # raise
            _logger.info(f"ARCHIVED: Successfully imported {task_count} main tasks and {subtask_count} subtasks")
            _logger.info("ARCHIVED: Successfully imported '%r' main tasks and '%r' subtasks", task_count, subtask_count)
            self.env.cr.commit()
            _logger.info("ARCHIVED: Successfully committed to DB")
            # return {
            #     'effect': {
            #         'fadeout': 'slow',
            #         'message': f"Successfully imported {task_count} main tasks and {subtask_count} subtasks",
            #         'type': 'rainbow_man',
            #     }
            # }
        except Exception as e:
            _logger.error(f"ARCHIVED Failed: Imported Failed Due to Error {e}")
            _logger.error("ARCHIVED Failed: Imported Failed Due to Error: ", e)
            _logger.error("Import failed at row %s: %s\n%s", index + 2, str(e), traceback.format_exc())

    def _prepare_main_task_vals(self, row):
        """Prepare values dictionary for main task creation"""
        # Get or create stage
        task_status = row.get('Task Status')
        task_temp_name = row.get('Task Temp/Name')

        stage = self.env['project.task.type'].sudo().search([('name', '=', row.get('Stage'))], limit=1)
        if not stage and row.get('Stage'):
            stage = self.env['project.task.type'].sudo().create({'name': row.get('Stage')})
            print("New Stage Created -->>", row.get('Stage'))

        # Get or create project
        project = self.env['project.project'].sudo().search([('name', '=', row.get('Project'))], limit=1)
        if not project and row.get('Project'):
            project = self.env['project.project'].create({
                'name': row.get('Project'),
                'type_ids': [(6, 0, stage.ids)] if stage else False,
            })
            print("New Project Created -->>", row.get('Project'))

        # Get task type
        task_type_name = row.get('Task Type/Name')
        task_type_id = False
        if task_type_name is not None:
            task_type_id = self.env['task.type'].sudo().search([('name', '=', task_type_name)], limit=1)
            if not task_type_id:
                task_type_id = self.env['task.type'].sudo().create({'name': task_type_name})
                print("New Task type Created -->>", task_type_name)

        # Get task template
        task_temp_id = False
        if task_temp_name is not None:
            task_temp_id = self.env['task.template'].sudo().search([('name', '=', task_temp_name)], limit=1)
            if not task_temp_id:
                task_temp_id = self.env['task.template'].sudo().create({'name': task_temp_name})
                print("New Task Temp Created -->>", task_temp_name)

        # Get project platform
        project_platform_id = False
        project_platform_name = row.get('Project Platform/Name')
        if project_platform_name is not None:
            project_platform_id = self.env['project.platform'].sudo().search([('name', '=', project_platform_name)], limit=1)
            if not project_platform_id:
                project_platform_id = self.env['project.platform'].sudo().create({'name': project_platform_name})
                print("New Project Platform Created -->>", project_platform_name)

        # Get assignee user
        user_ids = []
        if row.get('Assignees'):
            user = self.env['res.users'].sudo().search([('name', '=', row.get('Assignees'))], limit=1)
            if not user:
                # Try to find by email
                user = self.env['res.users'].sudo().search([('email', '=', row.get('Assignees'))], limit=1)
            if user:
                user_ids.append(user.id)

        # Set priority based on starred status
        priority = "1" if row.get('Starred') == 'Important' else "0"

        # Prepare task values
        return {
            'name': row.get('Title') or row.get('Name'),
            'priority': priority,
            'stage_id': stage.id if stage else False,
            'project_id': project.id if project else False,
            'user_ids': [(6, 0, user_ids)] if user_ids else False,
            'date_deadline': self._convert_date(row.get('Deadline')),
            'task_status': task_status,
            'task_temp_id': task_temp_id.id if task_temp_id else False,
            'post_description': row.get('Post Description') or '',
            'description': row.get('Description') or '',
            'date_assign': self._convert_date(row.get('Assigning Date')),
            'date_last_stage_update': self._convert_date(row.get('Last Stage Update')),
            'working_hours_close': float(row.get('Working Hours to Close', 0)) or 0,
            'working_days_close': float(row.get('Working Days to Close', 0)) or 0,
            'task_type_id': task_type_id.id if task_type_id else False,
            'project_platform_id': project_platform_id.id if project_platform_id else False,
        }

    def _prepare_subtask_vals(self, row, parent_task):
        """Prepare values dictionary for subtask creation"""
        # Get assignee user for subtask
        user_ids = []
        if row.get('Sub-tasks/Assignees/Login'):
            user = self.env['res.users'].sudo().search([('email', '=', row.get('Sub-tasks/Assignees/Login'))], limit=1)
            if not user and row.get('Sub-tasks/Assignees/Name'):
                user = self.env['res.users'].sudo().search([('name', '=', row.get('Sub-tasks/Assignees/Name'))], limit=1)
            if user:
                user_ids.append(user.id)

        # Get stage for subtask
        stage = self.env['project.task.type'].sudo().search([('name', '=', row.get('Sub-tasks/Stage/Name'))], limit=1)
        if not stage and row.get('Sub-tasks/Stage/Name'):
            stage = self.env['project.task.type'].sudo().create({'name': row.get('Sub-tasks/Stage/Name')})

        return {
            'name': row.get('Sub-tasks/Title'),
            'parent_id': parent_task.id,
            'project_id': parent_task.project_id.id,
            'user_ids': [(6, 0, user_ids)] if user_ids else False,
            'stage_id': stage.id if stage else False,
            'date_deadline': self._convert_date(row.get('Sub-tasks/Deadline')),
        }

    def _convert_date(self, date_value):
        """Convert date from Excel to Odoo format"""
        if not date_value or pd.isna(date_value):
            return False
        if isinstance(date_value, pd.Timestamp):
            return date_value.strftime('%Y-%m-%d')
        try:
            return datetime.strptime(str(date_value), '%Y-%m-%d').strftime('%Y-%m-%d')
        except:
            return False

    # def archive_projects_problems(self):
    #     active_projects = self.env['project.project'].sudo().search([('active', '=', True)])
    #
    #     for active_proj in active_projects:
    #         # Search for an inactive (archived) project with same name
    #         archived_proj = self.env['project.project'].sudo().search([
    #             ('name', '=', active_proj.name),
    #             ('active', '=', False)
    #         ], limit=1)
    #         if archived_proj:
    #             print(active_proj.name, "Archived Projects ---->>", archived_proj.name)
    #             tasks_to_update = self.env['project.task'].sudo().search([
    #                 ('project_id', '=', active_proj.id),
    #                 ('active', '=', False)
    #             ])
    #             tasks_to_update.sudo().update({'project_id': archived_proj.id})
    #             active_proj.name = 'To Remove this Proj as it exist alr in archived'
    #             print("Tasks To Update ----->>>", tasks_to_update.ids)
    #             self.env.cr.commit()

class IrAttachments(models.Model):
    _inherit = 'ir.attachment'

    def update_ir_attachment_records(self, attachment_id):
        attachment = self.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            raise UserError("Attachment not found.")

        try:
            # Read and decode the CSV file
            csv_data = base64.b64decode(attachment.datas)
            csv_file = io.StringIO(csv_data.decode('utf-8'))
            df = pd.read_csv(csv_file)

            updated_count = 0
            skipped = 0

            for index, row in df.iterrows():
                print("Rowwwwwwwww", row)
                # raise
                att_id = row['ID']
                if not att_id:
                    skipped += 1
                    continue

                existing_attachment = self.env['ir.attachment'].browse(int(att_id))
                print("Found Existing Attachment -->>>", existing_attachment)
                vals = {}
                if existing_attachment and 'File Content (base64)' in row and pd.notna(row['File Content (base64)']):
                    vals['datas'] = row['File Content (base64)']

                # Update record
                if vals:
                    existing_attachment.sudo().write(vals)
                    updated_count += 1

            return_vals = {
                'status': 'success',
                'updated': updated_count,
                'skipped': skipped
            }
            print("Final Result ---->>>", return_vals)
            # raise

        except Exception as e:
            raise UserError(f"Error while updating attachments: {str(e)}")

    # def export_attachment_data_in_json(self):
    #     attachments = self.env['ir.attachment'].search([('res_model', '=', 'account.move')])
    #     print("Length --->>>", len(attachments))
    #     export_data = []
    #     for attachment in attachments:
    #         encoded_datas = attachment.datas
    #         if isinstance(encoded_datas, bytes):
    #             encoded_datas = base64.b64encode(encoded_datas).decode('utf-8')
    #         if attachment.datas:
    #             print("yoooooooooooo")
    #             export_data.append({
    #                 'id': attachment.id,
    #                 'name': attachment.name,
    #                 'datas': encoded_datas,  # base64-encoded string
    #             })
    #
    #     # Define file path
    #     folder_path = r'C:\Users\fahad.rizwan\Downloads\Infini_import_exports_xlsx'
    #     os.makedirs(folder_path, exist_ok=True)
    #     file_path = os.path.join(folder_path, 'attachments.json')
    #
    #     # Write to JSON file
    #     with open(file_path, 'w', encoding='utf-8') as json_file:
    #         json.dump(export_data, json_file, indent=4)
    #
    #     print(f"✅ Exported {len(export_data)} attachments to {file_path}")

    # def export_attachment_data_in_json(self):
    #     MAX_SIZE_MB = 100
    #     MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
    #
    #     attachments = self.env['ir.attachment'].search([('res_model', '=', 'account.move')])
    #
    #     small_attachments = []
    #     large_attachments_count = 0
    #
    #     base_folder = r'C:\Users\fahad.rizwan\Downloads\Infini_import_exports_xlsx'
    #     os.makedirs(base_folder, exist_ok=True)
    #
    #     for attachment in attachments:
    #         if not attachment.datas:
    #             continue
    #
    #         try:
    #             # Ensure attachment.datas is a string
    #             base64_str = (
    #                 attachment.datas.decode('utf-8') if isinstance(attachment.datas, bytes) else str(attachment.datas)
    #             )
    #
    #             # Decode to bytes just to check actual size
    #             decoded_bytes = base64.b64decode(base64_str)
    #         except Exception as e:
    #             print(f"⚠️ Skipping attachment ID {attachment.id}: decoding error: {e}")
    #             continue
    #
    #         attachment_record = {
    #             'id': attachment.id,
    #             'name': attachment.name,
    #             'datas': base64_str,  # Always a string
    #         }
    #
    #         if len(decoded_bytes) > MAX_SIZE_BYTES:
    #             # Write large file separately
    #             file_path = os.path.join(base_folder, f'attachment_{attachment.id}.json')
    #             with open(file_path, 'w', encoding='utf-8') as f:
    #                 json.dump(attachment_record, f, indent=4)
    #             large_attachments_count += 1
    #             print(f"📦 Large file saved separately: {file_path}")
    #         else:
    #             small_attachments.append(attachment_record)
    #
    #     # Save all small attachments
    #     if small_attachments:
    #         small_file_path = os.path.join(base_folder, 'attachments_small.json')
    #         with open(small_file_path, 'w', encoding='utf-8') as f:
    #             json.dump(small_attachments, f, indent=4)
    #         print(f"✅ Small attachments written: {len(small_attachments)}")
    #
    #     print(f"📁 Total large attachments saved individually: {large_attachments_count}")

    def export_attachment_data_in_json(self):
        MAX_SIZE_MB = 100
        MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

        SPLIT_FILE_SIZE_MB = 200
        SPLIT_FILE_SIZE_BYTES = SPLIT_FILE_SIZE_MB * 1024 * 1024

        attachments = self.env['ir.attachment'].search([('res_model', '=', 'account.move')])

        base_folder = r'C:\Users\fahad.rizwan\Downloads\Infini_import_exports_xlsx'
        os.makedirs(base_folder, exist_ok=True)

        current_chunk = []
        current_size = 0
        part_number = 1
        large_attachments_count = 0

        def write_chunk(chunk, part):
            file_path = os.path.join(base_folder, f'attachments_part_{part}.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, indent=4)
            print(f"✅ Wrote part {part} with {len(chunk)} attachments")

        for attachment in attachments:
            if not attachment.datas:
                continue

            try:
                base64_str = (
                    attachment.datas.decode('utf-8') if isinstance(attachment.datas, bytes) else str(attachment.datas)
                )
                decoded_bytes = base64.b64decode(base64_str)
            except Exception as e:
                print(f"⚠️ Skipping attachment ID {attachment.id}: decoding error: {e}")
                continue

            attachment_record = {
                'id': attachment.id,
                'name': attachment.name,
                'datas': base64_str,
            }

            if len(decoded_bytes) > MAX_SIZE_BYTES:
                # Save large attachment separately
                large_path = os.path.join(base_folder, f'attachment_{attachment.id}.json')
                with open(large_path, 'w', encoding='utf-8') as f:
                    json.dump(attachment_record, f, indent=4)
                large_attachments_count += 1
                print(f"📦 Large file saved separately: {large_path}")
                continue

            # Estimate size of the JSON string
            estimated_size = len(json.dumps(attachment_record))

            # If adding this record would exceed 200MB, write current chunk and reset
            if current_size + estimated_size > SPLIT_FILE_SIZE_BYTES:
                write_chunk(current_chunk, part_number)
                part_number += 1
                current_chunk = []
                current_size = 0

            current_chunk.append(attachment_record)
            current_size += estimated_size

        # Write final chunk if any
        if current_chunk:
            write_chunk(current_chunk, part_number)

        print(f"📁 Total large attachments saved individually: {large_attachments_count}")

    def update_ir_attachment_records_from_json(self, attachment_id):
        attachment = self.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            raise UserError("Attachment not found.")

        try:
            # Read and decode the JSON file
            json_data = base64.b64decode(attachment.datas)
            json_file = io.StringIO(json_data.decode('utf-8'))
            data = json.load(json_file)

            if not isinstance(data, list):
                raise UserError("Invalid JSON format. Expected a list of attachment records.")

            updated_count = 0
            skipped = 0

            for record in data:
                att_id = record.get('id')
                base64_datas = record.get('datas')

                if not att_id or not base64_datas:
                    skipped += 1
                    continue

                existing_attachment = self.env['ir.attachment'].browse(int(att_id))

                if not existing_attachment.exists():
                    skipped += 1
                    continue

                vals = {
                    'datas': base64_datas,
                }
                existing_attachment.sudo().write(vals)
                print("Attachment Updated ======>>", existing_attachment)
                updated_count += 1

            return {
                'status': 'success',
                'updated': updated_count,
                'skipped': skipped
            }

        except Exception as e:
            raise UserError(f"Error while updating attachments from JSON: {str(e)}")