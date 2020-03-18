# © 2020 onDevelop.sa
# Autor: Idelis Gé Ramírez

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockLocation(models.Model):
    '''Some needed relationship'''

    _inherit = 'stock.location'

    route = fields.Integer(required=True)
    zone_id = fields.Many2one('stock.zone')
    product_quantity_ids = fields.One2many('product.location.quant',
                                           'location_id')
    external_comment = fields.Text()

    _sql_constraints = [
        ('zone_location_uniq', 'unique (route)',
         'This route number belong to other Location !!')]


class ProductLocationQuant(models.Model):
    '''Store the minimal quantity of a specific product in specific
    location.

    '''
    _name = 'product.location.quant'
    _inherit = ['mail.thread']

    product_id = fields.Many2one('product.template', required=True)
    location_id = fields.Many2one('stock.location')
    minimal_quant = fields.Integer(required=True)
