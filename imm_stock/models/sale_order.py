# © 2020 onDevelop.sa
# Autor: Idelis Gé Ramírez

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    zone_loca_info_ids = fields.One2many('zone.location.info', 'so_line_id')


class ZoneLocationInfo(models.Model):
    
    _name = 'zone.location.info'
    _rec_name = 'location_name'
    
    location_name = fields.Char(related='location_id.name', store=True)
    rest_info = fields.Char()
    is_default = fields.Boolean()
    so_line_id = fields.Many2one('sale.order.line')
    zone_id = fields.Many2one('stock.zone')
    location_id = fields.Many2one('stock.location')
    location_priority = fields.Integer()


class SaleOrder(models.Model):
    '''Store the minimal quantity of a specific product in specific
    location.

    '''
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        '''TODO:DOCUMENT'''

        ZoneLocInfo = self.env['zone.location.info']
        # this store the location, route to use like default.
        def update_move_itself(move, so_line_id):
            '''Create the default zone info using the first location
            selected by odoo.
            Also return the employee who must to attend this delivery order.

            '''
            employee = False
            if move.move_line_ids:
                line = move.move_line_ids[0]
                zinfo = ZoneLocInfo.create(
                    {'location_id' : line.location_id.id,
                     'zone_id': line.location_id.zone_id.id,
                     'is_default': True,
                     'so_line_id' : so_line_id})
                move.zone_location_info_ids = zinfo.id
                if zinfo.zone_id.employee_id:
                    employee = zinfo.zone_id.employee_id.id
            return employee

        def check_prod_disponibility(localization_id, needed_qty, prod_id,
                                     minimal_qty):
            '''Use the minimum quantity defined in the stock location and
            check if this location can supply the delivery.

            '''
            StockQuant= self.env['stock.quant']
            stock_quant = StockQuant.search([
                ('location_id', '=', localization_id),
                ('product_id', '=', prod_id)])
            available = (stock_quant.quantity - stock_quant.reserved_quantity)
            available -= minimal_qty
            return available >= needed_qty

        possible_owners = set()
        def get_better_location(so_line, stock_move, needed_qty):
            '''Update the stock.move.line location_id field if is necessary.
            Find the best location using the minimal product quantity and 
            the stock.move.line quantity (sold quantity).

            '''
            # buscar las localizaciones para el almacen de la venta de tipo
            # internal
            StockLocation = self.env['stock.location']
            location_and_route = False
            countt = 0
            for zone in self.warehouse_id.zone_ids:
                for zone_line in zone.line_ids:
                    ProductLocationQ = self.env['product.location.quant']
                    search_domain = [
                        ('location_id', '=', zone_line.localization_id.id),
                        ('product_id', '=', stock_move.product_id.id)]
                    loc_prod_qty = ProductLocationQ.search(search_domain)
                    if loc_prod_qty: #have: location 1, minimal prod x 1 U
                        location = loc_prod_qty.location_id
                        if check_prod_disponibility(
                                location.id, needed_qty,
                                stock_move.product_id.id,
                                loc_prod_qty.minimal_quant):
                            if location.zone_id.employee_id:
                                possible_owners.add(
                                    location.zone_id.employee_id.id)
                            zinfo = ZoneLocInfo.create(
                                {'location_id' : location.id,
                                 'zone_id': location.zone_id.id,
                                 'location_priority': location.route,
                                 'so_line_id' : so_line.id})
                            countt +=1
                            if location_and_route:
                                if (location.route < location_and_route[1]):
                                    location_and_route = (
                                        zinfo.id, location.route,
                                        location.zone_id.employee_id.id or False)
                            else:
                                location_and_route = (
                                    zinfo.id, location.route,
                                    location.zone_id.employee_id.id or False)
            return location_and_route

        result_confirm = super(SaleOrder, self).action_confirm()
        StockMove = self.env['stock.move']
        StockMoveLine = self.env['stock.move.line']
        for line in self.order_line:
            # TODO: Check what happened with the services product type.
            move = StockMove.search([('sale_line_id', '=', line.id)])
            best_location = get_better_location(line, move, line.product_uom_qty)
            if best_location:
                move.write({'zone_location_info_ids': best_location[0]})
                possible_owners = {best_location[2]}
            else:
                employee_id = update_move_itself(move, line.id)
                possible_owners.add(employee_id)
        for pick in self.picking_ids:
            pick.owner_id = possible_owners.pop()
            # This update the move_lines with the location in the move, and
            # update the reserved quants for create the correct stock moves.
            pick.onchange_move_lines()
        return result_confirm
        


