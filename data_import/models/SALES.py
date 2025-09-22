# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import pandas as pd


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def import_sale_order(self, file=None):
        if file:
            Order = self.env['sale.order']
            OrderLine = self.env['sale.order.line']

            df = pd.read_excel(file)
            for index, row in df.iterrows():
                # Prepare data for the new POS order
                # if row['Order Reference'].isna
                print("vendor============", row['Customer'])
                if pd.notna(row['Order Reference']):
                    confirm_date_str = row['Order Date']  # Remove leading/trailing spaces
                    # confirm_date_obj = datetime.strptime(confirm_date_str, "%d-%b-%Y %I:%M:%S %p")
                    # confirm_date = confirm_date_obj.strftime("%Y-%m-%d %H:%M:%S")

                    vendor = self.env['res.partner'].search([('name', '=', row['Customer'])], limit=1)
                    # purchase_rep = self.env['res.users'].search([('name', '=', row['Purchase Representative'])], limit=1)
                    if vendor:
                        if row['Status'] == 'Quotation':
                            state = 'draft'
                        elif row['Status'] == 'Quotation Sent':
                            state = 'sent'
                        elif row['Status'] == 'Sales Order':
                            state = 'sale'
                        elif row['Status'] == 'Cancelled':
                            state = 'cancel'

                        order_data = {
                            'name': row['Order Reference'],
                            'partner_id': vendor.id,
                            'date_order': confirm_date_str,
                            'state': state if state else None
                            # 'priority': row['Priority'] if pd.notna(row['Priority']) else '',
                            # 'user_id': purchase_rep.id if purchase_rep else None, \
                            # 'origin': row['Source Document'] if pd.notna(row['Source Document']) else '',

                        }

                        # Create the new POS order
                        order_id = Order.create(order_data)
                        print(f'Created Sale Order ID: {order_id}')

                    # If you have order lines, create them separately and link to the created order
                if not pd.isna(row['Product']) and order_id:
                    product = self.env['product.product'].search([('name', '=', row['Product'])], limit=1)
                    order_line_data = {
                        'order_id': order_id.id,
                        'product_id': product.id if product else 9,
                        'name': row['Description'],
                        'product_uom_qty': row['Quantity'],
                        'qty_delivered': row['Delivered Quantity'],
                        # 'qty_invoiced': row['Invoiced Quantity'],
                        'price_unit': row['Unit Price'],
                        'discount': row['Discount'],
                    }
                    OrderLine.create(order_line_data)
                    print(f'Created Sale Order Line for Order ID: {order_id}')