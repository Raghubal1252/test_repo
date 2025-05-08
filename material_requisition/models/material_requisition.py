from datetime import datetime, timedelta
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError


class MaterialRequisitionIndent(models.Model):
    _name = 'material.requisition.indent'
    _description = 'Indent'
    _inherit = ['mail.thread']
    _order = "verified_date desc"

    def _get_stock_type_ids(self):
        data = self.env['stock.picking.type'].search([])
        for line in data:
            if line.code == 'outgoing':
                return line

    def _default_employee(self):
        emp_ids = self.sudo().env['hr.employee'].search([('user_id', '=', self.env.uid)])
        return emp_ids and emp_ids[0] or False

    name = fields.Char(string='Indent Reference', size=256, tracking=True, required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('/'),
                       help='A unique sequence number for the Indent')
    responsible = fields.Many2one('hr.employee', string='Request Raised By', default=_default_employee, readonly=True,
                                  help="Responsible person for the Material Request Approvers")
    verified_date = fields.Datetime('Verified Date', readonly=True, tracking=True)
    indent_date = fields.Datetime('Indent Date', required=True,
                                  default=lambda self: fields.Datetime.now())
    required_date = fields.Datetime('Required Date', required=True)
    indentor_id = fields.Many2one('res.users', 'Indentor', tracking=True)
    department_id = fields.Many2one(string='Department', related='responsible.department_id', required=True,
                                    readonly=True, tracking=True)
    current_job_id = fields.Many2one(related='responsible.job_id', string=" Job Position", required=True)
    current_reporting_manager = fields.Many2one(related='responsible.parent_id', string="Reporting Manager",
                                                required=True)
    request_raised_for = fields.Many2one('hr.employee', string='Request Raised For',
                                         help="Request person for the Material")
    requester_department_id = fields.Many2one('hr.department', string=' Department', required=True, tracking=True)
    requester_current_job_id = fields.Many2one('hr.job', string="Job Position", required=True)
    requester_current_reporting_manager = fields.Many2one('hr.employee', string=" Reporting Manager",
                                                          required=True)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    purpose = fields.Char('Purpose', required=True, tracking=True)
    location_id = fields.Many2one('stock.location', 'Destination Location', required=True,
                                  tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Project', ondelete="cascade", readonly=True,
                                          tracking=True)
    requirement = fields.Selection([('1', 'Ordinary'), ('2', 'Urgent')], 'Requirement', required=True,
                                   tracking=True)
    type = fields.Selection([('stock', 'Stock')], 'Type', default='stock', required=True,
                            tracking=True, readonly=True)
    product_lines = fields.One2many('material.requisition.product.lines', 'indent_id', 'Products')
    request_product_lines = fields.One2many('material.requisition.request.product.lines', 'indent_id', ' Products')
    picking_id = fields.Many2one('stock.picking', 'Picking')
    in_picking_id = fields.Many2one('stock.picking', ' Picking')
    description = fields.Text('Additional Information', readonly=True)
    active = fields.Boolean('Active', default=True)
    item_for = fields.Selection([('store', 'Store'), ('capital', 'Capital')], 'Material Requisition for', readonly=True)
    ribbon_state = fields.Selection(
        [('not_available', 'Stock Not Available'), ('mr_stock_available', 'Stock Available'),
         ('store_to_verify', 'Store to Verify'),
         ('store_verified', 'Store Verified'),
         ('partial_stock', 'Partially Stock Available'),
         ('partial_stock_delivered', 'Partially Stock Delivery Created'),
         ('stock_delivered', 'Stock Delivery Created'),
         ('delivery_done', 'Delivery Completed'),
         ('partial_delivery_done', 'Partial Delivery Completed'),
         ('rfq_raise', 'RFQ/PO Raised'),
         ('tender_raise', 'Tender Raised'),
         ('grn_completed', 'GRN Completed'),
         ('draft', 'Draft'),
         ('request_to_approve', 'Request To Approve'),
         ('to_be_approved', 'Waiting 1st Level Approval'),
         ('leader_approval', 'Waiting 2nd Level Approval'),
         ('manager_approval', 'Waiting 3rd Level Approval'),
         ('director_approval', 'Waiting 4th Level Approval'),
         ('ceo_approval', 'Waiting 5th Level Approval'),
         ('final_approval', 'Waiting Final Approval'),
         ('request_approved', 'Approved'),
         ('reject', 'Rejected'),
         ('cancel', 'Cancelled'),
         ], 'Ribbon State',
        default="store_to_verify", readonly=True, tracking=True)
    approver_id = fields.Many2one('res.users', 'Authority', readonly=True, tracking=True,
                                  help="who have approve or reject indent.")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', help="default warehose where inward will be taken",
                                   readonly=True)
    move_type = fields.Selection([('direct', 'Partial'), ('one', 'All at once')], 'Receive Method', tracking=True,
                                 readonly=True,
                                 help="It specifies goods to be deliver partially or all at once")
    manager_id = fields.Many2one('res.users', string='Manager', default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Approved By')
    picking_count = fields.Integer(string="Count", copy=False)
    invoice_picking_id = fields.Many2one('stock.picking', string="Picking Id", copy=False)
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',
                                      default=_get_stock_type_ids,
                                      help="This will determine picking type of incoming shipment")
    material_requisition_backorder_count = fields.Integer(compute='_compute_material_requisition_backorder',
                                                          string='Back Order',
                                                          default=0)
    purchase_order_count = fields.Integer(compute='_compute_material_requisition_po', string='Purchase Order',
                                          default=0)
    rfq_total = fields.Integer('My RFQ', compute='compute_order')
    rfq_order_ids = fields.One2many('purchase.order', 'indent_id')
    stock_available = fields.Boolean('Stock')
    partial_stock_available = fields.Boolean('Partial Stock')
    enable_ribbon = fields.Boolean('Ribbon Active')
    stock_transferred = fields.Boolean('Stock Transferred')
    partial_stock_transferred = fields.Boolean('Partial Stock Transferred')
    partial_delivery = fields.Boolean('Partial Delivery')
    store_approval = fields.Boolean('Store Approval')
    store_request = fields.Boolean('Store Request')
    mr_reject = fields.Boolean('MR Reject')
    rfq_raised = fields.Boolean('RFQ Raised', default=False)
    tender_raised = fields.Boolean('Tender Raised', default=False)
    last_poll = fields.Datetime('Last Poll', default=lambda self: fields.Datetime.now())
    issued_date = fields.Datetime('Issued Date')
    inward_date = fields.Datetime('Inward Date')
    po_approved_by = fields.Char('PO Approved By')
    store_incharge = fields.Char('Store In-charge')
    approver1_reject_reason = fields.Text('1st Approver Reject Remarks')
    approver2_reject_reason = fields.Text('2nd Approver Reject Remarks')
    approver3_reject_reason = fields.Text('3rd Approver Reject Remarks')
    approver4_reject_reason = fields.Text('4th Approver Reject Remarks')
    approver5_reject_reason = fields.Text('5th Approver Reject Remarks')
    approver1_cancel_reason = fields.Text('1st Approver Cancel Remarks')
    approver2_cancel_reason = fields.Text('2nd Approver Cancel Remarks')
    approver3_cancel_reason = fields.Text('3rd Approver Cancel Remarks')
    approver4_cancel_reason = fields.Text('4th Approver Cancel Remarks')
    approver5_cancel_reason = fields.Text('5th Approver Cancel Remarks')
    approver1_approve_reason = fields.Text('1st Approver Approval Remarks')
    approver2_approve_reason = fields.Text('2nd Approver Approval Remarks')
    approver3_approve_reason = fields.Text('3rd Approver Approval Remarks')
    approver4_approve_reason = fields.Text('4th Approver Approval Remarks')
    approver5_approve_reason = fields.Text('5th Approver Approval Remarks')
    store_verified_remark = fields.Text('Store Verified Remarks')
    current_date = fields.Datetime(string='Current DateTime')
    add_hour_date = fields.Datetime(string='One Hour')
    cron_Boolean = fields.Boolean(string='Boolean')
    grn_status = fields.Boolean('GRN Status', default=False)

    type_of_purchase = fields.Many2one('material.approval.config', string="Type Of Material", copy=False,
                                       domain="[('approval_type','=', 'material_request')]",
                                       tracking=True)
    approval_responsible = fields.Many2one('res.users', copy=False, store=True, compute="compute_approver",
                                           string="Approval Responsible", tracking=True)
    approver1 = fields.Many2one('res.users', string="Approver 1", copy=False, tracking=True,
                                related='type_of_purchase.first_approval')
    approver2 = fields.Many2one('res.users', string="Approver 2", copy=False, tracking=True,
                                related='type_of_purchase.second_approval')
    approver3 = fields.Many2one('res.users', string="Approver 3", copy=False, tracking=True,
                                related='type_of_purchase.third_approval')
    approver4 = fields.Many2one('res.users', string="Approver 4", copy=False, tracking=True,
                                related='type_of_purchase.fourth_approval')
    approver5 = fields.Many2one('res.users', string="Approver 5", copy=False, tracking=True,
                                related='type_of_purchase.fifth_approval')
    approval_stages = fields.Selection([
        ('first_level', '1'),
        ('second_level', '2'),
        ('third_level', '3'),
        ('fourth_level', '4'),
        ('fifth_level', '5')], string="No.of Approvals", related='type_of_purchase.approval_levels')
    approval_checked = fields.Boolean(string="Approval Checked", copy=False)
    is_request_approval = fields.Boolean(string="Request Approval", copy=False, default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_be_approved', 'Waiting 1st Level Approval'),
        ('leader_approval', 'Waiting 2nd Level Approval'),
        ('manager_approval', 'Waiting 3rd Level Approval'),
        ('director_approval', 'Waiting 4th Level Approval'),
        ('ceo_approval', 'Waiting 5th Level Approval'),
        ('request_approved', 'Approved'),
        ('reject', 'Rejected'),
        ('request_rfq', 'Request For RFQ'),
        ('rfq_create', 'RFQ Created'),
        ('tender_create', 'Tender Created'),
        ('inprogress', 'In Progress'), ('received', 'Delivered'),
        ('partially_received', 'Partially Delivered'),
        ('done', 'Done'),
        ('request_for_store_approval', 'Request for Store Verify'),
        ('request_approved_store', 'Request Verified By Store Team'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, tracking=True)
    automated_sequence = fields.Boolean('Automated Sequence?',
                                        help="If checked, the Approval Requests will have an automated generated name "
                                             "based on the given code.")

    request_to_validate_count = fields.Integer("Number of requests to validate",
                                               compute="_compute_request_to_validate_count")

    @api.depends('state')
    def compute_approver(self):
        for order in self:
            if order.approval_stages == 'first_level':
                order.approval_responsible = order.approver1
            elif order.approval_stages == 'second_level':
                if order.state in ('draft', 'to_be_approved'):
                    order.approval_responsible = order.approver1
                elif order.state == 'leader_approval':
                    order.approval_responsible = order.approver2
            elif order.approval_stages == 'third_level':
                if order.state in ('draft', 'to_be_approved'):
                    order.approval_responsible = order.approver1
                elif order.state == 'leader_approval':
                    order.approval_responsible = order.approver2
                elif order.state == 'manager_approval':
                    order.approval_responsible = order.approver3

    def indent_request_for_store_approval(self):
        date = datetime.now()
        self.current_date = date
        hour = datetime.now() + timedelta(days=10)
        self.add_hour_date = hour
        if self.add_hour_date:
            self.write({'cron_Boolean': True})
        for indent in self:
            indent.write({
                'state': 'draft',
                'store_request': True,
                'ribbon_state': 'store_to_verify',
            })

    def indent_request_approved_store(self):
        view_id = self.env['store.verified.remark']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Store Verified Remark',
            'res_model': 'store.verified.remark',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('material_requisition.view_store_verified_remark_form', False).id,
            'target': 'new',
        }

    def get_line_items(self):
        line_vals = []
        for line in self:
            if line.request_product_lines:
                for pro in line.request_product_lines:
                    if pro.short_close:
                        vals = [0, 0, {
                            'product_id': pro.original_product_id.id,
                            'product_uom_qty': pro.approved_product_uom_qty,
                            'product_uom': pro.approved_product_uom.id,
                            'product_available': pro.approved_product_available,
                            'product_category': pro.approved_product_category.id,
                            'product_type': pro.approved_product_type,
                        }]
                        line_vals.append(vals)
                    else:
                        vals = [0, 0, {
                            'product_id': pro.product_id.id,
                            'product_uom_qty': pro.product_uom_qty,
                            'product_uom': pro.product_uom.id,
                            'product_available': pro.product_available,
                            'product_category': pro.product_category.id,
                            'product_type': pro.product_type,
                        }]
                        line_vals.append(vals)
        return line_vals

    def request_create_rfq(self):
        for indent in self:
            state = indent.state = 'request_rfq'
            return state

    def check_product_confirm(self):
        requisition_created = False
        for line in self:
            if line.request_product_lines:
                requisition_created = line.update({
                    'product_lines': line.get_line_items(),
                })

    def indent_confirm(self):
        for indent in self:
            indent.check_product_confirm()
            if not indent.product_lines:
                raise ValidationError('Alert!!,Mr.%s. You cannot confirm an indent %s which has no line.' % (
                    indent.env.user.name, indent.name))
            else:
                if indent.product_lines:
                    indent.write({
                        'state': 'to_be_approved',
                        'verified_date': fields.Datetime.now()})

    def set_draft(self):
        for indent in self:
            indent.state = 'draft'
            indent.write({
                'approver1_reject_reason': False,
                'approver2_reject_reason': False,
                'approver3_reject_reason': False,
                'approver4_reject_reason': False,
                'approver5_reject_reason': False,
                'approver1_cancel_reason': False,
                'approver2_cancel_reason': False,
                'approver3_cancel_reason': False,
                'approver4_cancel_reason': False,
                'approver5_cancel_reason': False,
            })
            for j in indent.product_lines:
                j.unlink()


    def material_requisition_approve_remarks(self):
        view_id = self.env['material.requisition.approve.remarks']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Material Requisition Approval Remarks',
            'res_model': 'material.requisition.approve.remarks',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('material_requisition.material_requisition_approve_remarks_wizard', False).id,
            'target': 'new',
        }

    def material_requisition_reject_remarks(self):
        view_id = self.env['material.requisition.reject.remarks']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Material Requisition Reject Remarks',
            'res_model': 'material.requisition.reject.remarks',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('material_requisition.material_requisition_reject_remarks_wizard', False).id,
            'target': 'new',
        }

    def material_requisition_cancel_remarks(self):
        view_id = self.env['material.requisition.cancel.remarks']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Material Requisition Cancel Remarks',
            'res_model': 'material.requisition.cancel.remarks',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('material_requisition.material_requisition_cancel_remarks_wizard', False).id,
            'target': 'new',
        }

    def apply_approval(self):
        for indent in self:
            indent.button_leader_approval()

    def apply_rejection(self):
        for indent in self:
            indent.button_leader_reject()

    def apply_cancellation(self):
        for indent in self:
            indent.button_leader_cancel()

    def button_leader_approval(self):
        if self.state == 'to_be_approved' or self.state == 'rfq_create' or self.state == 'tender_create':
            if self.approval_stages == 'first_level':
                self.button_approval()
            elif self.approval_stages != ('first_level', 'second_level', 'third_level', 'fourth_level'):
                if self.approver1.id == self._uid or self.approver2.id == self._uid \
                        or self.approver3.id == self._uid or self.approver4.id == self._uid or self.approver5.id == self._uid:
                    if self.approver1.id == self._uid:
                        self.write({'state': 'leader_approval'})
                    elif self.approver2.id == self._uid:
                        self.state = 'manager_approval'
                    elif self.approver3.id == self._uid:
                        self.state = 'director_approval'
                    elif self.approver4.id == self._uid:
                        self.state = 'ceo_approval'
                    elif self.approver5.id == self._uid:
                        self.state = 'request_approved'
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to approve this %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        elif self.state == 'leader_approval':
            if self.approval_stages == 'second_level':
                self.button_approval()
            elif self.approval_stages != ('second_level', 'third_level', 'fourth_level'):
                if self.approver2.id == self._uid or self.approver3.id == self._uid \
                        or self.approver4.id == self._uid or self.approver5.id == self._uid:
                    self.state = 'manager_approval'
                elif self.approver3.id == self._uid:
                    self.state = 'director_approval'
                elif self.approver4.id == self._uid:
                    self.state = 'ceo_approval'
                elif self.approver5.id == self._uid:
                    self.state = 'request_approved'
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to approve this %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        elif self.state == 'manager_approval':
            if self.approval_stages == 'third_level':
                self.button_approval()
            elif self.approval_stages != ('third_level', 'fourth_level'):
                if self.approver3.id == self._uid or self.approver4.id == self._uid or self.approver5.id == self._uid:
                    self.state = 'director_approval'
                elif self.approver4.id == self._uid:
                    self.state = 'ceo_approval'
                elif self.approver5.id == self._uid:
                    self.state = 'request_approved'
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to approve this %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        elif self.state == 'director_approval':
            if self.approval_stages == 'fourth_level':
                self.button_approval()
            elif self.approval_stages != 'fourth_level':
                if self.approver4.id == self._uid or self.approver5.id == self._uid:
                    if self.approver4.id:
                        self.state = 'ceo_approval'
                    elif self.approver5.id == self._uid:
                        self.state = 'request_approved'
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to approve this %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        elif self.state == 'ceo_approval':
            if self.approver5.id == self._uid:
                self.state = 'request_approved'
            else:
                raise UserError(_('Alert !, Mr.%s You Cannot allowed to approve this %s Material Requisition.') %
                                (self.env.user.name, self.name))

    def button_approval(self):
        if self.state == 'to_be_approved' or self.state == 'rfq_create' or self.state == 'tender_create':
            if self.approval_stages == 'first_level':
                if self.approver1.id == self._uid:
                    self.set_approval()
                else:
                    raise UserError(
                        _('Alert !, Mr.%s You Cannot allowed For the First approval of %s Material Requisition.') %
                        (self.env.user.name, self.name))
        if self.state == 'leader_approval':
            if self.approval_stages == 'second_level':
                if self.approver2.id == self._uid:
                    self.set_approval()
                else:
                    raise UserError(
                        _('Alert !, Mr.%s You Cannot allowed For the Second approval of %s Material Requisition.') %
                        (self.env.user.name, self.name))
        if self.state == 'manager_approval':
            if self.approval_stages == 'third_level':
                if self.approver3.id == self._uid:
                    self.set_approval()
                else:
                    raise UserError(
                        _('Alert !, Mr.%s You Cannot allowed For the Third approval of %s Material Requisition.') %
                        (self.env.user.name, self.name))
        if self.state == 'director_approval':
            if self.approval_stages == 'fourth_level':
                if self.approver4.id == self._uid:
                    self.set_approval()
                else:
                    raise UserError(
                        _('Alert !, Mr.%s You Cannot allowed For the Fourth approval of %s Material Requisition.') %
                        (self.env.user.name, self.name))

    def button_reject(self):
        if self.state == 'to_be_approved' or self.state == 'rfq_create' or self.state == 'tender_create':
            if self.approval_stages == 'first_level':
                if self.approver1.id == self._uid:
                    self.indent_reject()
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to Reject The %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        if self.state == 'leader_approval':
            if self.approval_stages == 'second_level':
                if self.approver2.id == self._uid:
                    self.indent_reject()
                else:
                    raise UserError(
                        _('Alert !, Mr.%s You Cannot allowed to Reject The %s Material Requisition.') %
                        (self.env.user.name, self.name))
        if self.state == 'manager_approval':
            if self.approval_stages == 'third_level':
                if self.approver3.id == self._uid:
                    self.indent_reject()
                else:
                    raise UserError(
                        _('Alert !, Mr.%s You Cannot allowed to Reject The %s Material Requisition.') %
                        (self.env.user.name, self.name))
        if self.state == 'director_approval':
            if self.approval_stages == 'fourth_level':
                if self.approver4.id == self._uid:
                    self.indent_reject()
                else:
                    raise UserError(
                        _('Alert !, Mr.%s You Cannot allowed to Reject The %s Material Requisition.') %
                        (self.env.user.name, self.name))

    def indent_reject(self):
        for indent in self:
            indent.write({
                'state': 'reject',
                'ribbon_state': 'reject',
            })

    def button_leader_reject(self):
        if self.state == 'to_be_approved' or self.state == 'rfq_create' or self.state == 'tender_create':
            if self.approval_stages == 'first_level':
                self.button_reject()
            elif self.approval_stages != ('first_level', 'second_level', 'third_level', 'fourth_level'):
                if self.approver1.id == self._uid or self.approver2.id == self._uid \
                        or self.approver3.id == self._uid or self.approver4.id == self._uid or self.approver5.id == self._uid:
                    if self.approver1.id == self._uid:
                        self.indent_reject()
                    elif self.approver2.id == self._uid:
                        self.indent_reject()
                    elif self.approver3.id == self._uid:
                        self.indent_reject()
                    elif self.approver4.id == self._uid:
                        self.indent_reject()
                    elif self.approver5.id == self._uid:
                        self.indent_reject()
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to Reject The %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        elif self.state == 'leader_approval':
            if self.approval_stages == 'second_level':
                self.button_reject()
            elif self.approval_stages != ('second_level', 'third_level', 'fourth_level'):
                if self.approver2.id == self._uid or self.approver3.id == self._uid \
                        or self.approver4.id == self._uid or self.approver5.id == self._uid:
                    self.indent_reject()
                elif self.approver3.id == self._uid:
                    self.indent_reject()
                elif self.approver4.id == self._uid:
                    self.indent_reject()
                elif self.approver5.id == self._uid:
                    self.indent_reject()
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to Reject The %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        elif self.state == 'manager_approval':
            if self.approval_stages == 'third_level':
                self.indent_reject()
            elif self.approval_stages != ('third_level', 'fourth_level'):
                if self.approver3.id == self._uid or self.approver4.id == self._uid or self.approver5.id == self._uid:
                    self.indent_reject()
                elif self.approver4.id == self._uid:
                    self.indent_reject()
                elif self.approver5.id == self._uid:
                    self.indent_reject()
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to Reject The %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        elif self.state == 'director_approval':
            if self.approval_stages == 'fourth_level':
                self.button_reject()
            elif self.approval_stages != 'fourth_level':
                if self.approver4.id == self._uid or self.approver5.id == self._uid:
                    self.indent_reject()
                elif self.approver5.id == self._uid:
                    self.indent_reject()
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to Reject The %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        elif self.state == 'ceo_approval':
            if self.approver5.id == self._uid:
                self.button_reject()
            else:
                raise UserError(_('Alert !, Mr.%s You Cannot allowed to Reject The %s Material Requisition.') %
                                (self.env.user.name, self.name))
        return True

    def indent_cancel(self):
        for indent in self:
            indent.write({
                'state': 'cancel',
                'ribbon_state': 'cancel'
            })

    def button_leader_cancel(self):
        if self.state == 'to_be_approved' or self.state == 'rfq_create' or self.state == 'tender_create':
            if self.approval_stages == 'first_level':
                self.button_cancels()
            elif self.approval_stages != ('first_level', 'second_level', 'third_level', 'fourth_level'):
                if self.approver1.id == self._uid or self.approver2.id == self._uid \
                        or self.approver3.id == self._uid or self.approver4.id == self._uid or self.approver5.id == self._uid:
                    if self.approver1.id == self._uid:
                        self.indent_cancel()
                    elif self.approver2.id == self._uid:
                        self.indent_cancel()
                    elif self.approver3.id == self._uid:
                        self.indent_cancel()
                    elif self.approver4.id == self._uid:
                        self.indent_cancel()
                    elif self.approver5.id == self._uid:
                        self.indent_cancel()
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to Cancel The %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        elif self.state == 'leader_approval':
            if self.approval_stages == 'second_level':
                self.button_cancels()
            elif self.approval_stages != ('second_level', 'third_level', 'fourth_level'):
                if self.approver2.id == self._uid or self.approver3.id == self._uid \
                        or self.approver4.id == self._uid or self.approver5.id == self._uid:
                    self.indent_cancel()
                elif self.approver3.id == self._uid:
                    self.indent_cancel()
                elif self.approver4.id == self._uid:
                    self.indent_cancel()
                elif self.approver5.id == self._uid:
                    self.indent_cancel()
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to Cancel The %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        elif self.state == 'manager_approval':
            if self.approval_stages == 'third_level':
                self.indent_cancel()
            elif self.approval_stages != ('third_level', 'fourth_level'):
                if self.approver3.id == self._uid or self.approver4.id == self._uid or self.approver5.id == self._uid:
                    self.indent_cancel()
                elif self.approver4.id == self._uid:
                    self.indent_cancel()
                elif self.approver5.id == self._uid:
                    self.indent_cancel()
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to Cancel The %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        elif self.state == 'director_approval':
            if self.approval_stages == 'fourth_level':
                self.button_cancels()
            elif self.approval_stages != 'fourth_level':
                if self.approver4.id == self._uid or self.approver5.id == self._uid:
                    self.indent_cancel()
                elif self.approver5.id == self._uid:
                    self.indent_cancel()
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to Cancel The %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        elif self.state == 'ceo_approval':
            if self.approver5.id == self._uid:
                self.button_cancels()
            else:
                raise UserError(_('Alert !, Mr.%s You Cannot allowed to Cancel The %s Material Requisition.') %
                                (self.env.user.name, self.name))
        return True

    def button_cancels(self):
        if self.state == 'to_be_approved' or self.state == 'rfq_create' or self.state == 'tender_create':
            if self.approval_stages == 'first_level':
                if self.approver1.id == self._uid:
                    self.indent_cancel()
                else:
                    raise UserError(_('Alert !, Mr.%s You Cannot allowed to Cancel The %s Material Requisition.') %
                                    (self.env.user.name, self.name))
        if self.state == 'leader_approval':
            if self.approval_stages == 'second_level':
                if self.approver2.id == self._uid:
                    self.indent_cancel()
                else:
                    raise UserError(
                        _('Alert !, Mr.%s You Cannot allowed to Cancel The %s Material Requisition.') %
                        (self.env.user.name, self.name))
        if self.state == 'manager_approval':
            if self.approval_stages == 'third_level':
                if self.approver3.id == self._uid:
                    self.indent_cancel()
                else:
                    raise UserError(
                        _('Alert !, Mr.%s You Cannot allowed to Cancel The %s Material Requisition.') %
                        (self.env.user.name, self.name))
        if self.state == 'director_approval':
            if self.approval_stages == 'fourth_level':
                if self.approver4.id == self._uid:
                    self.indent_cancel()
                else:
                    raise UserError(
                        _('Alert !, Mr.%s You Cannot allowed to Cancel The %s Material Requisition.') %
                        (self.env.user.name, self.name))

    @api.onchange('request_raised_for')
    def requester_details(self):
        if self.request_raised_for:
            self.sudo().write({
                'requester_current_reporting_manager': self.request_raised_for.parent_id.id,
                'requester_department_id': self.request_raised_for.department_id.id,
                'requester_current_job_id': self.request_raised_for.job_id.id,
            })

    def action_stock_move(self):
        if not self.picking_type_id:
            raise UserError(_(
                " Please select a picking type"))
        for order in self:
            if not self.invoice_picking_id:
                pick = {}
                if self.picking_type_id.code == 'outgoing':
                    pick = {
                        'picking_type_id': order.picking_type_id.id,
                        'partner_id': order.responsible.user_id.partner_id.id,
                        'responsible': order.responsible.user_id.partner_id.id,
                        'requested': order.request_raised_for.user_id.partner_id.id,
                        'shipment': True,
                        'origin': order.name,
                        'location_dest_id': order.responsible.address_id.property_stock_customer.id,
                        'location_id': order.picking_type_id.default_location_src_id.id,
                        'move_type': 'direct'
                    }
                picking = self.env['stock.picking'].create(pick)
                self.invoice_picking_id = picking.id
                self.picking_count = len(picking)
                moves = order.product_lines.filtered(lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves(picking)
                move_ids = moves._action_confirm()
                move_ids._action_assign()
                self.write({'state': 'received', 'ribbon_state': 'stock_delivered'})

    def action_partial_stock_move(self):
        if not self.picking_type_id:
            raise UserError(_(
                " Please select a picking type"))
        for order in self:
            if not self.invoice_picking_id:
                pick = {}
                if self.picking_type_id.code == 'outgoing':
                    pick = {
                        'picking_type_id': order.picking_type_id.id,
                        'partner_id': order.responsible.user_id.partner_id.id,
                        'responsible': order.responsible.user_id.partner_id.id,
                        'requested': order.request_raised_for.user_id.partner_id.id,
                        'shipment': True,
                        'origin': order.name,
                        'location_dest_id': order.responsible.address_id.property_stock_customer.id,
                        'location_id': order.picking_type_id.default_location_src_id.id,
                        'move_type': 'direct'
                    }
                picking = self.env['stock.picking'].create(pick)
                self.invoice_picking_id = picking.id
                self.picking_count = len(picking)
                moves = order.product_lines.filtered(lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves(picking)
                move_ids = moves._action_confirm()
                move_ids._action_assign()
                self.write({'state': 'partially_received', 'partial_delivery': True,
                            'ribbon_state': 'partial_stock_delivered', })

    def create_shipped(self):
        product_onhand = []
        req_product = []
        product_type = []
        res = []
        zero_count = 0.00
        non_zero_count = 0.00
        zero_non_zero_count = 0.00
        req_qun_count = 0.00
        for num in self:
            for l in num.product_lines:
                if l.product_type == 'product':
                    product_onhand.append(l.product_available)
                    req_product.append(l.product_uom_qty)
                    product_type.append(l.product_type)
                    print(req_product)
                    print('Product Type', product_type)
                else:
                    self.write({'stock_available': True,
                                'ribbon_state': 'mr_stock_available'})
                for i in product_onhand:
                    if i not in res:
                        res.append(i)
                for product in res:
                    print(product)
                    if product == 0.00:
                        zero_count += 1
                        print('Zero Count', zero_count)
                    if product > 0.00:
                        non_zero_count += 1
                        print('Non Zero Count', non_zero_count)
                for qty in req_product:
                    if qty > product:
                        req_qun_count += 1
                    if non_zero_count and req_qun_count or zero_count and non_zero_count:
                        zero_non_zero_count += 1
                        num.update({
                            'partial_stock_available': True,
                            'ribbon_state': 'partial_stock',
                            'stock_available': False,
                            'tender_raised': False,
                            'rfq_raised': False,
                        })
                    if non_zero_count and zero_non_zero_count == 0.00 or product == qty:
                        if not self.stock_available:
                            num.update({
                                'partial_stock_available': False,
                                'stock_available': True,
                                'ribbon_state': 'mr_stock_available',
                                'tender_raised': False,
                                'rfq_raised': False,
                            })
                        if self.stock_available:
                            num.update({
                                'tender_raised': False,
                            })
            self.write({'enable_ribbon': True})

    def set_approval(self):
        self.write({'state': 'request_approved', 'approved_by': self._uid})

    def open_rfq_form(self):
        action = self.env.ref('material_requisition.open_create_rfq_wizard_action')
        result = action.read()[0]
        order_line = []
        for line in self.product_lines:
            order_line.append({
                'product_id': line.product_id.id,
                'product_qty': line.product_uom_qty,
                'product_uom_id': line.product_uom.id,
                'on_hand_qty': line.product_available,
            })
            result['context'] = {
                'default_material_requisition_ref': self.name,
                'default_order_lines': order_line,
            }
        return result

    def _compute_material_requisition_backorder(self):
        self.material_requisition_backorder_count = self.env['stock.picking'].sudo().search_count(
            [('origin', '=', self.name), ('backorder_id', '!=', False)])

    def _compute_material_requisition_po(self):
        self.purchase_order_count = self.env['purchase.order'].sudo().search_count(
            [('origin', '=', self.name), ('state', '=', 'purchase')])

    # compute method for count total number of purchase order
    def compute_order(self):
        count = 0
        for employee in self:
            invoices = self.env['purchase.order']
            for record in employee.rfq_order_ids:
                if record.state == 'draft':
                    count += 1
            employee.rfq_total = count
            if employee.rfq_total:
                employee.write({'rfq_raised': True, 'ribbon_state': 'rfq_raise'})

    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_ready')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('id', '=', self.invoice_picking_id.id)]
        pick_ids = sum([self.invoice_picking_id.id])
        if pick_ids:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids or False
        return result

    def material_requisition_back_order(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('stock.view_picking_form')
        tree_view = self.sudo().env.ref('stock.vpicktree')
        return {
            'name': _('My Back Order'),
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('origin', '=', self.name), ('backorder_id', '!=', False)],
        }

    def create_RFQ_lines(self):
        return {
            'name': _('Purchase Orders'),
            'domain': [('id', 'in', [x.id for x in self.rfq_order_ids]), ('state', '=', 'draft')],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'view_id': False,
            'views': [(self.env.ref('purchase.purchase_order_kpis_tree').id, 'tree'),
                      (self.env.ref('purchase.purchase_order_form').id, 'form')],
            'type': 'ir.actions.act_window'
        }

    def button_purchase_order(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('purchase.purchase_order_form')
        tree_view = self.sudo().env.ref('purchase.purchase_order_view_tree')
        return {
            'name': _('Purchase Order'),
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('origin', '=', self.name), ('state', '=', 'purchase')],
        }

    def create_material_request(self):
        self.ensure_one()
        if self.automated_sequence:
            name = self.sequence_id.next_by_id()
        else:
            name = self.name
        return {
            "type": "ir.actions.act_window",
            "res_model": "material.requisition.indent",
            "views": [[False, "form"]],
            "context": {
                'form_view_initial_mode': 'edit',
                'default_name': name,
                'default_responsible': self.env.user.id,
                'default_state': 'draft'
            },
        }

    def _compute_request_to_validate_count(self):
        self.request_to_validate_count = self.env['material.requisition.indent'].sudo().search_count(
            [('state', '=', 'to_be_approved'), ('approver1', '=', self.env.user.id)])

    @api.model
    def create(self, values):
        values['name'] = self.sudo().env['ir.sequence'].get('material.requisition.indent') or '/'
        res = super(MaterialRequisitionIndent, self).create(values)
        return res


class IndentProductLines(models.Model):
    _name = 'material.requisition.product.lines'
    _description = 'Indent Product Lines'

    indent_id = fields.Many2one('material.requisition.indent', 'Indent', required=True)
    indent_type = fields.Selection([('new', 'Purchase Indent'), ('existing', 'Repairing Indent')], 'Type')
    product_id = fields.Many2one('product.product', 'Product')
    original_product_id = fields.Many2one('product.product', 'Product to be Repaired')
    product_uom_qty = fields.Float('Quantity Required', digits='Product UoS', default=1)
    product_uom = fields.Many2one('uom.uom', ' Unit of Measure', compute='_compute_product_details')
    product_uos_qty = fields.Float('Quantity (UoS)', digits='Product UoS')
    product_uos = fields.Many2one('uom.uom', 'Product UoS')
    qty_available = fields.Float('In Stock')
    product_available = fields.Float(string='OnHand Qty', related='product_id.qty_available')
    delay = fields.Float('Lead Time')
    qty_shipped = fields.Float('QTY Shipped')
    name = fields.Text('Purpose', required=False)
    specification = fields.Text('Specification')
    # sequence = fields.Datetime('Sequence')
    product_category = fields.Many2one('product.category', string='Product Category', compute='_compute_product_details')
    product_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product'),
    ], string='Product Type', compute='_compute_product_details')

    @api.depends('product_id')
    def _compute_product_details(self):
        for val in self:
            if val.product_id:
                val.product_uom = val.product_id.uom_id.id
                val.product_category = val.product_id.categ_id.id
                val.product_type = val.product_id.type
            else:
                val.product_uom = False
                val.product_category = False
                val.product_type = False

    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            if picking.picking_type_id.code == 'outgoing':
                template = {
                    'name': line.name or '',
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'location_id': picking.picking_type_id.default_location_src_id.id,
                    'location_dest_id': line.indent_id.responsible.address_id.property_stock_customer.id,
                    'picking_id': picking.id,
                    'state': 'draft',
                    'picking_type_id': picking.picking_type_id.id,
                    'route_ids': 1 and [
                        (6, 0, [x.id for x in self.env['stock.route'].search([('id', 'in', (2, 3))])])] or [],
                    'warehouse_id': picking.picking_type_id.warehouse_id.id,
                }
            diff_quantity = line.product_uom_qty
            tmp = template.copy()
            tmp.update({
                'product_uom_qty': diff_quantity,
            })
            template['product_uom_qty'] = diff_quantity
            done += moves.create(template)
        return done


class IndentRequestProductLines(models.Model):
    _name = 'material.requisition.request.product.lines'
    _description = 'Indent Request Product Lines'

    indent_id = fields.Many2one('material.requisition.indent', 'Indent', required=True)
    indent_type = fields.Selection([('new', 'Purchase Indent'), ('existing', 'Repairing Indent')], 'Type')
    product_id = fields.Many2one('product.product', 'Product')
    original_product_id = fields.Many2one('product.product', 'Approved Product')
    product_uom_qty = fields.Float('Quantity Required', digits='Product UoS', default=1)
    approved_product_uom_qty = fields.Float('Quantity Approved', required=True, digits='Product UoS')
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', compute='_compute_product_details')
    approved_product_uom = fields.Many2one('uom.uom', ' Unit of Measure', compute='_compute_original_product_id_details')
    product_uos_qty = fields.Float('Quantity (UoS)', digits='Product UoS')
    product_uos = fields.Many2one('uom.uom', 'Product UoS')
    qty_available = fields.Float('In Stock')
    product_available = fields.Float(string='OnHand Qty', related='product_id.qty_available')
    approved_product_available = fields.Float(string='Approved OnHand Qty',
                                              related='original_product_id.qty_available', )
    delay = fields.Float('Lead Time')
    name = fields.Text('Purpose')
    specification = fields.Text('Specification')
    # sequence = fields.Datetime('Sequence')
    product_category = fields.Many2one('product.category', string='Product Category', compute='_compute_product_details')
    approved_product_category = fields.Many2one('product.category', string='Approved Product Category',
                                                compute='_compute_original_product_id_details')
    product_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product'),
    ], string='Product Type', compute='_compute_product_details')
    approved_product_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product'),
    ], string='Approved Product Type', compute='_compute_original_product_id_details')
    short_close = fields.Boolean('Short Close')

    @api.depends('product_id')
    def _compute_product_details(self):
        for val in self:
            if val.product_id:
                val.product_uom = val.product_id.uom_id.id
                val.product_category = val.product_id.categ_id.id
                val.product_type = val.product_id.type
            else:
                val.product_uom = False
                val.product_category = False
                val.product_type = False

    @api.depends('original_product_id')
    def _compute_original_product_id_details(self):
        for val in self:
            if val.product_id:
                val.approved_product_uom = val.original_product_id.uom_id.id
                val.approved_product_category = val.original_product_id.categ_id.id
                val.approved_product_type = val.original_product_id.type
            else:
                val.approved_product_uom = False
                val.approved_product_category = False
                val.approved_product_type = False
