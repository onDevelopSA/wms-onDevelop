# © 2020 onDevelop.sa
# Autor: Idelis Gé Ramírez

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Stock Picking'
    
    picking_type_code = fields.Selection(related='picking_type_id.code',
                                         store=True)
    is_suborder = fields.Boolean()
    parent_pick_id = fields.Many2one('stock.picking')
    suborders_ids = fields.One2many('stock.picking', 'parent_pick_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('distributed', 'Distributed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True,
                             track_visibility='onchange',
                             help=" * Draft: not confirmed yet and will not be scheduled until confirmed.\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows).\n"
             " * Waiting: if it is not ready to be sent because the required products could not be reserved.\n"
             " * Ready: products are reserved and ready to be sent. If the shipping policy is 'As soon as possible' this happens as soon as anything is reserved.\n"
             " * Done: has been processed, can't be modified or cancelled anymore.\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore.")

    def _update_quants(self, src_location, dest_location, product, product_qty):
        '''Pass the product quantity reserved by default in some location to
        the new location selected by the user.
        (default behavior): location A1 .. reserved 1 unit
        (change the location to A2): location A1 .. reserved 0 unit
                                     location A2 .. reserved 1 unit

        '''
        StockQuant = self.env['stock.quant']
        src_quant = StockQuant.search([('location_id', '=', src_location.id),
                                       ('product_id', '=', product.id)])
        dest_quant = StockQuant.search([('location_id', '=', dest_location.id),
                                        ('product_id', '=', product.id)])
        if (src_quant and dest_quant) and (dest_quant != src_quant):
            # This is the right way but the ORM throw a wrong error when try
            # to update the unreserved amount of the product, so is necessary
            # use an sql query.
            #dest_quant.reserved_quantity += product_qty
            # src_quant.reserved_quantity -= product_qty

            reserved_dest = dest_quant.reserved_quantity + product_qty
            reserved_src = src_quant.reserved_quantity - product_qty
            update_quant_query = '''
            UPDATE
                stock_quant
            SET
                reserved_quantity = {reserved_quantity}
            WHERE id = {q_id};

            '''
            self.env.cr.execute(update_quant_query.format(
                reserved_quantity=reserved_src, q_id=src_quant.id))
            self.env.cr.execute(update_quant_query.format(
                reserved_quantity=reserved_dest, q_id=dest_quant.id))

    @api.onchange('move_lines')
    def onchange_move_lines(self):
        '''Update the stock.move.line location using the selected location
        in the stock.move, also must to update the reserved quantities of the
        locations.

        '''
        for move in self.move_lines:
            if (move.zone_location_info_ids
                and not move.zone_location_info_ids.is_default):
                new_location = move.zone_location_info_ids.location_id
                for stock_move_line in move.move_line_ids:
                    self._update_quants(stock_move_line.location_id,
                                        new_location,
                                        move.product_id,
                                        stock_move_line.product_qty)
                    stock_move_line.write({'location_id' : new_location.id})

    @api.multi
    def button_validate(self):
        '''Check if all the suborders have state done and update the parent
        pick order state to done if.

        '''
        not_complete = False
        for suborders in self.parent_pick_id.suborders_ids:
            if (suborders.state != 'done' and suborders.id != self.id):
                not_complete = True
        if not not_complete:
            self.parent_pick_id.write({'state' : 'done'})
        return super(StockPicking, self).button_validate()

    def get_internal_transfers_view(self):
        '''Return all the internal transfers related with the current RMA
        operation.

        '''
        action = self.env.ref(
            'stock.stock_picking_action_picking_type').read()[0]
        action['views'] = [
            (self.env.ref('stock.vpicktree').id, 'tree'),
            (self.env.ref('stock.view_picking_form').id, 'form'),
        ]
        action['context'] = self.env.context
        action['domain'] = [('parent_pick_id', 'in', [self.id])]
        return {
            'name': 'Suborders',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'target': 'current',
            'views': [(self.env.ref('stock.vpicktree').id, 'tree'),
                      (self.env.ref('stock.view_picking_form').id, 'form')],
            'domain': [('parent_pick_id', 'in', [self.id])],
            'context': {}}

    @api.multi
    def distribute_order(self):
        '''Call the wizard who permit distribute the order in suborders.'''
        return {'name': _('Confirm Distributon ?'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'distribute.order',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'current_pick_id': self.id}}
