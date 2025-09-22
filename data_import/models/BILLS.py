from odoo import models, fields, api, _
from datetime import datetime, date
import pandas as pd


# import odoorpc
class AccountMove(models.Model):
    _inherit = 'account.move'

    def import_invoices(self, file=None):
        if file:
            Order = self.env['account.move']
            OrderLine = self.env['account.move.line']

            df = pd.read_excel(file)
            i = 0
            for index, row in df.iterrows():
                i += i
                print(i, '9999999999999999999999999999999999999')
                if pd.notna(row['Status']):
                    confirm_date_str = row['Accounting Date']
                    due_date_str = row['Due Date']
                    vendor = self.env['res.partner'].search([('name', '=', row['Partner'])], limit=1)
                    client = self.env['res.partner'].search([('name', '=', row['Client'])], limit=1)
                    project = self.env['project.project'].search([('name', '=', row['Project'])], limit=1)
                    # journal = self.env['account.journal'].search([('name', '=', row['Journal'])])
                    if row['Status']:
                        if row['Status'] == 'Draft':
                            state = 'draft'
                        elif row['Status'] == 'Open':
                            state = 'posted'
                        elif row['Status'] == 'Paid':
                            state = 'posted'
                        elif row['Status'] == 'Cancelled':
                            state = 'cancel'
                        else:
                            state = 'draft'
                        order_data = {
                            'name': row['Number'],
                            'partner_id': vendor.id if vendor else self.env['res.partner'].create({'name': row['Partner']}).id,
                            'invoice_date': confirm_date_str,
                            'date': confirm_date_str,
                            'invoice_date_due': due_date_str,
                            'state': 'cancel',
                            'journal_id': 2,
                            # 'ref': row['Reference'] if row['Reference'] else '',
                            # 'x_issue': row['Issue date'] if row['Issue date'] else '',
                            'x_project': project.id,
                            'x_client': client.id,
                            'move_type': 'in_invoice'
                        }
                        # if confirm_date_str:
                        #     order_data['invoice_date'] = confirm_date_str
                        #     order_data['date'] = confirm_date_str
                        # if due_date_str:
                        #     order_data['invoice_date_due'] = due_date_str
                        # Create the new POS order
                        order_id = Order.create(order_data)
                        # order_id.write({'state': state})
                        print(f'Created Invoice ID: {order_id}')

                    # If you have order lines, create them separately and link to the created order
                if not pd.isna(row['Product']) and order_id:
                    product = self.env['product.product'].search([('name', '=', row['Product'])], limit=1)
                    order_line_data = {
                        'move_id': order_id.id,
                        'product_id': product.id if product else 1499,
                        'name': row['Description'],
                        # 'name': row['Product'],
                        'quantity': row['Quantity'],
                        'price_unit': row['Unit Price'],
                        # 'discount': row['Discount'],
                    }
                    OrderLine.create(order_line_data)
                    print(f'Created Invoice Line for Order ID: {order_id}')

    def update_invoices(self, file=None):
        df = pd.read_excel(file)
        for index, row in df.iterrows():
            if pd.notna(row['Number']):
                inv = self.env['account.move'].search([('name', '=', row['Number'])], limit=1)
                if row['Status'] == 'Draft':
                    state = 'draft'
                elif row['Status'] == 'Open':
                    state = 'posted'
                elif row['Status'] == 'Paid':
                    state = 'posted'
                elif row['Status'] == 'Cancelled':
                    state = 'cancel'
                else:
                    state = 'draft'
                inv.write({'state': state})
                print(row['Number'])


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def create_payments_from_excel(self, file=None):
        payment = self.env['account.payment']
        df = pd.read_excel(file)
        i = 0
        for index, row in df.iterrows():
            i += 1
            print(i, '9999999999999999999999999999999999999')
            if pd.notna(row['Status']):
                project = None
                bank_date = None
                ChequeNumber = None
                Memo = None
                if pd.notna(row['Project']):
                    project = row['Project']
                if pd.notna(row['Bank Date']):
                    bank_date = row['Bank Date']
                if pd.notna(row['Cheque Number']):
                    ChequeNumber = row['Cheque Number']
                if pd.notna(row['Memo']):
                    Memo = row['Memo']

                partner = self.env['res.partner'].search([('name', '=', row['Partner'])], limit=1)
                if not partner:
                    # If partner not found, create a new one with the provided name
                    partner = self.env['res.partner'].create({
                        'name': row['Partner']
                    })
                journal_id = self.env['account.journal'].search([('name', '=', row['Journal'])], limit=1)
                project_id = self.env['project.project'].search([('name', '=', project)], limit=1)
                payment_method = journal_id.inbound_payment_method_line_ids[0].id
                if not journal_id:
                    raise ValueError(_("Journal '%s' not found.") % row['Journal'])
                payment_vals = {
                    'name': row['Display Name'],
                    'partner_id': partner.id,
                    'amount': row['Payment Amount'],
                    'date': row['Payment Date'],
                    'journal_id': journal_id.id,
                    # Assuming bank journal
                    'payment_type': 'outbound',
                    # 'partner_type': 'customer',
                    'payment_method_line_id': payment_method,
                    'x_project': project_id.id,
                    'x_date': bank_date,
                    'cheque_reference': ChequeNumber,
                    'ref': Memo,
                }
                new_payment = payment.create(payment_vals)
                if row['Status'] == 'Draft':
                    state = 'draft'
                elif row['Status'] == 'Posted':
                    state = 'posted'
                elif row['Status'] == 'Cancelled':
                    state = 'cancel'
                else:
                    state = 'draft'
                new_payment.write({'state': state})
                print(new_payment, '000000000000000000000000000000000000000000')

