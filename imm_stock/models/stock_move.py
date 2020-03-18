# © 2020 onDevelop.sa
# Autor: Idelis Gé Ramírez

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockMove(models.Model):

    _inherit = "stock.move"

    zone_location_info_ids = fields.Many2one(
        'zone.location.info', domain="[('so_line_id','=',sale_line_id)]")
