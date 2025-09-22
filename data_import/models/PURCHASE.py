# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import pandas as pd


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def import_purchase_order(self, file=None):
        if file:
            Order = self.env['purchase.order']
            OrderLine = self.env['purchase.order.line']

            df = pd.read_excel(file)

            # Ensure all date columns are in datetime format and replace NaT with empty strings
            date_columns = ['Order Date', 'Set up Date', 'Completion Date', 'Event Date', 'Clearance Date']
            for col in date_columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').apply(
                    lambda x: '' if pd.isna(x) else x.strftime('%Y-%m-%d'))

            df = pd.read_excel(file)
            for index, row in df.iterrows():
                if pd.notna(row['Order Reference']):
                    x_podate = row['Order Date']
                    x_set = row['Set up Date']
                    x_comp = row['Completion Date']
                    x_event = row['Event Date']
                    x_clea = row['Clearance Date']

                    if row['Status'] == 'RFQ':
                        state = 'draft'
                    elif row['Status'] == 'RFQ Sent':
                        state = 'sent'
                    elif row['Status'] == 'To Approve':
                        state = 'to approve'
                    elif row['Status'] == 'Purchase Order':
                        state = 'purchase'
                    elif row['Status'] == 'Locked':
                        state = 'done'
                    elif row['Status'] == 'Cancelled':
                        state = 'cancel'

                    vendor = self.env['res.partner'].search([('name', '=', row['Vendor'])], limit=1)
                    x_client = self.env['res.partner'].search([('name', '=', row['Client'])], limit=1)
                    x_project = self.env['project.project'].search([('name', '=', row['Project'])], limit=1)
                    x_attention = self.env['res.partner'].search([('name', '=', row['Attention'])], limit=1)
                    x_signatory = self.env['res.users'].search([('name', '=', row['Signatory Person'])], limit=1)
                    # purchase_rep = self.env['res.users'].search([('name', '=', row['Purchase Representative'])], limit=1)
                    if row['Status']:
                        order_data = {
                            'name': row['Order Reference'],
                            'partner_id': vendor.id if vendor else self.env['res.partner'].create({'name': row['Vendor']}).id,
                            'x_client': x_client.id,
                            'x_project': x_project.id,
                            'x_attention': x_attention.id,
                            'x_signatory': x_signatory.id,
                            'date_order': x_podate or None,
                            'x_podate': x_podate or None,
                            'x_set': x_set or None,
                            'x_comp': x_comp or None,
                            'x_event': x_event or None,
                            'x_clea': x_clea or None,
                            'state': state if state else 'draft'
                        }

                        # Create the new POS order
                        order_id = Order.create(order_data)
                        print(f'Created Purchase Order ID: {order_id}')

                    # If you have order lines, create them separately and link to the created order
                if not pd.isna(row['Product']):
                    product = self.env['product.product'].search([('name', '=', row['Product'])], limit=1)

                    order_line_data = {
                        'order_id': order_id.id,
                        'product_id': product.id if product else 1499,
                        'name': row['Description'],
                        'product_qty': row['Quantity'],
                        # 'qty_received': row['Received Qty'],
                        # 'qty_invoiced': row['Billed Qty'],
                        'price_unit': row['Unit Price'],
                    }
                    OrderLine.create(order_line_data)

                    print(f'Created Purchase Order Line for Order ID: {order_id}')


class AccountMove(models.Model):
    _inherit = 'account.move'

    def create_bills(self):
        orders = self.env['purchase.order'].search([('invoice_status', '=', 'to invoice')], limit=210)
        for o in orders:
            if not o.invoice_ids:
                try:
                    o.action_create_invoice()
                    for bill in o.invoice_ids:
                        bill.invoice_date = o.date_order
                        bill.date = o.date_order
                        bill.action_post()
                        ctx = {'active_model': 'account.move', 'active_ids': bill.ids}
                        payment = self.env['account.payment.register'].with_context(**ctx).create({
                            'amount': bill.amount_residual,
                            'payment_date': bill.invoice_date,
                            'journal_id': 6,  # Replace with your journal ID
                            'payment_method_line_id': 1,  # Replace with your payment method ID
                            'communication': bill.name,

                        })
                        payment_created = payment.action_create_payments()
                        print("payemnt_created", payment_created)
                except Exception as e:
                    # Handle the exception and pass to continue execution
                    print(f"Error: {e}")
                    pass

    def create_invoices(self):
        orders = self.env['sale.order'].search([('invoice_status', '=', 'to invoice')])
        for o in orders:
            if not o.invoice_ids:
                print("order=============", o)

                try:
                    downpayment = self.env['sale.advance.payment.inv'].with_context(
                        active_ids=o.ids, open_invoices=True).create({})
                    print("success downpayment", downpayment)
                    invoice = downpayment.create_invoices()
                    for inv in o.invoice_ids:
                        inv.date = o.date_order
                        inv.invoice_date = o.date_order
                        inv.invoice_date_due = o.date_order
                        inv.action_post()
                        ctx = {'active_model': 'account.move', 'active_ids': inv.ids}
                        payment = self.env['account.payment.register'].with_context(**ctx).create({
                            'amount': inv.amount_residual,
                            'payment_date': inv.invoice_date,
                            'journal_id': 6,  # Replace with your journal ID
                            'payment_method_line_id': 1,  # Replace with your payment method ID
                            'communication': inv.name,

                        })
                        payment_created = payment.action_create_payments()
                        print("payemnt_created", payment_created)

                    print("success invoice", invoice)
                except Exception as e:
                    # Handle the exception and pass to continue execution
                    print(f"Error: {e}")
                    pass
                # for inv in o.invoice_ids:
                #     inv.invoice_date = o.
