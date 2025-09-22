from odoo import models, fields, api, _
import pandas as pd
import xlsxwriter
import os
import numpy as np
from datetime import datetime

class DigitalVideos(models.Model):
    _inherit = 'digital.videos'

    def import_digital_videos(self, file=None):
        print("File here -->>", file)
        if not file:
            return {'warning': 'No file provided for import'}

        try:
            # df = pd.read_excel(file)
            df = pd.read_excel(file, dtype={'Sequence': str, 'Agency Uid': str, 'Sub Tasks/Name': str, 'Sub Tasks/Task': str})
            df = df.replace({np.nan: None})

            # Initialize counters
            video_count = 0
            subtask_count = 0
            current_video = None

            for index, row in df.iterrows():
                # Process main video record (when we have agency/media/url)
                if row.get('Agency') and row.get('Media Type') and row.get('URL 1'):
                    # Prepare video data
                    video_data = {
                        'name': row.get('Name'),
                        'digital_seq': row.get('Sequence'),
                        'agency_UID': row.get('Agency Uid'),
                        'url_1': row.get('URL 1'),
                        'url_2': row.get('URL 2'),
                        'url_3': row.get('URL 3'),
                        'is_spam': bool(row.get('Spam')),
                    }

                    # Handle agency
                    if row.get('Agency'):
                        agency = self.env['res.agency'].sudo().search([('name', '=', row['Agency'])], limit=1)
                        if not agency:
                            agency = self.env['res.agency'].sudo().create({'name': row['Agency']})
                        video_data['agency_id'] = agency.id

                    # Handle media type
                    if row.get('Media Type'):
                        media_type = self.env['media.type'].sudo().search([('name', '=', row['Media Type'])], limit=1)
                        if not media_type:
                            media_type = self.env['media.type'].sudo().create({'name': row['Media Type']})
                        video_data['media_type_id'] = media_type.id

                    # Create the video record
                    print("Video Data --->>>", video_data)
                    current_video = self.env['digital.videos'].sudo().create(video_data)
                    print(index, "Digital Video Created --->>>", current_video)
                    video_count += 1

                # Process subtasks (for the current video)
                print("/////////", any(row.get(key) for key in ['Sub Tasks/Task', 'Sub Tasks/Parent Task']))
                if current_video and any(row.get(key) for key in ['Sub Tasks/Task', 'Sub Tasks/Parent Task']):
                    task_data = {
                        'task_seq': row.get('Sub Tasks/Name'),
                        'start_time': self._convert_date(row.get('Sub Tasks/Start')),
                        'end_time': self._convert_date(row.get('Sub Tasks/End')),
                    }

                    # Handle parent task
                    # if row.get('Sub Tasks/Parent Task'):
                    #     parent_task = self.env['project.task'].search([('name', '=', row['Sub Tasks/Parent Task'])], limit=1)
                    #     if parent_task:
                    #         task_data['parent_task_id'] = parent_task.id

                    # Handle main task
                    if row.get('Sub Tasks/Task'):
                        project_task = self.env['project.task'].search([('name', '=', row['Sub Tasks/Task'])], limit=1)
                        print("Found Project Task -->>", project_task)
                        if project_task:
                            task_data['task_id'] = project_task.id
                            task_data['project_id'] = project_task.project_id.id
                    print("Task Data Here --->>", task_data)

                    if task_data.get('task_id'):
                        current_video.write({
                            'sub_tasks_ids': [(0, 0, task_data)]
                        })
                        subtask_count += 1
                # if row['Sub Tasks/Task'] == 'Episode 3':
                #     raise
            print(f"Processed {video_count} videos and {subtask_count} subtasks...")

            # self._cr.commit()
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': f"Imported {video_count} videos with {subtask_count} subtasks",
                    'type': 'rainbow_man',
                }
            }

        except Exception as e:
            self._cr.rollback()
            print(f"Import failed: {str(e)}")

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

    # def import_digital_videos(self, file=None):
    #     if file:
    #         print("File ---------------", file)
    #         df = pd.read_excel(file)
    #         digital_videos = self.env['digital.videos']
    #         sub_task_url = self.env['sub.task.url']
    #         count = 0
    #         for index, row in df.iterrows():
    #             # Create a new digital video record
    #             agency = None
    #             media_type = None
    #             digital_sequence = pd.notna(row['Sequence'])
    #             if pd.notna(row['Agency']):
    #                 agency_id = self.env['res.agency'].search([('name', '=', row['Agency'])], limit=1)
    #                 agency = agency_id
    #             if pd.notna(row['Media Type']):
    #                 media_type_id = self.env['media.type'].search([('name', '=', row['Media Type'])], limit=1)
    #                 media_type = media_type_id
    #             print(agency, media_type, row['URL 1'], "..............................")
    #             if agency and media_type and row['URL 1']:
    #                 count += 1
    #                 video_data = {
    #                     'name': row['Name'] if pd.notna(row['Name']) else False,
    #                     'digital_seq': digital_sequence,
    #                     'agency_id': agency.id if agency else False,
    #                     'agency_UID': row['Agency Uid'] if pd.notna(row['Agency Uid']) else False,
    #                     'url_1': row['URL 1'],
    #                     'url_2': row['URL 2'] if pd.notna(row['URL 2']) else False,
    #                     'url_3': row['URL 3'] if pd.notna(row['URL 3']) else False,
    #                     'media_type_id': media_type.id if media_type else False,
    #                     # 'tags_ids': row['Tags'] if pd.notna(row['Tags']) else False,
    #                     'is_spam': row['Spam'] if pd.notna(row['Spam']) else False,
    #                 }
    #                 print("Video Data --------", video_data)
    #                 project_task = None
    #                 parent_task = None
    #                 if pd.notna(row['Sub Tasks/Parent Task']):
    #                     parent_task_id = self.env['project.task'].search([('name', '=', row['Sub Tasks/Parent Task'])], limit=1)
    #                     parent_task = parent_task_id
    #                 if pd.notna(row['Sub Tasks/Task']):
    #                     project_task_id = self.env['project.task'].search([('name', '=', row['Sub Tasks/Task'])], limit=1)
    #                     project_task = project_task_id
    #
    #                 task_data_list = []
    #                 if project_task:
    #                     task_data = {
    #                         'task_id': project_task.id if project_task else False,
    #                         'task_seq': row['Sub Tasks/Name'] if pd.notna(row['Sub Tasks/Name']) else False,
    #                         'start_time': row['Sub Tasks/Start'] if pd.notna(row['Sub Tasks/Start']) else False,
    #                         'end_time': row['Sub Tasks/End'] if pd.notna(row['Sub Tasks/End']) else False,
    #                         'parent_task_id': parent_task.id if parent_task else False,
    #                         'project_id': project_task.project_id.id if project_task.project_id else False,
    #                     }
    #                     task_data_list.append((0, 0, task_data))
    #
    #                 video_data['sub_tasks_ids'] = task_data_list
    #                 print("Form Data --->>>", video_data)
    #                 print("Count --->", count)
    #                 # Create the digital video record
    #                 # digital_video_record = digital_videos.create(video_data)
    #         return {'status': 'success', 'message': 'Digital videos imported successfully'}


class LeadGeneration(models.Model):
    _inherit = 'lead.generation'

    def import_lead_generation(self, file=None):
        if file:
            print("Lead File ---------------", file)
            df = pd.read_excel(file)

            lead_generation = self.env['lead.generation']
            current_lead_data = None
            subtask_data_list = []
            count = 0

            for index, row in df.iterrows():
                # Process only rows with email
                if pd.notna(row['Lead Generation Lines/Email']):
                    # If we have Social Media Network, it's a new lead
                    if pd.notna(row['Social Media Network']):
                        # First create the previous lead if we have one
                        if current_lead_data and subtask_data_list:
                            current_lead_data['lead_generation_lines'] = subtask_data_list
                            print("Current lead ---->>", current_lead_data)
                            # print("Final Sub tasks ---->>", subtask_data_list)
                            lead_generation.sudo().create(current_lead_data)
                            subtask_data_list = []

                        # Prepare new lead data (but don't create yet)
                        platform_id = self.env['project.platform'].search(
                            [('name', '=', row['Social Media Network'])], limit=1)

                        create_uid = None
                        if pd.notna(row['Created by']):
                            create_uid = self.env['res.users'].search(
                                [('name', '=', row['Created by'])], limit=1)

                        current_lead_data = {
                            'page_seq': row['Page ID'],
                            'platform_id': platform_id.id if platform_id else False,
                            'page_name': row['Page Name'],
                            'page_link': row['Page Link'],
                            'followers': row['Followers'] if pd.notna(row['Followers']) else False,
                            'create_date': self._convert_date(row['Created on']) if pd.notna(row['Created on']) else False,
                            'create_uid': create_uid.id if create_uid else False,
                        }
                        print("Preparing Lead Data ==>>>", current_lead_data)
                        count += 1

                    # Always add the current row as a subtask
                    subtask_data = {
                        'email': row['Lead Generation Lines/Email'],
                        'platform_id': current_lead_data.get('platform_id') if current_lead_data else False,
                        'name': row['Lead Generation Lines/Name'] if pd.notna(row['Lead Generation Lines/Name']) else False,
                        'website': row['Lead Generation Lines/Website'] if pd.notna(row['Lead Generation Lines/Website']) else False,
                        'phone': row['Lead Generation Lines/Phone'] if pd.notna(row['Lead Generation Lines/Phone']) else False,
                        'is_exported': True,
                        'export_datetime': self._convert_date(row['Lead Generation Lines/Export Datetime']) if pd.notna(row['Lead Generation Lines/Export Datetime']) else False,
                        'user_id': current_lead_data.get('create_uid') if current_lead_data else False,
                        'create_date': self._convert_date(row['Lead Generation Lines/Created on']) if pd.notna(row['Lead Generation Lines/Created on']) else False,
                    }
                    subtask_data_list.append((0, 0, subtask_data))
                    print("Added subtask for lead count ========", count)
                print("Sub task list ----------", subtask_data_list)
                print("Email -------", row['Lead Generation Lines/Email'])


            # Create the last lead after processing all rows
            if current_lead_data and subtask_data_list:
                current_lead_data['lead_generation_lines'] = subtask_data_list
                lead_generation.sudo().create(current_lead_data)

            print("Import completed. Total leads processed:", count)
            return {'status': 'success', 'message': f'Lead Gen imported successfully. {count} leads created.'}

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

    # def import_lead_generation(self, file=None):
    #     if file:
    #         print("Lead File ---------------", file)
    #         df = pd.read_excel(file)
    #
    #         lead_generation = self.env['lead.generation']
    #         lead_generation_lines = self.env['lead.generation.line']
    #         count = 0
    #
    #         for index, row in df.iterrows():
    #             platform_id = None
    #             create_uid = None
    #             if pd.notna(row['Social Media Network']):
    #                 platform_id = self.env['project.platform'].search([('name', '=', row['Social Media Network'])], limit=1)
    #
    #             if pd.notna(row['Created by']):
    #                 create_uid = self.env['res.users'].search([('name', '=', row['Created by'])], limit=1)
    #             page_name = row['Page Name']
    #             page_link = row['Page Link']
    #             print("THis Email ---------", row['Lead Generation Lines/Email'])
    #             # Constructing the lead generation record dictionary
    #             subtask_data_list = []
    #             # if platform_id and page_name and page_link:
    #             count += 1
    #             lead_data = {
    #                 'page_seq': row['Page ID'],
    #                 'platform_id': platform_id.id if platform_id else False,
    #                 'page_name': row['Page Name'],
    #                 'page_link': row['Page Link'],
    #                 'followers': row['Followers'] if pd.notna(row['Followers']) else False,
    #                 'create_date': row['Created on'] if pd.notna(row['Created on']) else False,
    #                 'create_uid': create_uid.id if create_uid else False,
    #             }
    #             print("Lead Data ==>>>", lead_data)
    #             if platform_id and page_name and page_link and pd.notna(row['Lead Generation Lines/Email']):
    #                 subtask_data = {
    #                     'email': row['Lead Generation Lines/Email'] if pd.notna(row['Lead Generation Lines/Email']) else False,
    #                     'platform_id': platform_id.id if platform_id else False,
    #                     'name': row['Lead Generation Lines/Name'] if pd.notna(row['Lead Generation Lines/Name']) else False,
    #                     'website': row['Lead Generation Lines/Website'] if pd.notna(row['Lead Generation Lines/Website']) else False,
    #                     'phone': row['Lead Generation Lines/Phone'] if pd.notna(row['Lead Generation Lines/Phone']) else False,
    #                     'is_exported': True,
    #                     'export_datetime': row['Lead Generation Lines/Export Datetime'] if pd.notna(row['Lead Generation Lines/Export Datetime']) else False,
    #                     'user_id': create_uid.id if create_uid else False,
    #                     'create_date': row['Lead Generation Lines/Created on'] if pd.notna(row['Lead Generation Lines/Created on']) else False,
    #                 }
    #                 subtask_data_list.append((0, 0, subtask_data))
    #                 # lead_data['lead_generation_lines'] = subtask_data_list
    #                 # print("Subtasks Ids ------------", subtask_data_list)
    #                 # lead_generation.sudo().create(lead_data)
    #                 print("Total Count ========", count)
    #             elif not (platform_id and page_name and page_link) and pd.notna(row['Lead Generation Lines/Email']):
    #                     subtask_data = {
    #                         'email': row['Lead Generation Lines/Email'] if pd.notna(row['Lead Generation Lines/Email']) else False,
    #                         'platform_id': platform_id.id if platform_id else False,
    #                         'name': row['Lead Generation Lines/Name'] if pd.notna(row['Lead Generation Lines/Name']) else False,
    #                         'website': row['Lead Generation Lines/Website'] if pd.notna(row['Lead Generation Lines/Website']) else False,
    #                         'phone': row['Lead Generation Lines/Phone'] if pd.notna(row['Lead Generation Lines/Phone']) else False,
    #                         'is_exported': True,
    #                         'export_datetime': row['Lead Generation Lines/Export Datetime'] if pd.notna(row['Lead Generation Lines/Export Datetime']) else False,
    #                         'user_id': create_uid.id if create_uid else False,
    #                         'create_date': row['Lead Generation Lines/Created on'] if pd.notna(row['Lead Generation Lines/Created on']) else False,
    #                     }
    #                     subtask_data_list.append((0, 0, subtask_data))
    #             print("Subtasks Ids ------------", subtask_data_list)
    #         return {'status': 'success', 'message': 'Lead Gen imported successfully'}
