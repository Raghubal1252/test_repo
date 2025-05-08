from odoo import api, fields, models, _
from datetime import datetime


class HrEmployeeCreate(models.TransientModel):
    _name = "hr.employee.create"
    _description = 'Hr Employee Create'

    partner_ids = fields.Many2many('res.partner', string=" Supplier name")
    name = fields.Many2one('res.partner', string="Supplier name")
    material_requisition_ref = fields.Char(string="Reference")
    order_lines = fields.One2many('hr.employee.create.line', 'line_order_id', string='Order Lines')

    def create_RFQ(self):
        obj_purchase_order = self.env['purchase.order']
        obj_purchase_order_line = self.env['purchase.order.line']

        if self.env.context.get('active_model') == 'material.requisition.indent':
            active_id = self.env.context.get('active_id', False)

            indent_id = self.env['material.requisition.indent'].search([('id', '=', active_id)])

            purchase_order_dict = {'partner_id': self.name.id, 'origin': indent_id.name,
                                   'purachse_rfq_request': True, 'indent_id': active_id}

            purchase_order = obj_purchase_order.create(purchase_order_dict)
            indent_id.write({
                'state': 'rfq_create'
            })

            # create a new dictionary for set value of order lines.
            for line in self.order_lines:
                if line:
                    product_tmpl_id = self.env['product.product'].search([('id', '=', line.product_id.id)])
                    order_line_dict = {
                        'product_id': product_tmpl_id.id,
                        'product_qty': line.product_qty,
                        'name': line.product_id.display_name,
                        'date_planned': datetime.today(),
                        'price_unit': line.price_unit,
                        'product_uom': product_tmpl_id.uom_id.id,
                        'order_id': purchase_order.id,
                    }
                    emp_purchase_order_id = obj_purchase_order_line.create(order_line_dict)

    # def create_tender(self):
    #     obj_purchase_tender = self.env['purchase.agreement']
    #     obj_purchase_tender_line = self.env['purchase.agreement.line']
    #
    #     if self.env.context.get('active_model') == 'material.requisition.indent':
    #         active_id = self.env.context.get('active_id', False)
    #
    #         indent_id = self.env['material.requisition.indent'].search([('id', '=', active_id)])
    #
    #         purchase_order_dict = {'partner_ids': self.partner_ids.ids, 'sh_source': indent_id.name,
    #                                'indent_id': active_id, 'state': 'draft'}
    #
    #         purchase_agreement = obj_purchase_tender.create(purchase_order_dict)
    #         indent_id.write({
    #             'state': 'tender_create'
    #         })
    #         # create a new dictionary for set value of order lines.
    #         for line in self.order_lines:
    #             if line:
    #                 product_tmpl_id = self.env['product.product'].search([('id', '=', line.product_id.id)])
    #                 order_line_dict = {
    #                     'sh_product_id': product_tmpl_id.id,
    #                     'sh_qty': line.product_qty,
    #                     'sh_price_unit': line.price_unit,
    #                     'agreement_id': purchase_agreement.id,
    #                 }
    #             emp_purchase_order_id = obj_purchase_tender_line.create(order_line_dict)


# create new class for get purchase order lines from wizard
class HrEmployeeCreateLine(models.TransientModel):
    _name = "hr.employee.create.line"
    _description = 'Hr Employee Create Line'

    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float('Quantity')
    price_unit = fields.Float('Unit Price')
    product_uom_id = fields.Many2one('uom.uom', 'UOM')
    line_order_id = fields.Many2one('hr.employee.create')
    on_hand_qty = fields.Float('On Hand Qty')

    @api.onchange('product_id')
    def onchange_product_id(self):
        for val in self:
            if val.product_id:
                val.product_uom_id = val.product_id.uom_id and val.product_id.uom_id.id


class DirectPORemark(models.TransientModel):
    _name = 'direct.po.remark.wizard'
    _description = 'Direct PO Remark'

    direct_po_remark = fields.Text(string='Direct Po Remark')

    def get_direct_po_remark(self):
        pass


class StoreVerifiedRemark(models.TransientModel):
    _name = 'store.verified.remark'
    _description = 'Store Verified Remark'

    store_verified_remark = fields.Text(string='Store Verified Remark')

    def get_store_verified_remark(self):
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['material.requisition.indent'].search([('id', '=', applicant_id)])
        for indent in active_id:
            indent.write({
                'state': 'request_approved_store',
                'store_approval': True,
                'ribbon_state': 'store_verified',
                'store_verified_remark': self.store_verified_remark,
            })
