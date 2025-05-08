from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MaterialApprovalConfig(models.Model):
    _name = 'material.approval.config'
    _description = 'Material Approval Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'type_of_purchase'

    def _default_seq_id(self):
        return self.env['ir.sequence'].search([('code', '=', 'material.requisition.indent')], limit=1).id

    def _default_journal(self):
        return self.env['account.journal'].search([('type', '=', 'sale')], limit=1).id

    @api.onchange('approval_levels')
    def onchange_approvals(self):
        if self.approval_levels:
            if self.approval_levels == 'first_level':
                self.first_approval = False
                self.second_approval = False
                self.third_approval = False
                self.fourth_approval = False
                self.fifth_approval = False
            elif self.approval_levels == 'second_level':
                self.first_approval = False
                self.second_approval = False
                self.third_approval = False
                self.fourth_approval = False
                self.fifth_approval = False
            elif self.approval_levels == 'third_level':
                self.first_approval = False
                self.second_approval = False
                self.third_approval = False
                self.fourth_approval = False
                self.fifth_approval = False
            elif self.approval_levels == 'fourth_level':
                self.first_approval = False
                self.second_approval = False
                self.third_approval = False
                self.fourth_approval = False
                self.fifth_approval = False
            elif self.approval_levels == 'fifth_level':
                self.first_approval = False
                self.second_approval = False
                self.third_approval = False
                self.fourth_approval = False
                self.fifth_approval = False

    color = fields.Integer('Color')
    approval_type = fields.Selection([
        ('material_request', 'Material Request Approvers'),
    ], default='material_request', copy=False, string="Approvals Type", readonly=True, tracking=True)
    type_of_purchase = fields.Char(string="Material Type", tracking=True, copy=False)
    approval_levels = fields.Selection([
        ('first_level', '1'),
        ('second_level', '2'),
        ('third_level', '3'),
        ('fourth_level', '4'),
        ('fifth_level', '5')], default='first_level', copy=False, string="No.of Approvals", tracking=True)
    first_approval = fields.Many2one('res.users', string="First Approval", tracking=True)
    second_approval = fields.Many2one('res.users', string="Second Approval", tracking=True)
    third_approval = fields.Many2one('res.users', string="Third Approval", tracking=True)
    fourth_approval = fields.Many2one('res.users', string="Fourth Approval", tracking=True)
    fifth_approval = fields.Many2one('res.users', string="Fifth Approval", tracking=True)
    first_approval_amount_from = fields.Float(string="", tracking=True)
    first_approval_amount_to = fields.Float(string="", tracking=True)
    second_approval_amount_from = fields.Float(string="", tracking=True)
    second_approval_amount_to = fields.Float(string="", tracking=True)
    third_approval_amount_from = fields.Float(string="", tracking=True)
    third_approval_amount_to = fields.Float(string="", tracking=True)
    fourth_approval_amount_from = fields.Float(string="", tracking=True)
    fourth_approval_amount_to = fields.Float(string="", tracking=True)
    fifth_approval_amount_from = fields.Float(string="", tracking=True)
    fifth_approval_amount_to = fields.Float(string="", tracking=True)
    material_limit = fields.Float(string="Material Value", tracking=True)
    product_categ = fields.Many2many('product.category', string="Product Categories", tracking=True)
    default_type = fields.Boolean(string="Default")
    lc_applicable = fields.Boolean(string="LC Applicable")
    seq_id = fields.Many2one('ir.sequence', string="Sequence", default=_default_seq_id)
    purchase_journal_id = fields.Many2one('account.journal', string="Material Journal",
                                          domain=['|', ('type', '=', 'purchase'), ('company_id', '=', 'company_id')])

    purchase_cancel_users = fields.Many2many('res.users', 'purchase_cancel_user_rel', string='Approved Purchase Cancel')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    material_types = fields.Selection([
        ('local', 'Local'),
        ('import', 'Import'),
        ('general', 'General'),
        ('asset', 'Asset'),
    ], 'Material Types', tracking=True)

    def name_get(self):
        result = []
        for bank in self:
            name = bank.type_of_purchase
            result.append((bank.id, name))
        return result

    @api.model
    def create(self, vals):
        res = super(MaterialApprovalConfig, self).create(vals)
        if vals.get('approval_levels') in ('first_level', 'second_level', 'third_level'):
            if not vals.get('first_approval'):
                raise UserError(_('Kindly set the First Approval.'))
        if vals.get('approval_levels') in ('second_level', 'third_level'):
            if not vals.get('second_approval'):
                raise UserError(_('Kindly set the Second Approval.'))
        if vals.get('approval_levels') == 'third_level':
            if not vals.get('third_approval'):
                raise UserError(_('Kindly set the Third Approval.'))
        if vals.get('approval_levels') == 'fourth_level':
            if not vals.get('fourth_approval'):
                raise UserError(_('Kindly set the Fourth Approval.'))
        if vals.get('approval_levels') == 'fifth_level':
            if not vals.get('fifth_approval'):
                raise UserError(_('Kindly set the Fifth Approval.'))
        return res

    def write(self, vals):
        res = super(MaterialApprovalConfig, self).write(vals)
        if vals.get('approval_levels') in ('first_level', 'second_level', 'third_level') or \
                self.approval_levels in ('first_level', 'second_level', 'third_level'):
            if vals.get('first_approval') == False or self.first_approval == False:
                raise UserError(_('Kindly set the First Approval.'))
        if vals.get('approval_levels') in ('second_level', 'third_level') or \
                self.approval_levels in ('second_level', 'third_level'):
            if vals.get('second_approval') == False or self.second_approval == False:
                raise UserError(_('Kindly set the Second Approval.'))
        if vals.get('approval_levels') == 'third_level' or \
                self.approval_levels == 'third_level':
            if vals.get('third_approval') == False or self.third_approval == False:
                raise UserError(_('Kindly set the Third Approval.'))
        if vals.get('approval_levels') == 'fourth_level' or \
                self.approval_levels == 'fourth_level':
            if vals.get('fourth_approval') == False or self.fourth_approval == False:
                raise UserError(_('Kindly set the Fourth Approval.'))
        if vals.get('approval_levels') == 'fifth_level' or \
                self.approval_levels == 'fifth_level':
            if vals.get('fifth_approval') == False or self.fifth_approval == False:
                raise UserError(_('Kindly set the Fifth Approval.'))
        return res
