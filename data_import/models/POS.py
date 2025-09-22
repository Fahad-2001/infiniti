# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime
import pandas as pd

from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def create_payment_pos(self):
        orders = self.env['pos.order'].search([('state', '=', 'paid')], limit=200)
        for order_id in orders:
            try:
                order_id.action_pos_order_invoice()
                print('Created POS Order invoice')
            except Exception as e:
                # Handle the exception and pass to continue execution
                print(f"Error: {e}")
                pass

    def _generate_pos_order_invoice(self):
        moves = self.env['account.move']

        for order in self:
            # Force company for all SUPERUSER_ID action
            if order.account_move:
                moves += order.account_move
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            move_vals = order._prepare_invoice_vals()
            new_move = order._create_invoice(move_vals)

            order.write({'account_move': new_move.id, 'state': 'invoiced'})
            new_move.invoice_date = order.date_order.date()
            new_move.invoice_date_due = order.date_order.date()
            print(new_move.invoice_date, '111111111111111111111')
            new_move.sudo().with_company(order.company_id).with_context(skip_invoice_sync=True)._post()
            print(new_move.invoice_date, '222222222222222222222222222')

            # Send and Print
            if self.env.context.get('generate_pdf', True):
                template = self.env.ref(new_move._get_mail_template())
                new_move.with_context(skip_invoice_sync=True)._generate_pdf_and_send_invoice(template)

            moves += new_move
            payment_moves = order._apply_invoice_payments()

            if order.session_id.state == 'closed':  # If the session isn't closed this isn't needed.
                # If a client requires the invoice later, we need to revers the amount from the closing entry, by making a new entry for that.
                order._create_misc_reversal_move(payment_moves)

        if not moves:
            return {}

        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': moves and moves.ids[0] or False,
        }

    def import_order(self, file=None):
        if file:
            PosOrder = self.env['pos.order']
            PosOrderLine = self.env['pos.order.line']
            # payment = self.env['pos.payment']
            df = pd.read_excel(file)
            order_id = None
            # PM = None
            for index, row in df.iterrows():
                if pd.notna(row['Order Ref']):
                    if order_id is not None:
                        order_id.add_payment({
                            'pos_order_id': order_id.id,
                            'payment_date': order_id.date_order,
                            'amount': order_id.amount_total,
                            'payment_method_id': 2,
                        })
                        order_id.state = 'paid'
                        order_id._create_order_picking()
#                        order_id.action_pos_order_invoice()
#                     payment_method_id = self.env['pos.payment.method'].search([('name', '=', row['Payment Method'])],
#                                                                               limit=1)
                    # PM = payment_method_id
                    # vendor = self.env['res.partner'].search([('name', '=', row['Customer'])], limit=1)
                    # if vendor:
                    date_str = row['Date'].strip()  # Remove leading/trailing spaces
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    date_order = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                    order_data = {
                        'name': row['Order Ref'],
                        'session_id': 1,
                        'partner_id': 44,
                        'amount_total': row['Total'],
                        'date_order': date_order,
                        'amount_paid': 0.0,
                        'amount_return': 0.0,
                        'amount_tax': 0.0,
                        'state': 'draft',
                        'pos_reference': row['Receipt Number'],

                    }

                    order_id = PosOrder.create(order_data)
                    print(f'Created POS Order ID: {order_id.id}')

                if not pd.isna(row['Product']):
                    product = self.env['product.product'].search([('name', '=', row['Product'])], limit=1)
                    order_line_data = {
                        'order_id': order_id.id,
                        'product_id': product.id,
                        'full_product_name': product.name,
                        'qty': 1,
                        'price_unit': row['Total'],
                        'price_subtotal': row['Total'],
                        'price_subtotal_incl': row['Total'],

                    }
                    PosOrderLine.create(order_line_data)
                    print(f'Created POS Order Line for Order ID: {order_id}')

            print('All orders inserted successfully!')