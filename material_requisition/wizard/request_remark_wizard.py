from odoo import api, fields, models, _
from datetime import datetime, date


class MaterialRequisitionApproveRemarks(models.TransientModel):
    _name = 'material.requisition.approve.remarks'
    _description = 'Material Requisition Approve Remarks'
    _inherit = ['mail.thread']

    remarks = fields.Text('Remarks')
    is_default_remark = fields.Boolean('Enable Default Remark')
    default_remark = fields.Text('Default Remark',
                                 default='Requisition Approval get confirmed Without Remarks')

    @api.onchange("is_default_remark")
    def _onchange_is_default_remark(self):
        for val in self:
            if val.is_default_remark:
                val.remarks = val.default_remark
            else:
                val.remarks = ''

    def tick_ok(self):
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['material.requisition.indent'].search([('id', '=', applicant_id)])
        today = date.today()
        current_date = today.strftime("%d/%m/%Y")
        current_user = self.env.user.name

        if active_id.state == 'to_be_approved':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_approval()
            active_id.write({'approver1_approve_reason': text})
        elif active_id.state == 'leader_approval':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_approval()
            active_id.write({'approver2_approve_reason': text})
        elif active_id.state == 'manager_approval':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_approval()
            active_id.write({'approver3_approve_reason': text})
        elif active_id.state == 'director_approval':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_approval()
            active_id.write({'approver4_approve_reason': text})
        elif active_id.state == 'ceo_approval':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_approval()
            active_id.write({'approver5_approve_reason': text})
        return True


class MaterialRequisitionRejectRemarks(models.TransientModel):
    _name = 'material.requisition.reject.remarks'
    _description = 'Material Requisition Reject Remarks'
    _inherit = ['mail.thread']

    remarks = fields.Text('Remarks')

    def tick_ok(self):
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['material.requisition.indent'].search([('id', '=', applicant_id)])
        today = date.today()
        current_date = today.strftime("%d/%m/%Y")
        current_user = self.env.user.name

        if active_id.state == 'to_be_approved':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_rejection()
            active_id.write({'approver1_reject_reason': text})
        elif active_id.state == 'leader_approval':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_rejection()
            active_id.write({'approver2_reject_reason': text})
        elif active_id.state == 'manager_approval':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_rejection()
            active_id.write({'approver3_reject_reason': text})
        elif active_id.state == 'director_approval':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_rejection()
            active_id.write({'approver4_reject_reason': text})
        elif active_id.state == 'ceo_approval':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_rejection()
            active_id.write({'approver5_reject_reason': text})


class MaterialRequisitionCancelRemarks(models.TransientModel):
    _name = 'material.requisition.cancel.remarks'
    _description = 'Material Requisition Cancel Remarks'
    _inherit = ['mail.thread']

    remarks = fields.Text('Remarks')

    def tick_ok(self):
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['material.requisition.indent'].search([('id', '=', applicant_id)])
        today = date.today()
        current_date = today.strftime("%d/%m/%Y")
        current_user = self.env.user.name

        if active_id.state == 'to_be_approved':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_cancellation()
            active_id.write({'approver1_cancel_reason': text})
        elif active_id.state == 'leader_approval':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_cancellation()
            active_id.write({'approver2_cancel_reason': text})
        elif active_id.state == 'manager_approval':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_cancellation()
            active_id.write({'approver3_cancel_reason': text})
        elif active_id.state == 'director_approval':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_cancellation()
            active_id.write({'approver4_cancel_reason': text})
        elif active_id.state == 'ceo_approval':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.apply_cancellation()
            active_id.write({'approver5_cancel_reason': text})
        return True

