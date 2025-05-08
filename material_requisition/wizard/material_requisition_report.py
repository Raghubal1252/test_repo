from odoo import models, fields, api, _
import xlwt
from io import BytesIO
import base64
from odoo import tools
from xlwt import easyxf
from datetime import datetime, timedelta

cell = easyxf('pattern: pattern solid, fore_colour yellow')
ADDONS_PATH = tools.config['addons_path'].split(",")[-1]

MONTH_LIST = [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'),
              ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'),
              ('7', 'Jul'), ('8', 'Aug'), ('9', 'Sep'),
              ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec')]


class MaterialRequisitionReport(models.TransientModel):
    _name = 'material.requisition.excel.report.wizard'
    _description = 'Material Requisition Report'

    start_date = fields.Date('Start date', required=True)
    end_date = fields.Date('End date', required=True)
    attachment = fields.Binary('File')
    attach_name = fields.Char('Attachment Name')
    summary_file = fields.Binary('Material Requisition Report')
    file_name = fields.Char('File Name')
    report_printed = fields.Boolean(' Material Requisition Report')
    current_time = fields.Date('Current Time', default=lambda self: fields.Datetime.now())
    ams_time = datetime.now() + timedelta(hours=5, minutes=30)
    date = ams_time.strftime('%d-%m-%Y %H:%M:%S')
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    material_request_raised_for = fields.Many2many('hr.employee', string='Request Raised For')
    material_request_raised_by = fields.Many2one('hr.employee', string='Request Raised By')
    requested = fields.Boolean('Request..?')

    def action_get_material_requisiton_report_excel(self):
        workbook = xlwt.Workbook()
        worksheet1 = workbook.add_sheet('Material Requisition Report')

        design_6 = easyxf('align: horiz left;font: bold 1;')
        design_7 = easyxf('align: horiz center;font: bold 1;')
        design_8 = easyxf('align: horiz left;')
        design_9 = easyxf('align: horiz right;')
        design_10 = easyxf('align: horiz right; pattern: pattern solid, fore_colour red;')
        design_11 = easyxf('align: horiz right; pattern: pattern solid, fore_colour green;')
        design_12 = easyxf('align: horiz right; pattern: pattern solid, fore_colour gray25;')
        design_13 = easyxf('align: horiz center;font: bold 1;pattern: pattern solid, fore_colour gray25;')

        worksheet1.col(0).width = 1500
        worksheet1.col(1).width = 5500
        worksheet1.col(2).width = 6500
        worksheet1.col(3).width = 6500
        worksheet1.col(4).width = 5800
        worksheet1.col(5).width = 3800
        worksheet1.col(6).width = 3800
        worksheet1.col(7).width = 3800
        worksheet1.col(8).width = 3500
        worksheet1.col(9).width = 3500
        worksheet1.col(10).width = 3500
        worksheet1.col(11).width = 3300
        worksheet1.col(12).width = 4500
        worksheet1.col(13).width = 4500
        worksheet1.col(14).width = 4500
        worksheet1.col(15).width = 4000

        rows = 0
        cols = 0
        row_pq = 5

        worksheet1.set_panes_frozen(True)
        worksheet1.set_horz_split_pos(rows + 1)
        worksheet1.set_remove_splits(True)

        col_1 = 0
        worksheet1.write_merge(rows, rows, 2, 6, 'MATERIAL REQUISITION REPORT', design_13)
        rows += 1
        worksheet1.write(rows, 3, 'FROM', design_7)
        worksheet1.write(rows, 4, self.start_date.strftime('%d-%m-%Y'), design_7)
        rows += 1
        worksheet1.write(rows, 3, 'TO', design_7)
        worksheet1.write(rows, 4, self.end_date.strftime('%d-%m-%Y'), design_7)
        rows += 2
        if self.material_request_raised_by:
            worksheet1.write(rows, 3, 'MATERIAL REQUESTED BY', design_7)
            worksheet1.write(rows, 4, self.material_request_raised_by.name, design_7)
            rows += 1
        worksheet1.write(rows, col_1, _('Sl.No'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Requested Material No'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Requested Material For'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Department'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Requested Material  Name'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Requested Date'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Requested  QTY'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Approved QTY'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Approved Date'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Inward Date'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Issued Date'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Issued QTY'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('MR Approved By'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Stores Incharge'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Status'), design_13)
        col_1 += 1

        sl_no = 1
        row_pq += 1
        for record in self:
            domain09 = [
                ('indent_date', '>=', record.start_date),
                ('required_date', '<=', record.end_date),
                ('responsible', '=', record.material_request_raised_by.name),
                ('request_raised_for', '=', record.material_request_raised_for.ids),
                ('state', 'not in', ('draft', 'cancel', 'reject'))]
            domain10 = [
                ('indent_date', '>=', record.start_date),
                ('required_date', '<=', record.end_date),
                ('state', 'not in', ('draft', 'cancel', 'reject'))]
            domain11 = [
                ('indent_date', '>=', record.start_date),
                ('required_date', '<=', record.end_date),
                ('responsible', '=', record.material_request_raised_by.name),
                ('state', 'not in', ('draft', 'cancel', 'reject'))]
            domain12 = [
                ('indent_date', '>=', record.start_date),
                ('required_date', '<=', record.end_date),
                ('request_raised_for', '=', record.material_request_raised_for.ids),
                ('state', 'not in', ('draft', 'cancel', 'reject'))]
            domain2 = [
                ('scheduled_date', '>=', record.end_date),
                ('state', 'not in', ('draft', 'waiting', 'confirmed', 'assigned', 'cancel'))]
            picking = record.env['stock.picking'].sudo().search(domain2)
            row_pq_new = 0
            if record.start_date and record.end_date and record.material_request_raised_for and record.material_request_raised_by:
                material = record.env['material.requisition.indent'].sudo().search(domain09)
                for indent in material:
                    ref_date1 = indent.indent_date
                    updated_date = indent.required_date
                    verified_date = indent.verified_date
                    issued_date = indent.issued_date
                    import datetime
                    if ref_date1:
                        d11 = str(ref_date1)
                        dt21 = datetime.datetime.strptime(d11, '%Y-%m-%d %H:%M:%S')
                        date1 = dt21.strftime("%d/%m/%Y")
                    if updated_date:
                        d22 = str(updated_date)
                        dt22 = datetime.datetime.strptime(d22, '%Y-%m-%d %H:%M:%S')
                        indent_updated_date = dt22.strftime("%d/%m/%Y")
                    if verified_date:
                        d33 = str(verified_date)
                        dt23 = datetime.datetime.strptime(d33, '%Y-%m-%d %H:%M:%S')
                        verified_date = dt23.strftime("%d/%m/%Y")
                    if indent.inward_date:
                        d44 = str(indent.inward_date)
                        dt24 = datetime.datetime.strptime(d44, '%Y-%m-%d %H:%M:%S')
                        inward_date = dt24.strftime("%d/%m/%Y")
                    if indent.issued_date:
                        d55 = str(indent.issued_date)
                        d55 = (d55.split("."))[0]
                        dt25 = datetime.datetime.strptime(d55, '%Y-%m-%d %H:%M:%S')
                        issued_date = dt25.strftime("%d/%m/%Y")
                    worksheet1.write(row_pq, 0, sl_no, design_8)
                    if indent.name:
                        worksheet1.write(row_pq, 1, indent.name, design_8)
                    else:
                        worksheet1.write(row_pq, 1, '-', design_8)
                    if indent.request_raised_for.name:
                        worksheet1.write(row_pq, 2, indent.request_raised_for.name, design_8)
                    else:
                        worksheet1.write(row_pq, 2, '-', design_8)
                    if indent.request_raised_for.department_id.name:
                        worksheet1.write(row_pq, 3, indent.request_raised_for.department_id.name, design_8)
                    else:
                        worksheet1.write(row_pq, 3, '-', design_8)
                    if ref_date1:
                        worksheet1.write(row_pq, 5, date1, design_8)
                    else:
                        worksheet1.write(row_pq, 5, '-', design_8)
                    if indent.verified_date:
                        worksheet1.write(row_pq, 8, verified_date, design_8)
                    else:
                        worksheet1.write(row_pq, 8, '-', design_8)
                    if indent.inward_date:
                        worksheet1.write(row_pq, 9, inward_date, design_8)
                    else:
                        worksheet1.write(row_pq, 9, '-', design_8)
                    if indent.issued_date:
                        worksheet1.write(row_pq, 10, issued_date, design_8)
                    else:
                        worksheet1.write(row_pq, 10, '-', design_8)
                    if indent.approved_by:
                        worksheet1.write(row_pq, 12, indent.approved_by.name, design_8)
                    else:
                        worksheet1.write(row_pq, 12, '-', design_8)
                    if indent.store_incharge:
                        worksheet1.write(row_pq, 13, indent.store_incharge, design_8)
                    else:
                        worksheet1.write(row_pq, 13, '-', design_8)
                    worksheet1.write(row_pq, 14, (dict(indent._fields['state'].selection).get(indent.state)), design_8)
                    row_pq_new = row_pq
                    for material in indent.request_product_lines:
                        worksheet1.write(row_pq_new, 4, material.product_id.name, design_8)
                        worksheet1.write(row_pq_new, 6, material.product_uom_qty, design_9)
                        row_pq_new += 1
                    row_pq_new = row_pq
                    for material_approved in indent.product_lines:
                        worksheet1.write(row_pq_new, 11, '%.2f' % material_approved.qty_shipped, design_8)
                        worksheet1.write(row_pq_new, 7, material_approved.product_uom_qty, design_9)
                        row_pq_new += 1
                    sl_no += 1
                    row_pq = row_pq_new
            elif record.start_date and record.end_date and record.material_request_raised_for:
                material = record.env['material.requisition.indent'].sudo().search(domain12)
                for indent in material:
                    ref_date1 = indent.indent_date
                    updated_date = indent.required_date
                    verified_date = indent.verified_date
                    issued_date = indent.issued_date
                    import datetime
                    if ref_date1:
                        d11 = str(ref_date1)
                        dt21 = datetime.datetime.strptime(d11, '%Y-%m-%d %H:%M:%S')
                        date1 = dt21.strftime("%d/%m/%Y")
                    if updated_date:
                        d22 = str(updated_date)
                        dt22 = datetime.datetime.strptime(d22, '%Y-%m-%d %H:%M:%S')
                        indent_updated_date = dt22.strftime("%d/%m/%Y")
                    if verified_date:
                        d33 = str(verified_date)
                        dt23 = datetime.datetime.strptime(d33, '%Y-%m-%d %H:%M:%S')
                        verified_date = dt23.strftime("%d/%m/%Y")
                    if indent.inward_date:
                        d44 = str(indent.inward_date)
                        dt24 = datetime.datetime.strptime(d44, '%Y-%m-%d %H:%M:%S')
                        inward_date = dt24.strftime("%d/%m/%Y")
                    if indent.issued_date:
                        d55 = str(indent.issued_date)
                        d55 = (d55.split("."))[0]
                        dt25 = datetime.datetime.strptime(d55, '%Y-%m-%d %H:%M:%S')
                        issued_date = dt25.strftime("%d/%m/%Y")
                    worksheet1.write(row_pq, 0, sl_no, design_8)
                    if indent.name:
                        worksheet1.write(row_pq, 1, indent.name, design_8)
                    else:
                        worksheet1.write(row_pq, 1, '-', design_8)
                    if indent.request_raised_for.name:
                        worksheet1.write(row_pq, 2, indent.request_raised_for.name, design_8)
                    else:
                        worksheet1.write(row_pq, 2, '-', design_8)
                    if indent.request_raised_for.department_id.name:
                        worksheet1.write(row_pq, 3, indent.request_raised_for.department_id.name, design_8)
                    else:
                        worksheet1.write(row_pq, 3, '-', design_8)
                    if ref_date1:
                        worksheet1.write(row_pq, 5, date1, design_8)
                    else:
                        worksheet1.write(row_pq, 5, '-', design_8)
                    if indent.verified_date:
                        worksheet1.write(row_pq, 8, verified_date, design_8)
                    else:
                        worksheet1.write(row_pq, 8, '-', design_8)
                    if indent.inward_date:
                        worksheet1.write(row_pq, 9, inward_date, design_8)
                    else:
                        worksheet1.write(row_pq, 9, '-', design_8)
                    if indent.issued_date:
                        worksheet1.write(row_pq, 10, issued_date, design_8)
                    else:
                        worksheet1.write(row_pq, 10, '-', design_8)
                    if indent.approved_by:
                        worksheet1.write(row_pq, 12, indent.approved_by.name, design_8)
                    else:
                        worksheet1.write(row_pq, 12, '-', design_8)
                    if indent.store_incharge:
                        worksheet1.write(row_pq, 13, indent.store_incharge, design_8)
                    else:
                        worksheet1.write(row_pq, 13, '-', design_8)
                    worksheet1.write(row_pq, 14, (dict(indent._fields['state'].selection).get(indent.state)), design_8)
                    row_pq_new = row_pq
                    for material in indent.request_product_lines:
                        worksheet1.write(row_pq_new, 4, material.product_id.name, design_8)
                        worksheet1.write(row_pq_new, 6, material.product_uom_qty, design_9)
                        row_pq_new += 1
                    row_pq_new = row_pq
                    for material_approved in indent.product_lines:
                        worksheet1.write(row_pq_new, 11, '%.2f' % material_approved.qty_shipped, design_8)
                        worksheet1.write(row_pq_new, 7, material_approved.product_uom_qty, design_9)
                        row_pq_new += 1
                    sl_no += 1
                    row_pq = row_pq_new
            elif record.start_date and record.end_date and record.material_request_raised_by:
                material = record.env['material.requisition.indent'].sudo().search(domain11)
                for indent in material:
                    ref_date1 = indent.indent_date
                    updated_date = indent.required_date
                    verified_date = indent.verified_date
                    issued_date = indent.issued_date
                    import datetime
                    if ref_date1:
                        d11 = str(ref_date1)
                        dt21 = datetime.datetime.strptime(d11, '%Y-%m-%d %H:%M:%S')
                        date1 = dt21.strftime("%d/%m/%Y")
                    if updated_date:
                        d22 = str(updated_date)
                        dt22 = datetime.datetime.strptime(d22, '%Y-%m-%d %H:%M:%S')
                        indent_updated_date = dt22.strftime("%d/%m/%Y")
                    if verified_date:
                        d33 = str(verified_date)
                        dt23 = datetime.datetime.strptime(d33, '%Y-%m-%d %H:%M:%S')
                        verified_date = dt23.strftime("%d/%m/%Y")
                    if indent.inward_date:
                        d44 = str(indent.inward_date)
                        dt24 = datetime.datetime.strptime(d44, '%Y-%m-%d %H:%M:%S')
                        inward_date = dt24.strftime("%d/%m/%Y")
                    if indent.issued_date:
                        d55 = str(indent.issued_date)
                        d55 = (d55.split("."))[0]
                        dt25 = datetime.datetime.strptime(d55, '%Y-%m-%d %H:%M:%S')
                        issued_date = dt25.strftime("%d/%m/%Y")
                    worksheet1.write(row_pq, 0, sl_no, design_8)
                    if indent.name:
                        worksheet1.write(row_pq, 1, indent.name, design_8)
                    else:
                        worksheet1.write(row_pq, 1, '-', design_8)
                    if indent.request_raised_for.name:
                        worksheet1.write(row_pq, 2, indent.request_raised_for.name, design_8)
                    else:
                        worksheet1.write(row_pq, 2, '-', design_8)
                    if indent.request_raised_for.department_id.name:
                        worksheet1.write(row_pq, 3, indent.request_raised_for.department_id.name, design_8)
                    else:
                        worksheet1.write(row_pq, 3, '-', design_8)
                    if ref_date1:
                        worksheet1.write(row_pq, 5, date1, design_8)
                    else:
                        worksheet1.write(row_pq, 5, '-', design_8)
                    if indent.verified_date:
                        worksheet1.write(row_pq, 8, verified_date, design_8)
                    else:
                        worksheet1.write(row_pq, 8, '-', design_8)
                    if indent.inward_date:
                        worksheet1.write(row_pq, 9, inward_date, design_8)
                    else:
                        worksheet1.write(row_pq, 9, '-', design_8)
                    if indent.issued_date:
                        worksheet1.write(row_pq, 10, issued_date, design_8)
                    else:
                        worksheet1.write(row_pq, 10, '-', design_8)
                    if indent.approved_by:
                        worksheet1.write(row_pq, 12, indent.approved_by.name, design_8)
                    else:
                        worksheet1.write(row_pq, 12, '-', design_8)
                    if indent.store_incharge:
                        worksheet1.write(row_pq, 13, indent.store_incharge, design_8)
                    else:
                        worksheet1.write(row_pq, 13, '-', design_8)
                    worksheet1.write(row_pq, 14, (dict(indent._fields['state'].selection).get(indent.state)), design_8)
                    row_pq_new = row_pq
                    for material in indent.request_product_lines:
                        worksheet1.write(row_pq_new, 4, material.product_id.name, design_8)
                        worksheet1.write(row_pq_new, 6, material.product_uom_qty, design_9)
                        row_pq_new += 1
                    row_pq_new = row_pq
                    for material_approved in indent.product_lines:
                        worksheet1.write(row_pq_new, 11, '%.2f' % material_approved.qty_shipped, design_8)
                        worksheet1.write(row_pq_new, 7, material_approved.product_uom_qty, design_9)
                        row_pq_new += 1
                    sl_no += 1
                    row_pq = row_pq_new
            else:
                material = record.env['material.requisition.indent'].sudo().search(domain10)
                for indent in material:
                    ref_date1 = indent.indent_date
                    updated_date = indent.required_date
                    verified_date = indent.verified_date
                    issued_date = indent.issued_date
                    import datetime
                    if ref_date1:
                        d11 = str(ref_date1)
                        dt21 = datetime.datetime.strptime(d11, '%Y-%m-%d %H:%M:%S')
                        date1 = dt21.strftime("%d/%m/%Y")
                    if updated_date:
                        d22 = str(updated_date)
                        dt22 = datetime.datetime.strptime(d22, '%Y-%m-%d %H:%M:%S')
                        indent_updated_date = dt22.strftime("%d/%m/%Y")
                    if verified_date:
                        d33 = str(verified_date)
                        dt23 = datetime.datetime.strptime(d33, '%Y-%m-%d %H:%M:%S')
                        verified_date = dt23.strftime("%d/%m/%Y")
                    if indent.inward_date:
                        d44 = str(indent.inward_date)
                        dt24 = datetime.datetime.strptime(d44, '%Y-%m-%d %H:%M:%S')
                        inward_date = dt24.strftime("%d/%m/%Y")
                    if indent.issued_date:
                        d55 = str(indent.issued_date)
                        d55 = (d55.split("."))[0]
                        dt25 = datetime.datetime.strptime(d55, '%Y-%m-%d %H:%M:%S')
                        issued_date = dt25.strftime("%d/%m/%Y")
                    worksheet1.write(row_pq, 0, sl_no, design_8)
                    if indent.name:
                        worksheet1.write(row_pq, 1, indent.name, design_8)
                    else:
                        worksheet1.write(row_pq, 1, '-', design_8)
                    if indent.request_raised_for.name:
                        worksheet1.write(row_pq, 2, indent.request_raised_for.name, design_8)
                    else:
                        worksheet1.write(row_pq, 2, '-', design_8)
                    if indent.request_raised_for.department_id.name:
                        worksheet1.write(row_pq, 3, indent.request_raised_for.department_id.name, design_8)
                    else:
                        worksheet1.write(row_pq, 3, '-', design_8)
                    if ref_date1:
                        worksheet1.write(row_pq, 5, date1, design_8)
                    else:
                        worksheet1.write(row_pq, 5, '-', design_8)
                    if indent.verified_date:
                        worksheet1.write(row_pq, 8, verified_date, design_8)
                    else:
                        worksheet1.write(row_pq, 8, '-', design_8)
                    if indent.inward_date:
                        worksheet1.write(row_pq, 9, inward_date, design_8)
                    else:
                        worksheet1.write(row_pq, 9, '-', design_8)
                    if indent.issued_date:
                        worksheet1.write(row_pq, 10, issued_date, design_8)
                    else:
                        worksheet1.write(row_pq, 10, '-', design_8)
                    if indent.approved_by:
                        worksheet1.write(row_pq, 12, indent.approved_by.name, design_8)
                    else:
                        worksheet1.write(row_pq, 12, '-', design_8)
                    if indent.store_incharge:
                        worksheet1.write(row_pq, 13, indent.store_incharge, design_8)
                    else:
                        worksheet1.write(row_pq, 13, '-', design_8)
                    worksheet1.write(row_pq, 14, (dict(indent._fields['state'].selection).get(indent.state)), design_8)
                    row_pq_new = row_pq
                    for material in indent.request_product_lines:
                        worksheet1.write(row_pq_new, 4, material.product_id.name, design_8)
                        worksheet1.write(row_pq_new, 6, material.product_uom_qty, design_9)
                        row_pq_new += 1
                    row_pq_new = row_pq
                    for material_approved in indent.product_lines:
                        worksheet1.write(row_pq_new, 11, '%.2f' % material_approved.qty_shipped, design_8)
                        worksheet1.write(row_pq_new, 7, material_approved.product_uom_qty, design_9)
                        row_pq_new += 1
                    sl_no += 1
                    row_pq = row_pq_new
        fp = BytesIO()
        o = workbook.save(fp)
        fp.read()
        excel_file = base64.b64encode(fp.getvalue())
        self.write({'summary_file': excel_file, 'file_name': 'Material Requisition Report - [ %s ].xls' % self.date,
                    'report_printed': True})
        fp.close()
        return {
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'material.requisition.excel.report.wizard',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }
