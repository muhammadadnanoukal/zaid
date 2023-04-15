from odoo import api, fields, models, _, Command


class CrmStage(models.Model):
    """ Manufacturing Orders """
    _inherit = 'crm.stage'

    new_stage = fields.Boolean(string='New Stage')
    state = fields.Selection([
        ('sales_status', 'Sales Status'),
        ('manufacturing', 'Manufacturing'),
        ('operation_type_sales', 'Operation Type-Sales'),
        ('operation_type_manufacturing', 'Operation Type-Manufacturing'),

    ])
    sales_status_selection = fields.Selection([
        ('draft', "Quotation"),
        ('sent', "Quotation Sent"),
        ('tentative/final approval', 'Tentative/Final Approval'),
        ('sale', "Sales Order"),
        ('done', "Locked"),
        ('cancel', "Cancelled"),
    ])
    manufacturing_selection = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')])

    operation_type_sales = fields.Many2one('stock.picking.type', string="Operation Type-Sales")
    operation_type_manufacturing = fields.Many2one('stock.picking.type', string="Operation Type-Manufacturing")

    # @api.model
    # def search(self, domain, offset=0, limit=None, order=None, count=False):
    #     res = super().search(domain, offset=offset, limit=limit, order=order, count=count)
    #     print('555555')
    #     return res if count else self.browse(res)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        res = super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        pipelines = self.env['crm.lead'].search([])
        stages = self.env['crm.stage'].search([], order='sequence desc')
        print('///////////////////////////////')
        for stage in stages:
            for pipeline in pipelines:
                quotations = self.env['sale.order'].search([('opportunity_id', '=', pipeline.id)])
                for quotation in quotations:
                    print('//////////////', stages, '///////////////', stage)
                    print('//////////////', pipelines, '///////////////', pipeline.id)
                    print('//////////////', quotations, '///////////////', quotation)

                    #            ///////////////////////////--quotation count condition--///////////////////
                    idss = self.env['crm.stage'].search([]).ids[0]
                    seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                    if stage.sequence <= seq:
                        print('pricing stage 1')
                        if len(quotations) >= 1 and quotation.state == 'draft':
                            print('pricing stage 1 ok')
                            new_stage = pipeline.env['crm.stage'].search(
                                [('state', '=', 'sales_status'), ('sales_status_selection', '=', 'draft')],
                                order='id desc', limit=1)
                            if new_stage:
                                print('pricing stage 1 ok x2')
                                pipeline.write({'stage_id': new_stage.id})
                                pipeline.check_status = 'compatible'
                            else:
                                print('pricing stage 1 else')
                                # first_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                # quotation.opportunity_id.stage_id = first_stage_id
                                quotation.opportunity_id.check_status = 'not_compatible'
                        elif len(quotations) >= 1 and quotation.state == 'cancel':
                            print('pricing stage 1 else x2')
                            # first_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            # quotation.opportunity_id.stage_id = first_stage_id
                            quotation.opportunity_id.check_status = 'not_compatible'

                        # ///////////////////////////--quotation tentative and final --///////////////////

                    if quotation.state == 'tentative approval' or quotation.state == 'final approval':
                        print('contracting stage 2/3')
                        idss = self.env['crm.stage'].search([]).ids[1]
                        seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                        if stage.sequence <= seq:
                            print('contracting stage 2/3 ok')
                            new_stage = self.env['crm.stage'].search([('state', '=', 'sales_status'), (
                                'sales_status_selection', '=', 'tentative/final approval')], order='id desc',
                                                                     limit=1)
                            if quotation.state == 'tentative approval' or quotation.state == 'final approval':
                                print('contracting stage 2/3 ok x2')
                                if new_stage:
                                    print('contracting stage 2/3 ok x3')
                                    quotation.opportunity_id.write({'stage_id': new_stage.id})
                                    quotation.opportunity_id.check_status = 'compatible'
                                    return res

                                else:
                                    print('contracting stage 2/3 else')
                                    # second_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                    # quotation.opportunity_id.stage_id = second_stage_id
                                    quotation.opportunity_id.check_status = 'not_compatible'
                            else:
                                print('contracting stage 2/3 else x2')
                                # second_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                # quotation.opportunity_id.stage_id = second_stage_id
                                quotation.opportunity_id.check_status = 'not_compatible'

                    # ///////////////////////////--quotation Sales Order --///////////////////

                    production_ids = self.env['mrp.production'].search(
                        [('id', 'in', quotation.mrp_production_ids.ids)])
                    #
                    for product in production_ids:
                        if quotation.state == 'sale' and product.state not in ['confirmed', 'done']:
                            print('approved stage 4')
                            idss = self.env['crm.stage'].search([]).ids[2]
                            seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                            if stage.sequence <= seq:
                                print('approved stage 4 ok')
                                new_stage = quotation.env['crm.stage'].search(
                                    [('state', '=', 'sales_status'), ('sales_status_selection', '=', 'sale')]
                                    , order='id desc', limit=1)
                                if quotation.state == 'sale':
                                    print('approved stage 4 ok x2')
                                    if new_stage:
                                        print('approved stage 4 ok x3')
                                        quotation.opportunity_id.write({'stage_id': new_stage.id})
                                        quotation.opportunity_id.check_status = 'compatible'
                                    else:
                                        print('approved stage 4 else')
                                        # third_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                        # quotation.opportunity_id.stage_id = third_stage_id
                                        quotation.opportunity_id.check_status = 'not_compatible'
                                else:
                                    print('approved stage 4 else x2')
                                    # third_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                    # quotation.opportunity_id.stage_id = third_stage_id
                                    quotation.opportunity_id.check_status = 'not_compatible'

                        # #            ///////////////////////////--manufacturing confirmed --///////////////////

                        if product.state == 'confirmed' and quotation.state != 'cancel':
                            print('under production stage 5')
                            idss = self.env['crm.stage'].search([]).ids[3]
                            seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                            if stage.sequence <= seq:
                                print('under production stage 5 ok')
                                if stage.state == 'manufacturing' and stage.manufacturing_selection == 'confirmed':
                                    print('under production stage 5 ok x2')
                                    for manf in quotation.procurement_group_id.mrp_production_ids:
                                        if product.state == 'confirmed' and quotation.state != 'cancel':
                                            print('under production stage 5 ok x3')
                                            if manf.state == 'confirmed':
                                                print('under production stage 5 ok x4')
                                                quotation.opportunity_id.stage_id = stage.id
                                                quotation.opportunity_id.check_status = 'compatible'
                                                return res
                                        else:
                                            print('under production stage 5 else')
                                            # forth_stage_id = self.env['crm.stage'].search(
                                            #     [('sequence', '=', seq)])
                                            # quotation.opportunity_id.stage_id = forth_stage_id
                                            quotation.opportunity_id.check_status = 'not_compatible'
                        elif product.state == 'cancelled' and quotation.state == 'sale':
                            print('under production stage 5 else x2')
                            # forth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                            # quotation.opportunity_id.stage_id = forth_stage_id
                            quotation.opportunity_id.check_status = 'not_compatible'

                        # ///////////////////////////-- operation type manufacturing
                        # --/////////////////////////////////////////////////////////////////////////

                        manufacture_picking_ids = self.env['stock.picking'].search([
                            ('group_id', '=', product.procurement_group_id.id), ('group_id', '!=', False)])

                        for product_piking_id in manufacture_picking_ids:
                            if product_piking_id.state == 'done' and product.state == 'done':
                                print('stored stage 6')
                                idss = self.env['crm.stage'].search([]).ids[4]
                                seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                                # if stage.sequence <= seq:
                                print('stored stage 6 ok')
                                operation_type = self.env['stock.picking.type'].search(
                                    [('id', '=', stage.operation_type_manufacturing.id)]).name
                                if stage.state == 'operation_type_manufacturing' and operation_type == "Store Finished Product" and quotation.state != 'cancel':
                                    print('stored stage 6 ok x2')
                                    operation_type_1 = self.env['stock.picking.type'].search(
                                        [('id', '=', product_piking_id.picking_type_id.id)]).name
                                    if product_piking_id.state == 'done' and operation_type_1 == "Store Finished Product" and product.state == 'done':
                                        print('stored stage 6 ok x3')
                                        quotation.opportunity_id.stage_id = stage.id
                                        quotation.opportunity_id.check_status = 'compatible'
                                        return res
                                    else:
                                        print('stored stage 6 else')
                                        # fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                        # quotation.opportunity_id.stage_id = fifth_stage_id
                                        quotation.opportunity_id.check_status = 'not_compatible'
                                        # indicator = 1
                                else:
                                    print('stored stage 6 else x2')
                                    # fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                                    # quotation.opportunity_id.stage_id = fifth_stage_id
                                    quotation.opportunity_id.check_status = 'not_compatible'
                                    # indicator = 1

                        # ///////////////////////////-- operation type sales-under install --///////////////////
                    delivery_transfer_ids = self.env['stock.picking'].search(
                        [('id', 'in', quotation.picking_ids.ids)])

                    for delivery_transfer_id in delivery_transfer_ids:
                        idss = self.env['crm.stage'].search([]).ids[5]
                        seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                        # if stage.sequence <= seq:
                        print('under installation stage 7 ok')
                        operation_type = self.env['stock.picking.type'].search(
                            [('id', '=', stage.operation_type_sales.id)]).name
                        if stage.state == 'operation_type_sales' and operation_type == "Pick" and quotation.state != 'cancel':
                            print('under installation stage 7 ok x2')
                            operation_type_1 = self.env['stock.picking.type'].search(
                                [('id', '=', delivery_transfer_id.picking_type_id.id)]).name
                            if delivery_transfer_id.state == 'done' and operation_type_1 == "Pick":
                                print('under installation stage 7 ok x3')
                                quotation.opportunity_id.stage_id = stage.id
                                quotation.opportunity_id.check_status = 'compatible'
                                return res
                        #     else:
                        #         if indicator not in (0, 1):
                        #             sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                        #             quotation.opportunity_id.stage_id = sixth_stage_id
                        #             quotation.opportunity_id.check_status = 'not_compatible'
                        #             indicator = 2
                        # else:
                        #     if indicator not in (0, 1):
                        #         sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                        #         quotation.opportunity_id.stage_id = sixth_stage_id
                        #         quotation.opportunity_id.check_status = 'not_compatible'
                        #         indicator = 2

                        # ///////////////////////////-- operation type sales-done --///////////////////

                        idss = self.env['crm.stage'].search([]).ids[6]
                        seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                        # if stage.sequence <= seq:
                        print('done stage 8')
                        operation_type = self.env['stock.picking.type'].search(
                            [('id', '=', stage.operation_type_sales.id)]).name
                        if stage.state == 'operation_type_sales' and operation_type == "Delivery Orders" and quotation.state != 'cancel':
                            print('done stage 8 ok')
                            operation_type_1 = self.env['stock.picking.type'].search(
                                [('id', '=', delivery_transfer_id.picking_type_id.id)]).name
                            if delivery_transfer_id.state == 'done' and operation_type_1 == "Delivery Orders":
                                print('done stage 8 ok x2')
                                quotation.opportunity_id.stage_id = stage.id
                                quotation.opportunity_id.check_status = 'compatible'
                                return res
                        #     else:
                        #         if indicator not in (2, 1):
                        #             seventh_stage_id = self.env['crm.stage'].search(
                        #                 [('sequence', '=', seq)])
                        #             quotation.opportunity_id.stage_id = seventh_stage_id
                        #             quotation.opportunity_id.check_status = 'not_compatible'
                        # else:
                        #     if indicator not in (2, 1):
                        #         seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                        #         quotation.opportunity_id.stage_id = seventh_stage_id
                        #         quotation.opportunity_id.check_status = 'not_compatible'
        return res

    # def read(self, fields=None, load='_classic_read'):
    #     print('1')
    #     indicator = 0
    #     res = super(CrmStage, self).read(fields=fields, load=load)
    #     for stagess in self:
    #         # same_stage = self.env['crm.stage'].search([('state', '=', self.state),
    #         #                                            ('sales_status_selection', '=', self.sales_status_selection),
    #         #                                            ('manufacturing_selection', '=', self.manufacturing_selection),
    #         #                                            ('id', '!=', self.id)])
    #         # if len(same_stage) != 0:
    #         #     return res
    #         # else:
    #         pipelines = self.env['crm.lead'].search([])
    #
    #         stages = self.env['crm.stage'].search([], order='sequence desc')
    #         for stage in stages:
    #             for pipeline in pipelines:
    #                 quotations = self.env['sale.order'].search([('opportunity_id', '=', pipeline.id)])
    #                 for quotation in quotations:
    #
    #                     #            ///////////////////////////--quotation count condition--///////////////////
    #                     idss = self.env['crm.stage'].search([]).ids[0]
    #                     seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
    #                     if stagess.sequence <= seq:
    #                         if len(quotations) >= 1 and quotation.state == 'draft':
    #                             new_stage = pipeline.env['crm.stage'].search(
    #                                 [('state', '=', 'sales_status'), ('sales_status_selection', '=', 'draft')],
    #                                 order='id desc', limit=1)
    #                             if new_stage:
    #                                 pipeline.write({'stage_id': new_stage.id})
    #                                 pipeline.check_status = 'compatible'
    #                             else:
    #                                 seq1 = self.env['crm.stage'].search([('id', '=', pipelines.ids[0])]).sequence
    #                                 first_stage_id = self.env['crm.stage'].search(
    #                                     ['|', ('sequence', '=', seq1), ('name', '=', 'New'), ('state', '=', '')])
    #                                 pipeline.write({'stage_id': first_stage_id})
    #                                 pipeline.check_status = 'not_compatible'
    #
    #                         # ///////////////////////////--quotation tentative and final --///////////////////
    #
    #                     if quotation.state == 'tentative approval' or quotation.state == 'final approval':
    #                         idss = self.env['crm.stage'].search([]).ids[1]
    #                         seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
    #                         if stagess.sequence <= seq:
    #
    #                             new_stage = quotation.env['crm.stage'].search([('state', '=', 'sales_status'), (
    #                                 'sales_status_selection', '=', 'tentative/final approval')], order='id desc',
    #                                                                           limit=1)
    #                             if new_stage:
    #                                 quotation.opportunity_id.write({'stage_id': new_stage.id})
    #                                 quotation.opportunity_id.check_status = 'compatible'
    #
    #                             else:
    #                                 second_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
    #                                 quotation.opportunity_id.stage_id = second_stage_id
    #                                 quotation.opportunity_id.check_status = 'not_compatible'
    #
    #                     # ///////////////////////////--quotation Sales Order --///////////////////
    #
    #                     elif quotation.state == 'sale':
    #                         idss = self.env['crm.stage'].search([]).ids[2]
    #                         seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
    #                         if stagess.sequence <= seq:
    #                             new_stage = quotation.env['crm.stage'].search(
    #                                 [('state', '=', 'sales_status'), ('sales_status_selection', '=', 'sale')]
    #                                 , order='id desc', limit=1)
    #                             if new_stage:
    #                                 quotation.opportunity_id.write({'stage_id': new_stage.id})
    #                                 quotation.opportunity_id.check_status = 'compatible'
    #                             else:
    #                                 third_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
    #                                 quotation.opportunity_id.stage_id = third_stage_id
    #                                 quotation.opportunity_id.check_status = 'not_compatible'
    #
    #                         # #            ///////////////////////////--manufacturing confirmed --///////////////////
    #                     delivery_transfer_ids = self.env['stock.picking'].search(
    #                         [('id', 'in', quotation.picking_ids.ids)])
    #                     production_ids = self.env['mrp.production'].search(
    #                         [('id', 'in', quotation.mrp_production_ids.ids)])
    #
    #                     for product in production_ids:
    #                         print(production_ids)
    #                         print(product)
    #                         print(product.state)
    #                         print(quotation.state)
    #                         if product.state == 'confirmed' and quotation.state != 'cancel':
    #                             idss = self.env['crm.stage'].search([]).ids[3]
    #                             seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
    #                             print(stagess.sequence)
    #                             print(seq)
    #                             if stagess.sequence <= seq:
    #                                 print('1')
    #                                 print(stage.state)
    #                                 print(stage.manufacturing_selection)
    #                                 if stage.state == 'manufacturing' and stage.manufacturing_selection == 'confirmed':
    #                                     print('2')
    #                                     for manf in quotation.procurement_group_id.mrp_production_ids:
    #                                         print('3')
    #                                         print(quotation.procurement_group_id.mrp_production_ids)
    #                                         print(manf)
    #                                         print(manf.state)
    #                                         if manf.state == 'confirmed':
    #                                             print('4')
    #                                             quotation.opportunity_id.stage_id = stage.id
    #                                             quotation.opportunity_id.check_status = 'compatible'
    #                                             return res
    #                                 #         else:
    #                                 #             forth_stage_id = self.env['crm.stage'].search(
    #                                 #                 [('sequence', '=', seq)])
    #                                 #             quotation.opportunity_id.stage_id = forth_stage_id
    #                                 #             quotation.opportunity_id.check_status = 'not_compatible'
    #                                 # else:
    #                                 #     forth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
    #                                 #     quotation.opportunity_id.stage_id = forth_stage_id
    #                                 #     quotation.opportunity_id.check_status = 'not_compatible'
    #
    #                             # ///////////////////////////-- operation type manufacturing
    #                             # --/////////////////////////////////////////////////////////////////////////
    #
    #                         manufacture_picking_ids = self.env['stock.picking'].search([
    #                             ('group_id', '=', product.procurement_group_id.id), ('group_id', '!=', False)])
    #
    #                         for product_piking_id in manufacture_picking_ids:
    #                             idss = self.env['crm.stage'].search([]).ids[4]
    #                             seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
    #                             if stagess.sequence <= seq:
    #                                 operation_type = self.env['stock.picking.type'].search(
    #                                     [('id', '=', stage.operation_type_manufacturing.id)]).name
    #                                 if stage.state == 'operation_type_manufacturing' and operation_type == "Store Finished Product" and quotation.state != 'cancel':
    #                                     operation_type_1 = self.env['stock.picking.type'].search(
    #                                         [('id', '=', product_piking_id.picking_type_id.id)]).name
    #                                     if product_piking_id.state == 'done' and operation_type_1 == "Store Finished Product" and product.state == 'done':
    #                                         quotation.opportunity_id.stage_id = stage.id
    #                                         quotation.opportunity_id.check_status = 'compatible'
    #                                         # return res
    #                                     else:
    #                                         fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
    #                                         quotation.opportunity_id.stage_id = fifth_stage_id
    #                                         quotation.opportunity_id.check_status = 'not_compatible'
    #                                         indicator = 1
    #                                 else:
    #                                     fifth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
    #                                     quotation.opportunity_id.stage_id = fifth_stage_id
    #                                     quotation.opportunity_id.check_status = 'not_compatible'
    #                                     indicator = 1
    #
    #                         # ///////////////////////////-- operation type sales-under install --///////////////////
    #
    #                     for delivery_transfer_id in delivery_transfer_ids:
    #                         idss = self.env['crm.stage'].search([]).ids[5]
    #                         seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
    #                         if stagess.sequence <= seq:
    #                             operation_type = self.env['stock.picking.type'].search(
    #                                 [('id', '=', stage.operation_type_sales.id)]).name
    #                             if stage.state == 'operation_type_sales' and operation_type == "Pick" and quotation.state != 'cancel':
    #                                 operation_type_1 = self.env['stock.picking.type'].search(
    #                                     [('id', '=', delivery_transfer_id.picking_type_id.id)]).name
    #                                 if delivery_transfer_id.state == 'done' and operation_type_1 == "Pick":
    #                                     quotation.opportunity_id.stage_id = stage.id
    #                                     quotation.opportunity_id.check_status = 'compatible'
    #                             #     else:
    #                             #         if indicator not in (0, 1):
    #                             #             sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
    #                             #             quotation.opportunity_id.stage_id = sixth_stage_id
    #                             #             quotation.opportunity_id.check_status = 'not_compatible'
    #                             #             indicator = 2
    #                             # else:
    #                             #     if indicator not in (0, 1):
    #                             #         sixth_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
    #                             #         quotation.opportunity_id.stage_id = sixth_stage_id
    #                             #         quotation.opportunity_id.check_status = 'not_compatible'
    #                             #         indicator = 2
    #
    #                             #            ///////////////////////////-- operation type sales-done --///////////////////
    #
    #                         idss = self.env['crm.stage'].search([]).ids[6]
    #                         seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
    #                         if stagess.sequence <= seq:
    #                             operation_type = self.env['stock.picking.type'].search(
    #                                 [('id', '=', stage.operation_type_sales.id)]).name
    #                             if stage.state == 'operation_type_sales' and operation_type == "Delivery Orders" and quotation.state != 'cancel':
    #                                 operation_type_1 = self.env['stock.picking.type'].search(
    #                                     [('id', '=', delivery_transfer_id.picking_type_id.id)]).name
    #                                 if delivery_transfer_id.state == 'done' and operation_type_1 == "Delivery Orders":
    #                                     quotation.opportunity_id.stage_id = stage.id
    #                                     quotation.opportunity_id.check_status = 'compatible'
    #                             #     else:
    #                             #         if indicator not in (2, 1):
    #                             #             seventh_stage_id = self.env['crm.stage'].search(
    #                             #                 [('sequence', '=', seq)])
    #                             #             quotation.opportunity_id.stage_id = seventh_stage_id
    #                             #             quotation.opportunity_id.check_status = 'not_compatible'
    #                             # else:
    #                             #     if indicator not in (2, 1):
    #                             #         seventh_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
    #                             #         quotation.opportunity_id.stage_id = seventh_stage_id
    #                             #         quotation.opportunity_id.check_status = 'not_compatible'
    #
    #     return res

    @api.model
    def create(self, vals):

        stage = super(CrmStage, self).create(vals)
        # print('123')
        # print(stage)
        # stages = self.search([], order='create_date')
        # print(stages)
        # index_of_before_last_stage = len(stages) - 2
        # id_of_before_last_Stage = stages.ids[index_of_before_last_stage]
        # seq_of_before_last_Stage = self.env['crm.stage'].search([('id', '=', id_of_before_last_Stage)]).sequence
        # print(seq_of_before_last_Stage)
        # print('123')
        # order = 0
        # for stage in stages:
        # stage.write({'sequence': 9})
        # order += 1

        same_stage = self.env['crm.stage'].search([('state', '=', stage.state),
                                                   ('sales_status_selection', '=', stage.sales_status_selection),
                                                   ('manufacturing_selection', '=', stage.manufacturing_selection),
                                                   ('id', '!=', stage.id)])
        pipelines = self.env['crm.lead'].search([])
        if len(same_stage) != 0:
            return stage
        else:

            for pipeline in pipelines:
                quotations = self.env['sale.order'].search([('opportunity_id', '=', pipeline.id)])
                for quotation in quotations:
                    #            ///////////////////////////--quotation count condition--///////////////////
                    idss = self.env['crm.stage'].search([]).ids[0]
                    seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                    if stage.sequence <= seq:
                        if len(quotations) >= 1 and quotation.state == 'draft':
                            new_stage = pipeline.env['crm.stage'].search(
                                [('state', '=', 'sales_status'), ('sales_status_selection', '=', 'draft')],
                                order='id desc', limit=1)
                            if new_stage:
                                pipeline.write({'stage_id': new_stage.id})
                                pipeline.check_status = 'compatible'

                    #            ///////////////////////////--quotation sent quotation --///////////////////

                    # if quotation.state == 'sent' and flag < 1:
                    #     flag = 1
                    #     new_stage = quotation.env['crm.stage'].search(
                    #         [('state', '=', 'sales_status'), ('sales_status_selection', '=', 'sent')]
                    #         , order='id desc', limit=1)
                    #     if new_stage:
                    #         quotation.opportunity_id.write({'stage_id': new_stage.id})
                    #         quotation.opportunity_id.check_status = 'compatible'

                    #         ////////////////////////--quotation cancelled --/////////////////////

                    # if quotation.state == 'cancel' and flag < 2:
                    #     flag = 2
                    #     new_stage = quotation.env['crm.stage'].search(
                    #         [('state', '=', 'sales_status'), ('sales_status_selection', '=', 'cancel')]
                    #         , order='id desc', limit=1)
                    #     if new_stage:
                    #         quotation.opportunity_id.write({'stage_id': new_stage.id})
                    #         quotation.opportunity_id.check_status = 'compatible'

                    #            ///////////////////////////--quotation tentative and final --///////////////////

                    if quotation.state == 'tentative approval' or quotation.state == 'final approval':
                        idss = self.env['crm.stage'].search([]).ids[1]
                        seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                        if stage.sequence <= seq:

                            new_stage = quotation.env['crm.stage'].search([('state', '=', 'sales_status'), (
                                'sales_status_selection', '=', 'tentative/final approval')], order='id desc', limit=1)
                            if new_stage:
                                quotation.opportunity_id.write({'stage_id': new_stage.id})
                                quotation.opportunity_id.check_status = 'compatible'

                    #            ///////////////////////////--quotation Sales Order --///////////////////

                    elif quotation.state == 'sale':
                        idss = self.env['crm.stage'].search([]).ids[2]
                        seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                        if stage.sequence <= seq:
                            new_stage = quotation.env['crm.stage'].search(
                                [('state', '=', 'sales_status'), ('sales_status_selection', '=', 'sale')]
                                , order='id desc', limit=1)
                            if new_stage:
                                quotation.opportunity_id.write({'stage_id': new_stage.id})
                                quotation.opportunity_id.check_status = 'compatible'

                    #     #            ///////////////////////////--quotation done --///////////////////
                    #
                    # elif quotation.state == 'done' and flag < 5:
                    #     flag = 5
                    #     new_stage = quotation.env['crm.stage'].search(
                    #         [('state', '=', 'sales_status'), ('sales_status_selection', '=', 'done')]
                    #         , order='id desc', limit=1)
                    #     if new_stage:
                    #         quotation.opportunity_id.write({'stage_id': new_stage.id})
                    #         quotation.opportunity_id.check_status = 'compatible'
                    #
                    # #            ///////////////////////////--manufacturing draft --///////////////////
                    #
                    delivery_transfer_ids = self.env['stock.picking'].search([('id', 'in', quotation.picking_ids.ids)])
                    production_ids = self.env['mrp.production'].search([('id', 'in', quotation.mrp_production_ids.ids)])

                    for product in production_ids:
                        #
                        #     if product.state == 'draft' and flag < 6:
                        #         flag = 6
                        #         new_stage = self.env['crm.stage'].search(
                        #             [('state', '=', 'manufacturing'), ('manufacturing_selection', '=', 'draft')],
                        #             order='id desc', limit=1)
                        #         if new_stage:
                        #             if quotation.opportunity_id.stage_id.id != new_stage.id:
                        #                 quotation.opportunity_id.stage_id = new_stage.id
                        #                 quotation.opportunity_id.check_status = 'compatible'
                        #
                        #     #            ///////////////////////////--manufacturing approve --///////////////////
                        #
                        #     elif product.state == 'approve' and flag < 7:
                        #         flag = 7
                        #         new_stage = self.env['crm.stage'].search(
                        #             [('state', '=', 'manufacturing'), ('manufacturing_selection', '=', 'approve')],
                        #             order='id desc', limit=1)
                        #         if new_stage:
                        #             if quotation.opportunity_id.stage_id.id != new_stage.id:
                        #                 quotation.opportunity_id.stage_id = new_stage.id
                        #                 quotation.opportunity_id.check_status = 'compatible'
                        #
                        #            ///////////////////////////--manufacturing confirmed --///////////////////

                        if product.state == 'confirmed':
                            idss = self.env['crm.stage'].search([]).ids[3]
                            seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                            if stage.sequence <= seq:
                                stages = self.env['crm.stage'].search([], order='sequence desc')
                                for stage in stages:
                                    if stage.state == 'manufacturing' and stage.manufacturing_selection == 'confirmed' and quotation.state != 'cancel':
                                        for manf in self.procurement_group_id.mrp_production_ids:
                                            if manf.state == 'confirmed':
                                                quotation.opportunity_id.stage_id = stage.id
                                                quotation.opportunity_id.check_status = 'compatible'
                        #
                        #     #            ///////////////////////////--manufacturing done --///////////////////
                        #
                        #     elif product.state == 'done' and flag < 9:
                        #         flag = 9
                        #         new_stage = self.env['crm.stage'].search(
                        #             [('state', '=', 'manufacturing'), ('manufacturing_selection', '=', 'done')],
                        #             order='id desc', limit=1)
                        #         if new_stage:
                        #             if quotation.opportunity_id.stage_id.id != new_stage.id:
                        #                 quotation.opportunity_id.stage_id = new_stage.id
                        #                 quotation.opportunity_id.check_status = 'compatible'
                        #
                        #     #            ///////////////////////////--manufacturing cancel --////////////////////
                        #
                        #     elif product.state == 'cancel' and flag < 10:
                        #         flag = 10
                        #         new_stage = self.env['crm.stage'].search(
                        #             [('state', '=', 'manufacturing'), ('manufacturing_selection', '=', 'cancel')],
                        #             order='id desc', limit=1)
                        #         if new_stage:
                        #             if quotation.opportunity_id.stage_id.id != new_stage.id:
                        #                 quotation.opportunity_id.stage_id = new_stage.id
                        #                 quotation.opportunity_id.check_status = 'compatible'
                        #
                        manufacture_picking_ids = self.env['stock.picking'].search([
                            ('group_id', '=', product.procurement_group_id.id), ('group_id', '!=', False)])
                        #
                        #            ///////////////////////////-- operation type manufacturing --///////////////////

                        for product_piking_id in manufacture_picking_ids:
                            idss = self.env['crm.stage'].search([]).ids[4]
                            seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                            if stage.sequence <= seq:
                                stages = self.env['crm.stage'].search([], order='sequence desc')
                                for stage in stages:
                                    operation_type = self.env['stock.picking.type'].search(
                                        [('id', '=', stage.operation_type_manufacturing.id)]).name
                                    if stage.state == 'operation_type_manufacturing' and operation_type == "Store Finished Product" and quotation.state != 'cancel':
                                        operation_type_1 = self.env['stock.picking.type'].search(
                                            [('id', '=', product_piking_id.picking_type_id.id)]).name
                                        if product_piking_id.state == 'done' and operation_type_1 == "Store Finished Product" and product.state == 'done':
                                            quotation.opportunity_id.stage_id = stage.id
                                            quotation.opportunity_id.check_status = 'compatible'

                        # ///////////////////////////-- operation type sales-under install --///////////////////

                        for delivery_transfer_id in delivery_transfer_ids:
                            idss = self.env['crm.stage'].search([]).ids[5]
                            seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                            if stage.sequence <= seq:
                                stages = self.env['crm.stage'].search([], order='sequence desc')
                                for stage in stages:
                                    operation_type = self.env['stock.picking.type'].search(
                                        [('id', '=', stage.operation_type_sales.id)]).name
                                    if stage.state == 'operation_type_sales' and operation_type == "Pick" and quotation.state != 'cancel':
                                        operation_type_1 = self.env['stock.picking.type'].search(
                                            [('id', '=', delivery_transfer_id.picking_type_id.id)]).name
                                        if delivery_transfer_id.state == 'done' and operation_type_1 == "Pick":
                                            quotation.opportunity_id.stage_id = stage.id
                                            quotation.opportunity_id.check_status = 'compatible'

                            #            ///////////////////////////-- operation type sales-done --///////////////////

                            idss = self.env['crm.stage'].search([]).ids[6]
                            seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
                            if stage.sequence <= seq:
                                stages = self.env['crm.stage'].search([], order='sequence desc')
                                for stage in stages:
                                    operation_type = self.env['stock.picking.type'].search(
                                        [('id', '=', stage.operation_type_sales.id)]).name
                                    if stage.state == 'operation_type_sales' and operation_type == "Delivery Orders" and quotation.state != 'cancel':
                                        operation_type_1 = self.env['stock.picking.type'].search(
                                            [('id', '=', delivery_transfer_id.picking_type_id.id)]).name
                                        if delivery_transfer_id.state == 'done' and operation_type_1 == "Delivery Orders":
                                            quotation.opportunity_id.stage_id = stage.id
                                            quotation.opportunity_id.check_status = 'compatible'

        return stage
