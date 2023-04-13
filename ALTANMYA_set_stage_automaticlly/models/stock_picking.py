from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        indicator = 0
        res = super().button_validate()
        for rec in self:
            idss = self.env['crm.stage'].search([]).ids[4]
            seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
            if self.sale_id.opportunity_id.stage_id.sequence <= seq:
                # ///////////////////////////-- operation type manufacturing --///////////////////
                mrp_production_id = self.env['mrp.production'].search([
                    ('procurement_group_id', '=', rec.group_id.id), ('procurement_group_id', '!=', False)])
                # if mrp_production_id:
                sale_order_ids = mrp_production_id.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id.ids
                sale_order_ids = mrp_production_id.env['sale.order'].browse(sale_order_ids)
                for sale in sale_order_ids:
                    stages = self.env['crm.stage'].search([], order='sequence desc')
                    for stage in stages:
                        operation_type = self.env['stock.picking.type'].search(
                            [('id', '=', stage.operation_type_manufacturing.id)]).name
                        if stage.state == 'operation_type_manufacturing' and operation_type == "Store Finished Product":
                            for trans in self:
                                operation_type_1 = self.env['stock.picking.type'].search(
                                    [('id', '=', trans.picking_type_id.id)]).name
                                if trans.state == 'done' and operation_type_1 == "Store Finished Product" and mrp_production_id.state == 'done':
                                    sale.opportunity_id.stage_id = stage.id
                                    sale.opportunity_id.check_status = 'compatible'
                                    return
                                else:
                                    fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                    sale.opportunity_id.stage_id = fifth_stage_id
                                    sale.opportunity_id.check_status = 'not_compatible'
                                    # indicator = 1
                        else:
                            fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            sale.opportunity_id.stage_id = fifth_stage_id
                            sale.opportunity_id.check_status = 'not_compatible'
                            # indicator = 1
                    # else:
                    #     stage = sale.env['crm.stage'].search(
                    #         [('state', '=', 'manufacturing'), ('manufacturing_selection', '=', 'done')],
                    #         order='id desc', limit=1)
                    #     if stage:
                    #         if sale.opportunity_id.id:
                    #             if sale.opportunity_id.stage_id.id != stage.id:
                    #                 sale.opportunity_id.check_status = 'compatible'
                    #     else:
                    #         stage = sale.env['crm.stage'].search(
                    #             [('state', '=', 'manufacturing'), ('manufacturing_selection', '=', 'confirmed')],
                    #             order='id desc',
                    #             limit=1)
                    #         if stage:
                    #             if sale.opportunity_id.id:
                    #                 if sale.opportunity_id.stage_id.id != stage.id:
                    #                     sale.opportunity_id.stage_id = stage.id
                    #                     sale.opportunity_id.check_status = 'compatible'
                    #         else:
                    #             stage = sale.env['crm.stage'].search(
                    #                 [('state', '=', 'manufacturing'), ('manufacturing_selection', '=', 'approve')],
                    #                 order='id desc',
                    #                 limit=1)
                    #             if stage:
                    #                 if sale.opportunity_id.id:
                    #                     if sale.opportunity_id.stage_id.id != stage.id:
                    #                         sale.opportunity_id.stage_id = stage.id
                    #                         sale.opportunity_id.check_status = 'compatible'
                    #             else:
                    #                 check_quotations = self.env['crm.lead'].search(
                    #                     [('id', '=', sale.opportunity_id)]).quotation_ids.ids
                    #                 if stage.state == 'sales_status' and stage.sales_status_selection == 'draft':
                    #                     if len(check_quotations) >= 1:
                    #                         sale.opportunity_id.check_status = 'compatible'
                    #                         sale.opportunity_id.write({'stage_id': stage.id})
                    #                 else:
                    #                     sale.opportunity_id._compute_quotation_count()
                    #                     sale.opportunity_id.check_status = 'not_compatible'

                #              ///////////////////////////-- operation type sales-under install --///////////////////

            idss = self.env['crm.stage'].search([]).ids[5]
            seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
            if self.sale_id.opportunity_id.stage_id.sequence <= seq:
                sale_order_ids = rec.group_id.sale_id.id
                sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                for sale in sale_order_ids:
                    stages = self.env['crm.stage'].search([], order='sequence desc')
                    for stage in stages:
                        operation_type = self.env['stock.picking.type'].search(
                            [('id', '=', stage.operation_type_sales.id)]).name
                        if stage.state == 'operation_type_sales' and operation_type == "Pick":
                            for dev in self:
                                operation_type_1 = self.env['stock.picking.type'].search(
                                    [('id', '=', dev.picking_type_id.id)]).name
                                if dev.state == 'done' and operation_type_1 == "Pick":
                                    sale.opportunity_id.stage_id = stage.id
                                    sale.opportunity_id.check_status = 'compatible'
                                    return
                        #         else:
                        #             print('5')
                        #             if indicator not in (0, 1):
                        #                 print('5.5')
                        #                 sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                        #                 sale.opportunity_id.stage_id = sixth_stage_id
                        #                 sale.opportunity_id.check_status = 'not_compatible'
                        #                 indicator = 2
                        # else:
                        #     print('6')
                        #     if indicator not in (0, 1):
                        #         print('6.5')
                        #         sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                        #         sale.opportunity_id.stage_id = sixth_stage_id
                        #         sale.opportunity_id.check_status = 'not_compatible'
                        #         indicator = 2

                    #              ///////////////////////////-- operation type sales-done --///////////////////

            idss = self.env['crm.stage'].search([]).ids[6]
            seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
            if self.sale_id.opportunity_id.stage_id.sequence <= seq:
                sale_order_ids = rec.group_id.sale_id.id
                sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                for sale in sale_order_ids:
                    stages = self.env['crm.stage'].search([], order='sequence desc')
                    for stage in stages:
                        operation_type = self.env['stock.picking.type'].search(
                            [('id', '=', stage.operation_type_sales.id)]).name
                        if stage.state == 'operation_type_sales' and operation_type == "Delivery Orders":
                            for dev in self:
                                operation_type_1 = self.env['stock.picking.type'].search(
                                    [('id', '=', dev.picking_type_id.id)]).name
                                if dev.state == 'done' and operation_type_1 == "Delivery Orders":
                                    sale.opportunity_id.stage_id = stage.id
                                    sale.opportunity_id.check_status = 'compatible'
                                    return
                        #         else:
                        #             if indicator not in (2, 1):
                        #                 seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                        #                 sale.opportunity_id.stage_id = seventh_stage_id
                        #                 sale.opportunity_id.check_status = 'not_compatible'
                        # else:
                        #     if indicator not in (2, 1):
                        #         seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                        #         sale.opportunity_id.stage_id = seventh_stage_id
                        #         sale.opportunity_id.check_status = 'not_compatible'
                    # else:
                    #     stages = self.env['crm.stage'].search([], order='sequence desc')
                    #     for stage in stages:
                    #         if stage.state == 'sales_status' and stage.sales_status_selection == 'sale':
                    #             print("its trigger her111")
                    #             sale.opportunity_id.check_status = 'compatible'
                    #             sale.opportunity_id.stage_id = stage.id
                    #         else:
                    #             print("111222111222")
                    #             """get the final approval to here"""
                    #             "/////////////////////////////////////////////////"
                    #             print("stage", stage)
                    #             if stage.state == 'sales_status' and stage.sales_status_selection == 'tentative/final approval':
                    #                 print("11")
                    #                 sale.opportunity_id.stage_id = stage.id
                    #                 sale.opportunity_id.check_status = 'compatible'
                    #                 print("truuuuuuuuuuuu")
                    #             else:
                    #                 check_quotations = self.env['crm.lead'].search(
                    #                     [(
                    #                         'id', '=',
                    #                         sale.opportunity_id)]).quotation_ids.ids
                    #                 if stage.state == 'sales_status' and stage.sales_status_selection == 'draft':
                    #                     if len(check_quotations) >= 1:
                    #                         sale.opportunity_id.check_status = 'compatible'
                    #                         sale.opportunity_id.write({'stage_id': stage.id})
                    #                 else:
                    #                     sale.opportunity_id._compute_quotation_count()
                    #                     sale.opportunity_id.check_status = 'not_compatible'
                    #             sale.opportunity_id.check_status = 'not_compatible'
        return res


class ImmediateStockPicking(models.TransientModel):
    _inherit = "stock.immediate.transfer"

    def process(self):
        indicator = 0
        res = super().process()
        if self.env.context.get('default_opportunity_id'):
            opportunity_id = self.env['crm.lead'].search([('id', '=', self.env.context['default_opportunity_id'])])
            origin = opportunity_id.order_ids.name
            picking_ids = self.env['stock.picking'].search([('origin', '=', origin)])
            for rec in picking_ids:
                idss = self.env['crm.stage'].search([]).ids[4]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    mrp_production_id = self.env['mrp.production'].search([
                        ('procurement_group_id', '=', rec.group_id.id), ('procurement_group_id', '!=', False)])
                    sale_order_ids = mrp_production_id.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id.ids
                    sale_order_ids = mrp_production_id.env['sale.order'].browse(sale_order_ids)
                    # ///////////////////////////-- operation type manufacturing --///////////////////
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_manufacturing.id)]).name
                            if stage.state == 'operation_type_manufacturing' and operation_type == "Store Finished Product":
                                for trans in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', trans.picking_type_id.id)]).name
                                    if trans.state == 'done' and operation_type_1 == "Store Finished Product" and mrp_production_id.state == 'done':
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                                    else:
                                        fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                        sale.opportunity_id.stage_id = fifth_stage_id
                                        sale.opportunity_id.check_status = 'not_compatible'
                            else:
                                fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                sale.opportunity_id.stage_id = fifth_stage_id
                                sale.opportunity_id.check_status = 'not_compatible'

                    # ///////////////////////////-- operation type sales-under install --///////////////////

                idss = self.env['crm.stage'].search([]).ids[5]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    sale_order_ids = rec.group_id.sale_id.id
                    sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_sales.id)]).name
                            if stage.state == 'operation_type_sales' and operation_type == "Pick":
                                for dev in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', dev.picking_type_id.id)]).name
                                    if dev.state == 'done' and operation_type_1 == "Pick":
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                            #         else:
                            #             print('5b')
                            #             if indicator != 0:
                            #                 print('5.5b')
                            #                 sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #                 sale.opportunity_id.stage_id = sixth_stage_id
                            #                 sale.opportunity_id.check_status = 'not_compatible'
                            #                 indicator = 2
                            # else:
                            #     print('6b')
                            #     if indicator != 0:
                            #         print('6.5b')
                            #         sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #         sale.opportunity_id.stage_id = sixth_stage_id
                            #         sale.opportunity_id.check_status = 'not_compatible'
                            #         indicator = 2
                        #              ///////////////////////////-- operation type sales-done --///////////////////

                idss = self.env['crm.stage'].search([]).ids[6]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    sale_order_ids = rec.group_id.sale_id.id
                    sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_sales.id)]).name
                            if stage.state == 'operation_type_sales' and operation_type == "Delivery Orders":
                                for dev in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', dev.picking_type_id.id)]).name
                                    if dev.state == 'done' and operation_type_1 == "Delivery Orders":
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                            #         else:
                            #             print('4c')
                            #             if indicator not in (2, 1):
                            #                 seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #                 sale.opportunity_id.stage_id = seventh_stage_id
                            #                 sale.opportunity_id.check_status = 'not_compatible'
                            # else:
                            #     print('5c')
                            #     if indicator not in (2, 1):
                            #         seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #         sale.opportunity_id.stage_id = seventh_stage_id
                            #         sale.opportunity_id.check_status = 'not_compatible'

        else:
            opportunity_id = self.env['sale.order'].search([('id', '=', self.env.context['active_id'])]).opportunity_id
            origin = opportunity_id.order_ids.name
            picking_ids = self.env['stock.picking'].search([('origin', '=', origin)])
            for rec in picking_ids:
                idss = self.env['crm.stage'].search([]).ids[4]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    mrp_production_id = self.env['mrp.production'].search([
                        ('procurement_group_id', '=', rec.group_id.id), ('procurement_group_id', '!=', False)])
                    sale_order_ids = mrp_production_id.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id.ids
                    sale_order_ids = mrp_production_id.env['sale.order'].browse(sale_order_ids)
                    # ///////////////////////////-- operation type manufacturing --///////////////////
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_manufacturing.id)]).name
                            if stage.state == 'operation_type_manufacturing' and operation_type == "Store Finished Product":
                                for trans in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', trans.picking_type_id.id)]).name
                                    if trans.state == 'done' and operation_type_1 == "Store Finished Product" and mrp_production_id.state == 'done':
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                                    else:
                                        fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                        sale.opportunity_id.stage_id = fifth_stage_id
                                        sale.opportunity_id.check_status = 'not_compatible'
                            else:
                                fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                sale.opportunity_id.stage_id = fifth_stage_id
                                sale.opportunity_id.check_status = 'not_compatible'

                    # ///////////////////////////-- operation type sales-under install --///////////////////

                idss = self.env['crm.stage'].search([]).ids[5]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    sale_order_ids = rec.group_id.sale_id.id
                    sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_sales.id)]).name
                            if stage.state == 'operation_type_sales' and operation_type == "Pick":
                                for dev in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', dev.picking_type_id.id)]).name
                                    if dev.state == 'done' and operation_type_1 == "Pick":
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                            #         else:
                            #             print('5b')
                            #             if indicator != 0:
                            #                 print('5.5b')
                            #                 sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #                 sale.opportunity_id.stage_id = sixth_stage_id
                            #                 sale.opportunity_id.check_status = 'not_compatible'
                            #                 indicator = 2
                            # else:
                            #     print('6b')
                            #     if indicator != 0:
                            #         print('6.5b')
                            #         sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #         sale.opportunity_id.stage_id = sixth_stage_id
                            #         sale.opportunity_id.check_status = 'not_compatible'
                            #         indicator = 2
                        #              ///////////////////////////-- operation type sales-done --///////////////////

                idss = self.env['crm.stage'].search([]).ids[6]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    sale_order_ids = rec.group_id.sale_id.id
                    sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_sales.id)]).name
                            if stage.state == 'operation_type_sales' and operation_type == "Delivery Orders":
                                for dev in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', dev.picking_type_id.id)]).name
                                    if dev.state == 'done' and operation_type_1 == "Delivery Orders":
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                            #         else:
                            #             print('4c')
                            #             if indicator not in (2, 1):
                            #                 seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #                 sale.opportunity_id.stage_id = seventh_stage_id
                            #                 sale.opportunity_id.check_status = 'not_compatible'
                            # else:
                            #     print('5c')
                            #     if indicator not in (2, 1):
                            #         seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #         sale.opportunity_id.stage_id = seventh_stage_id
                            #         sale.opportunity_id.check_status = 'not_compatible'

        return res

class StockBackOrderConfirmation1(models.TransientModel):
    _inherit = "stock.backorder.confirmation"

    def process(self):
        res = super().process()
        if self.env.context.get('default_opportunity_id'):
            opportunity_id = self.env['crm.lead'].search([('id', '=', self.env.context['default_opportunity_id'])])
            origin = opportunity_id.order_ids.name
            picking_ids = self.env['stock.picking'].search([('origin', '=', origin)])
            for rec in picking_ids:
                idss = self.env['crm.stage'].search([]).ids[4]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    mrp_production_id = self.env['mrp.production'].search([
                        ('procurement_group_id', '=', rec.group_id.id), ('procurement_group_id', '!=', False)])
                    sale_order_ids = mrp_production_id.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id.ids
                    sale_order_ids = mrp_production_id.env['sale.order'].browse(sale_order_ids)
                    # ///////////////////////////-- operation type manufacturing --///////////////////
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_manufacturing.id)]).name
                            if stage.state == 'operation_type_manufacturing' and operation_type == "Store Finished Product":
                                for trans in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', trans.picking_type_id.id)]).name
                                    if trans.state == 'done' and operation_type_1 == "Store Finished Product" and mrp_production_id.state == 'done':
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                                    else:
                                        fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                        sale.opportunity_id.stage_id = fifth_stage_id
                                        sale.opportunity_id.check_status = 'not_compatible'
                            else:
                                fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                sale.opportunity_id.stage_id = fifth_stage_id
                                sale.opportunity_id.check_status = 'not_compatible'

                    # ///////////////////////////-- operation type sales-under install --///////////////////

                idss = self.env['crm.stage'].search([]).ids[5]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    sale_order_ids = rec.group_id.sale_id.id
                    sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_sales.id)]).name
                            if stage.state == 'operation_type_sales' and operation_type == "Pick":
                                for dev in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', dev.picking_type_id.id)]).name
                                    if dev.state == 'done' and operation_type_1 == "Pick":
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                            #         else:
                            #             print('5b')
                            #             if indicator != 0:
                            #                 print('5.5b')
                            #                 sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #                 sale.opportunity_id.stage_id = sixth_stage_id
                            #                 sale.opportunity_id.check_status = 'not_compatible'
                            #                 indicator = 2
                            # else:
                            #     print('6b')
                            #     if indicator != 0:
                            #         print('6.5b')
                            #         sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #         sale.opportunity_id.stage_id = sixth_stage_id
                            #         sale.opportunity_id.check_status = 'not_compatible'
                            #         indicator = 2
                        #              ///////////////////////////-- operation type sales-done --///////////////////

                idss = self.env['crm.stage'].search([]).ids[6]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    sale_order_ids = rec.group_id.sale_id.id
                    sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_sales.id)]).name
                            if stage.state == 'operation_type_sales' and operation_type == "Delivery Orders":
                                for dev in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', dev.picking_type_id.id)]).name
                                    if dev.state == 'done' and operation_type_1 == "Delivery Orders":
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                            #         else:
                            #             print('4c')
                            #             if indicator not in (2, 1):
                            #                 seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #                 sale.opportunity_id.stage_id = seventh_stage_id
                            #                 sale.opportunity_id.check_status = 'not_compatible'
                            # else:
                            #     print('5c')
                            #     if indicator not in (2, 1):
                            #         seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #         sale.opportunity_id.stage_id = seventh_stage_id
                            #         sale.opportunity_id.check_status = 'not_compatible'

        else:
            opportunity_id = self.env['sale.order'].search([('id', '=', self.env.context['active_id'])]).opportunity_id
            origin = opportunity_id.order_ids.name
            picking_ids = self.env['stock.picking'].search([('origin', '=', origin)])
            for rec in picking_ids:
                idss = self.env['crm.stage'].search([]).ids[4]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    mrp_production_id = self.env['mrp.production'].search([
                        ('procurement_group_id', '=', rec.group_id.id), ('procurement_group_id', '!=', False)])
                    sale_order_ids = mrp_production_id.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id.ids
                    sale_order_ids = mrp_production_id.env['sale.order'].browse(sale_order_ids)
                    # ///////////////////////////-- operation type manufacturing --///////////////////
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_manufacturing.id)]).name
                            if stage.state == 'operation_type_manufacturing' and operation_type == "Store Finished Product":
                                for trans in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', trans.picking_type_id.id)]).name
                                    if trans.state == 'done' and operation_type_1 == "Store Finished Product" and mrp_production_id.state == 'done':
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                                    else:
                                        fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                        sale.opportunity_id.stage_id = fifth_stage_id
                                        sale.opportunity_id.check_status = 'not_compatible'
                            else:
                                fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                sale.opportunity_id.stage_id = fifth_stage_id
                                sale.opportunity_id.check_status = 'not_compatible'

                    # ///////////////////////////-- operation type sales-under install --///////////////////

                idss = self.env['crm.stage'].search([]).ids[5]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    sale_order_ids = rec.group_id.sale_id.id
                    sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_sales.id)]).name
                            if stage.state == 'operation_type_sales' and operation_type == "Pick":
                                for dev in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', dev.picking_type_id.id)]).name
                                    if dev.state == 'done' and operation_type_1 == "Pick":
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                            #         else:
                            #             print('5b')
                            #             if indicator != 0:
                            #                 print('5.5b')
                            #                 sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #                 sale.opportunity_id.stage_id = sixth_stage_id
                            #                 sale.opportunity_id.check_status = 'not_compatible'
                            #                 indicator = 2
                            # else:
                            #     print('6b')
                            #     if indicator != 0:
                            #         print('6.5b')
                            #         sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #         sale.opportunity_id.stage_id = sixth_stage_id
                            #         sale.opportunity_id.check_status = 'not_compatible'
                            #         indicator = 2
                        #              ///////////////////////////-- operation type sales-done --///////////////////

                idss = self.env['crm.stage'].search([]).ids[6]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    sale_order_ids = rec.group_id.sale_id.id
                    sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_sales.id)]).name
                            if stage.state == 'operation_type_sales' and operation_type == "Delivery Orders":
                                for dev in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', dev.picking_type_id.id)]).name
                                    if dev.state == 'done' and operation_type_1 == "Delivery Orders":
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                            #         else:
                            #             print('4c')
                            #             if indicator not in (2, 1):
                            #                 seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #                 sale.opportunity_id.stage_id = seventh_stage_id
                            #                 sale.opportunity_id.check_status = 'not_compatible'
                            # else:
                            #     print('5c')
                            #     if indicator not in (2, 1):
                            #         seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #         sale.opportunity_id.stage_id = seventh_stage_id
                            #         sale.opportunity_id.check_status = 'not_compatible'
        return res

    def process_cancel_backorder(self):
        res = super().process_cancel_backorder()
        if self.env.context.get('default_opportunity_id'):
            opportunity_id = self.env['crm.lead'].search([('id', '=', self.env.context['default_opportunity_id'])])
            origin = opportunity_id.order_ids.name
            picking_ids = self.env['stock.picking'].search([('origin', '=', origin)])
            for rec in picking_ids:
                idss = self.env['crm.stage'].search([]).ids[4]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    mrp_production_id = self.env['mrp.production'].search([
                        ('procurement_group_id', '=', rec.group_id.id), ('procurement_group_id', '!=', False)])
                    sale_order_ids = mrp_production_id.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id.ids
                    sale_order_ids = mrp_production_id.env['sale.order'].browse(sale_order_ids)
                    # ///////////////////////////-- operation type manufacturing --///////////////////
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_manufacturing.id)]).name
                            if stage.state == 'operation_type_manufacturing' and operation_type == "Store Finished Product":
                                for trans in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', trans.picking_type_id.id)]).name
                                    if trans.state == 'done' and operation_type_1 == "Store Finished Product" and mrp_production_id.state == 'done':
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                                    else:
                                        fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                        sale.opportunity_id.stage_id = fifth_stage_id
                                        sale.opportunity_id.check_status = 'not_compatible'
                            else:
                                fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                sale.opportunity_id.stage_id = fifth_stage_id
                                sale.opportunity_id.check_status = 'not_compatible'

                    # ///////////////////////////-- operation type sales-under install --///////////////////

                idss = self.env['crm.stage'].search([]).ids[5]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    sale_order_ids = rec.group_id.sale_id.id
                    sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_sales.id)]).name
                            if stage.state == 'operation_type_sales' and operation_type == "Pick":
                                for dev in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', dev.picking_type_id.id)]).name
                                    if dev.state == 'done' and operation_type_1 == "Pick":
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                            #         else:
                            #             print('5b')
                            #             if indicator != 0:
                            #                 print('5.5b')
                            #                 sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #                 sale.opportunity_id.stage_id = sixth_stage_id
                            #                 sale.opportunity_id.check_status = 'not_compatible'
                            #                 indicator = 2
                            # else:
                            #     print('6b')
                            #     if indicator != 0:
                            #         print('6.5b')
                            #         sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #         sale.opportunity_id.stage_id = sixth_stage_id
                            #         sale.opportunity_id.check_status = 'not_compatible'
                            #         indicator = 2
                        #              ///////////////////////////-- operation type sales-done --///////////////////

                idss = self.env['crm.stage'].search([]).ids[6]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    sale_order_ids = rec.group_id.sale_id.id
                    sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_sales.id)]).name
                            if stage.state == 'operation_type_sales' and operation_type == "Delivery Orders":
                                for dev in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', dev.picking_type_id.id)]).name
                                    if dev.state == 'done' and operation_type_1 == "Delivery Orders":
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                            #         else:
                            #             print('4c')
                            #             if indicator not in (2, 1):
                            #                 seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #                 sale.opportunity_id.stage_id = seventh_stage_id
                            #                 sale.opportunity_id.check_status = 'not_compatible'
                            # else:
                            #     print('5c')
                            #     if indicator not in (2, 1):
                            #         seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #         sale.opportunity_id.stage_id = seventh_stage_id
                            #         sale.opportunity_id.check_status = 'not_compatible'

        else:
            opportunity_id = self.env['sale.order'].search([('id', '=', self.env.context['active_id'])]).opportunity_id
            origin = opportunity_id.order_ids.name
            picking_ids = self.env['stock.picking'].search([('origin', '=', origin)])
            for rec in picking_ids:
                idss = self.env['crm.stage'].search([]).ids[4]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    mrp_production_id = self.env['mrp.production'].search([
                        ('procurement_group_id', '=', rec.group_id.id), ('procurement_group_id', '!=', False)])
                    sale_order_ids = mrp_production_id.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id.ids
                    sale_order_ids = mrp_production_id.env['sale.order'].browse(sale_order_ids)
                    # ///////////////////////////-- operation type manufacturing --///////////////////
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_manufacturing.id)]).name
                            if stage.state == 'operation_type_manufacturing' and operation_type == "Store Finished Product":
                                for trans in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', trans.picking_type_id.id)]).name
                                    if trans.state == 'done' and operation_type_1 == "Store Finished Product" and mrp_production_id.state == 'done':
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                                    else:
                                        fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                        sale.opportunity_id.stage_id = fifth_stage_id
                                        sale.opportunity_id.check_status = 'not_compatible'
                            else:
                                fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                sale.opportunity_id.stage_id = fifth_stage_id
                                sale.opportunity_id.check_status = 'not_compatible'

                    # ///////////////////////////-- operation type sales-under install --///////////////////

                idss = self.env['crm.stage'].search([]).ids[5]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    sale_order_ids = rec.group_id.sale_id.id
                    sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_sales.id)]).name
                            if stage.state == 'operation_type_sales' and operation_type == "Pick":
                                for dev in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', dev.picking_type_id.id)]).name
                                    if dev.state == 'done' and operation_type_1 == "Pick":
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                            #         else:
                            #             print('5b')
                            #             if indicator != 0:
                            #                 print('5.5b')
                            #                 sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #                 sale.opportunity_id.stage_id = sixth_stage_id
                            #                 sale.opportunity_id.check_status = 'not_compatible'
                            #                 indicator = 2
                            # else:
                            #     print('6b')
                            #     if indicator != 0:
                            #         print('6.5b')
                            #         sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #         sale.opportunity_id.stage_id = sixth_stage_id
                            #         sale.opportunity_id.check_status = 'not_compatible'
                            #         indicator = 2
                        #              ///////////////////////////-- operation type sales-done --///////////////////

                idss = self.env['crm.stage'].search([]).ids[6]
                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                if opportunity_id.stage_id.sequence <= seq:
                    sale_order_ids = rec.group_id.sale_id.id
                    sale_order_ids = rec.env['sale.order'].browse(sale_order_ids)
                    for sale in sale_order_ids:
                        stages = self.env['crm.stage'].search([], order='sequence desc')
                        for stage in stages:
                            operation_type = self.env['stock.picking.type'].search(
                                [('id', '=', stage.operation_type_sales.id)]).name
                            if stage.state == 'operation_type_sales' and operation_type == "Delivery Orders":
                                for dev in picking_ids:
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', dev.picking_type_id.id)]).name
                                    if dev.state == 'done' and operation_type_1 == "Delivery Orders":
                                        sale.opportunity_id.stage_id = stage.id
                                        sale.opportunity_id.check_status = 'compatible'
                                        return
                            #         else:
                            #             print('4c')
                            #             if indicator not in (2, 1):
                            #                 seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #                 sale.opportunity_id.stage_id = seventh_stage_id
                            #                 sale.opportunity_id.check_status = 'not_compatible'
                            # else:
                            #     print('5c')
                            #     if indicator not in (2, 1):
                            #         seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            #         sale.opportunity_id.stage_id = seventh_stage_id
                            #         sale.opportunity_id.check_status = 'not_compatible'
        return res