# © 2020 onDevelop.sa
# Autor: Idelis Gé Ramírez

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockWarehouse(models.Model):
    '''Add some needed relationships '''
    
    _inherit = 'stock.warehouse'

    zone_ids = fields.One2many('stock.zone', 'warehouse_id')
    active_employee_ids = fields.One2many('active.employee', 'warehouse_id')


class ActiveEmployee(models.Model):
    '''Store the employee who will attend a specific stock'''
    
    _name = 'active.employee'

    warehouse_id = fields.Many2one('stock.warehouse')
    zone_id = fields.Many2one('stock.zone')
    employee_id = fields.Many2one('res.partner')
    is_active = fields.Boolean()
    

    




    
