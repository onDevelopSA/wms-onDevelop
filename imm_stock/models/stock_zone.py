# © 2020 onDevelop.sa
# Autor: Idelis Gé Ramírez

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockZone(models.Model):
    '''Group many location in one entity with an employee who attend this
    zone.

    '''
    _name = 'stock.zone'
    _description = 'Stock Zone'
    _rec_name = 'zone_name'

    zone_name = fields.Char(required=True)
    warehouse_id = fields.Many2one('stock.warehouse', required=True)
    line_ids = fields.One2many('zone.line', 'zone_id')
    employee_id = fields.Many2one('res.partner')


class ZoneLine(models.Model):
    '''Group all the locations who belong to this zone.'''

    _name = 'zone.line'
    _description = 'Stock Zone'
    _rec_name = 'localization_id'

    zone_id = fields.Many2one('stock.zone')
    localization_id = fields.Many2one('stock.location', required=True)
    location_route = fields.Integer(related='localization_id.route',
                                    store=True)

    @api.model
    def create(self, vals):
        '''Update the stock.location with the related zone who belong. '''
        StockLocation = self.env['stock.location']
        location = StockLocation.search([
            ('id', '=', vals.get('localization_id'))])
        location.zone_id = vals.get('zone_id')
        return super(ZoneLine, self).create(vals)

    _sql_constraints = [
        ('zone_location_uniq', 'unique (localization_id)',
         'This location appear in other zone and the location must be only\
         in one zone. !')]
