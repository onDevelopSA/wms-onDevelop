# -*- coding: utf-8 -*-
# © 2019 Open System Network
# Autor: Idelis Gé Ramírez

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError


class StockMoveLine(models.TransientModel):
    '''This is necessary for extend the stock.move.line class.
    TODO:DOCUMENT

    '''
    _name = 'stock.move_line'
    _inherit = 'stock.move.line'

    @api.depends('location_id')
    def _get_emplyee(self):
        pass

    @api.multi
    @api.depends('distribution_id', 'location_id')
    def _get_stock_zone(self):
        for rec in self:
            rec.stock_zone_id = rec.location_id.zone_id
            if not rec.employee_id:
                rec.employee_id = rec.location_id.zone_id.employee_id

    distribution_id = fields.Many2one('distribute.order')
    stock_zone_id = fields.Many2one('stock.zone',
                                    compute='_get_stock_zone', store=True)
    employee_id = fields.Many2one('res.partner', default=_get_emplyee,
                                  store=True)

class DistributeOrder(models.TransientModel):
    _name = 'distribute.order'
    _description = 'Distribute Order'

    def _get_sub_lines(self):
        '''TODO:DOCUMENT'''        
        StockPicking = self.env['stock.picking']
        pick = StockPicking.search([
                ('id', '=', self._context.get('current_pick_id'))])
        if pick:
            StockPickingLine = self.env['stock.move.line']
            lines = StockPickingLine.search([('picking_id', '=', pick.id)])
            if lines:
                return [(6, 0, lines.ids)]
            return []

    subord_ids = fields.One2many('stock.move_line', 'distribution_id',
                                 default=_get_sub_lines, store=True,
                                 readonly=False)
    partner_msg = fields.Char()
    pick_id = fields.Many2one('stock.picking')

    def transfer_pick(self):
        ''' Used for update the context and set confirmed. '''
        StockPicking = self.env['stock.picking']
        pick = StockPicking.search([
                ('id', '=', self._context.get('current_pick_id'))])
        if pick:
            self.pick_id = pick
        for popup_line in self.subord_ids:
            if not popup_line.employee_id:
                msg_error = 'Who is the employee to get the product\
                : {p} ??'.format(p=popup_line.product_id.name)
                raise UserError(_(msg_error))
        # use itertools.groupby for group by employee:
        # employee 7, line 1 ... employee 7 , line 4 ... employee 4, line 3
        import itertools
        employee_line = [(l.employee_id.id, l) for l in self.subord_ids]
        employee_iterator = itertools.groupby(employee_line, lambda x : x[0])

        for employee_id, group in employee_iterator:
            stock_move_line = [] # this array have the stock.move.line (s)
            # Nothing special everybody = False
            move_date = move_location_id = move_location_dest_id = False
            move_product_id = move_product_uom_id = False

            print('*********' * 10)
            print('el empleado {k}'.format(k=employee_id))
            stock_move = []
            for line in group:
                stock_move_line = []
                # line have .. eg: (3, stock.move_line(9,))..(employee,move)
                move = line[1]
                stock_move_line.append((0, 0, {
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_uom_id.id,
                    'location_id': move.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                    'qty_done': move.qty_done,
                    'product_uom_qty': move.product_uom_qty,
                    'lot_id': move.lot_id.id,
                    'package_id': move.package_id.id,
                    'owner_id': move.owner_id.id}))
                stock_move.append(
                    (0, 0, {'additional': False,
                            'move_line_ids': stock_move_line,
                            'date_expected': move.date,
                            'location_dest_id': move.location_dest_id.id,
                            'location_id': move.location_id.id,
                            'name': 'eggs',                            
                            'zone_location_info_ids':
                            move.move_id.zone_location_info_ids.id,
                            'picking_type_id': pick.picking_type_id.id,
                            'product_id': move.product_id.id,
                            'product_uom': move.product_uom_id.id,
                            'product_uom_qty': move.product_uom_qty,
                            'state': 'draft'}))
            vals = {'_barcode_scanned': False,
                    'company_id': self.env.user.company_id.id,
                    'is_locked': pick.is_locked,
                    'is_suborder': True,
                    'location_dest_id': pick.location_dest_id.id,
                    'location_id': pick.location_id.id,
                    'move_lines': stock_move,
                    'move_type': pick.move_type,
                    'note': pick.note,
                    'origin': pick.name,
                    'owner_id': employee_id,
                    'partner_id': pick.partner_id.id,
                    'picking_type_id': pick.picking_type_id.id,
                    'parent_pick_id' : pick.id,
                    'priority': pick.priority}
            new_pick = StockPicking.create(vals)
            '''This is because the stock.pick have a relationship directly
            with the stock.move.line then is necessary update the field
            move_line_ids with all the stock_move_lines.  when the user try
            to validate the suborder odoo throw an exception.
            '''
            move_line_ids = []
            for m in new_pick.move_lines:
                move_line_ids += m.move_line_ids.ids
            new_pick.move_line_ids = [(6, 0, move_line_ids)]
        pick.write({'state': 'distributed'})


            
            
            # for empl, line in list(group):
            #     print('*********' * 10)
            #     print(employee)
            #     print(empl)
            #     print(line)
            
        # import ipdb; ipdb.set_trace() # REMOVE THIS
        # assert False, 'cabeza en la acera ..'            
        
        
            #     line_dict = {'product_id': line.product_id.id,
            #                  'product_uom_id': line.product_uom_id.id,
            #                  'location_id': line.location_id.id,
            #                  'location_dest_id': line.location_dest_id.id,
            #                  'qty_done': line.qty_done,
            #                  'product_uom_qty': line.product_uom_qty,
            #                  'lot_id': line.lot_id.id,
            #                  'package_id': line.package_id.id,
            #                  'owner_id': line.owner_id.id}
            #     stock_move_line.append((0, 0, line_dict))
            #     move_date = line.date
            #     move_location_dest_id = line.location_dest_id.id
            #     move_location_id = line.location_id.id
            #     move_product_id = line.product_id.id
            #     move_product_uom_id = line.product_uom_id.id
            # stock_move = []
            # stock_move.append(
            #         (0, 0, {'additional': False,
            #                 'move_line_ids': stock_move_line,
            #                 'date_expected': move_date,
            #                 'location_dest_id': move_location_dest_id,
            #                 'location_id': move_location_id,
            #                 'name': 'eggs',
            #                 'picking_type_id': pick.picking_type_id.id,
            #                 'product_id': move_product_id,
            #                 'product_uom': move_product_uom_id,
            #                 'state': 'draft'}))
            # vals = {'_barcode_scanned': False,
            #         'company_id': self.env.user.company_id.id,
            #         'is_locked': pick.is_locked,
            #         'is_suborder': True,
            #         'location_dest_id': pick.location_dest_id.id,
            #         'location_id': pick.location_id.id,
            #         'move_lines': stock_move,
            #         'move_type': pick.move_type,
            #         'note': pick.note,
            #         'origin': str(line.product_id.name),
            #         'owner_id': employee,
            #         'partner_id': pick.partner_id.id,
            #         'picking_type_id': pick.picking_type_id.id,
            #         'parent_pick_id' : pick.id,
            #         'priority': pick.priority}
            # new_pick = StockPicking.create(vals)
        return True
