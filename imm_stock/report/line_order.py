# -*- coding: utf-8 -*-

from odoo import api, models
from datetime import datetime, date


class BankDepositReport(models.AbstractModel):
    '''This show all the deposits selected by the user in the 
    account reconciliation.
    '''
    _name = 'report.imm_stock.pdf_product_order_report'
    # _name = 'report.imm_stock.custom_report_pick_template'

    @api.model
    def get_report_values(self, docids, data=None):
        
        '''TODO:DOCUMENT'''
        StockPicking = self.env['stock.picking']
        ZoneLine = self.env['zone.line']
        prod_zone = [] # (zone, location, product, prod_qty)
        prod_no_zone = [] # (zone, location, product, prod_qty)
        product_amount = 0
        pick_date = ''
        for record in docids:
            pick = StockPicking.search([('id', '=', record)])
            pick_date = str(pick.date)
            for line in pick.move_line_ids:
                if line.location_id:
                    zone_line = ZoneLine.search([
                        ('localization_id','=', line.location_id.id)], limit=1)
                    product_amount += line.product_qty
                    if zone_line:
                        prod_zone.append((line.product_qty,
                                       zone_line.zone_id.zone_name,
                                       line.location_id.name,
                                       line.product_id.name,
                                       line.product_qty))
                    else:
                        prod_no_zone.append((line.product_qty,
                                             False,
                                             line.location_id.name,
                                             line.product_id.name,
                                             line.product_qty))
            prod_zone.sort(key=lambda x: x[0])
            return {
                'doc_ids': pick,
                'doc_model': 'stock.picking',
                'move_lines' : pick.move_line_ids.ids,
                'current_date': pick_date,
                'product_amount' : product_amount,
                'prod_zone' : prod_zone,
                'pick_type_name' : pick.picking_type_id.name+ ' : ' + pick.name,
                'docs': [],
            }
