from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purachse_rfq_request = fields.Boolean(string="Material RFQ Request", copy=False)
    indent_id = fields.Many2one('material.requisition.indent', 'Indent')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    responsible = fields.Many2one('res.partner', string='Request Raised By')
    requested = fields.Many2one('res.partner', string='Request Raised For')
    shipment = fields.Boolean('Shipment', copy=False)

    def create_qty_material(self):
        print('-------------------1')
        material_requisition_sr = self.env['material.requisition.indent'].search([('name', '=', self.origin)])
        purchase_order = self.env['purchase.order'].search([('name', '=', self.origin)])
        mr_list = self.env['material.requisition.indent'].search([('name', '=', purchase_order.origin)])
        stock_pic = self.env['stock.picking'].search([('origin', '=', self.origin)])
        if self.origin:
            mr_list.update({
                'grn_status': True,
                'ribbon_state': 'grn_completed',
            })
        for num in stock_pic:
            print('-------------------2')
            # for line in material_requisition_sr.product_lines:
            print('-------------------3', num.state)
            if num.state == 'assigned':
                print('-------------------4')
                material_requisition_sr.update({
                    'state': 'done',
                    'stock_transferred': True,
                    'ribbon_state': 'delivery_done',
                    'issued_date': num.write_date,
                    'inward_date': num.scheduled_date,
                    'store_incharge': self.env.user.name,
                })
            added_qty = 0.0
            for line in material_requisition_sr.product_lines:
                added_qty = 0.0
                for val in stock_pic:
                    for qty in val.move_ids_without_package:
                        if qty.product_id.id == line.product_id.id:
                            added_qty += qty.quantity
                            product_id = qty.product_id
                    if val.product_id.id == line.product_id.id:
                        line.update({
                            'qty_shipped': added_qty,
                        })
            return True

    def button_validate(self):
        self.create_qty_material()
        return super().button_validate()

