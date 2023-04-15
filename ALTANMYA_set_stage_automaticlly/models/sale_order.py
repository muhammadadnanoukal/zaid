from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    opportunity_id = fields.Many2one('crm.lead', string='Opportunity')

    def unlink(self):
        opportunity_id = self.opportunity_id
        res = super().unlink()
        # Not guaranteed to trigger the constraint
        opportunity_id._compute_quotation_count()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        idss = self.env['crm.stage'].search([]).ids[0]
        seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
        if res.opportunity_id.stage_id.sequence <= seq:
            new_stage_id = self.env['crm.stage'].search(
                [('state', '=', 'sales_status'), ('sales_status_selection', '=', 'draft')], order='id desc', limit=1)
            if self._context:
                if self._context.get('default_opportunity_id'):
                    check_quotations = self.env['crm.lead'].search(
                        [('id', '=', self._context['default_opportunity_id'])]).quotation_ids.ids
                    if new_stage_id:
                        if len(check_quotations) >= 1 and res.state == 'draft':
                            res.opportunity_id.check_status = 'compatible'
                            res.opportunity_id.write({'stage_id': new_stage_id.id})
                    else:
                        first_stage_id = self.env['crm.stage'].search(
                            ['|', ('sequence', '=', seq), ('name', '=', 'New'), ('state', '=', '')])
                        self.opportunity_id.stage_id = first_stage_id
                        res.opportunity_id.check_status = 'not_compatible'
        return res

    def action_tentative_confirm(self):
        super().action_tentative_confirm()
        idss = self.env['crm.stage'].search([]).ids[1]
        seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
        if self.opportunity_id.stage_id.sequence <= seq:
            for rec in self:
                stages = self.env['crm.stage'].search([], order='sequence desc')

                for stage in stages:
                    if stage.state == 'sales_status' and stage.sales_status_selection == 'tentative/final approval':
                        rec.opportunity_id.stage_id = stage.id
                        rec.opportunity_id.check_status = 'compatible'
                        return

                    else:
                        second_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                        rec.opportunity_id.stage_id = second_stage_id
                        rec.opportunity_id.check_status = 'not_compatible'
                        # if self._context:
                        #     if self._context.get('default_opportunity_id'):
                        #         check_quotations = self.env['crm.lead'].search(
                        #             [('id', '=', self._context['default_opportunity_id'])]).quotation_ids.ids
                        #         if stage.state == 'sales_status' and stage.sales_status_selection == 'draft':
                        #             if len(check_quotations) >= 1:
                        #                 rec.opportunity_id.check_status = 'compatible'
                        #                 rec.opportunity_id.write({'stage_id': stage.id})
                        #         else:
                        #             rec.opportunity_id._compute_quotation_count()
                        #             rec.opportunity_id.check_status = 'not_compatible'

    def action_final_confirm(self):
        super().action_final_confirm()
        idss = self.env['crm.stage'].search([]).ids[1]
        seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
        if self.opportunity_id.stage_id.sequence <= seq:
            for rec in self:
                stages = self.env['crm.stage'].search([], order='sequence desc')

                for stage in stages:
                    if stage.state == 'sales_status' and stage.sales_status_selection == 'tentative/final approval':
                        rec.opportunity_id.stage_id = stage.id
                        rec.opportunity_id.check_status = 'compatible'
                        return

                    else:
                        second_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                        rec.opportunity_id.stage_id = second_stage_id
                        rec.opportunity_id.check_status = 'not_compatible'
                        # if self._context:
                        #     if self._context.get('default_opportunity_id'):
                        #         check_quotations = self.env['crm.lead'].search(
                        #             [('id', '=', self._context['default_opportunity_id'])]).quotation_ids.ids
                        #         if stage.state == 'sales_status' and stage.sales_status_selection == 'draft':
                        #             if len(check_quotations) >= 1:
                        #                 rec.opportunity_id.check_status = 'compatible'
                        #                 rec.opportunity_id.write({'stage_id': stage.id})
                        #         else:
                        #             rec.opportunity_id._compute_quotation_count()
                        #             rec.opportunity_id.check_status = 'not_compatible'

    def action_confirm(self):
        super().action_confirm()
        idss = self.env['crm.stage'].search([]).ids[2]
        seq = self.env['crm.stage'].search([('id', '=', idss)]).sequence
        if self.opportunity_id.stage_id.sequence - 1 <= seq:
            for rec in self:
                stages = self.env['crm.stage'].search([], order='sequence desc')
                for stage in stages:
                    if stage.state == 'sales_status' and stage.sales_status_selection == 'sale':
                        rec.opportunity_id.check_status = 'compatible'
                        rec.opportunity_id.stage_id = stage.id
                        return
                    else:
                        third_stage_id = self.env['crm.stage'].search([('sequence', '=', seq)])
                        rec.opportunity_id.stage_id = third_stage_id
                        rec.opportunity_id.check_status = 'not_compatible'

                # if rec.mrp_production_ids:
                #     for rec1 in rec.mrp_production_ids:
                #         if rec1.state == 'draft':
                #             for stage in stages:
                #                 if stage.state == 'manufacturing' and stage.manufacturing_selection == 'draft':
                #                     if rec.opportunity_id.id:
                #                         if rec.opportunity_id.stage_id.id != stage.id:
                #                             rec.opportunity_id.check_status = 'compatible'
                #                             rec.opportunity_id.stage_id = stage.id
                #                 # else:
                #                 #     if stage.state == 'sales_status' and stage.sales_status_selection == 'sale':
                #                 #
                #                 #         rec.opportunity_id.check_status = 'compatible'
                #                 #         rec.opportunity_id.stage_id = stage.id
                #                 #     else:
                #                 #
                #                 #         """get the final approval to here"""
                #                 #         "///////////////////////////////////////////////////////////////////////////////////"
                #                 #
                #                 #         if stage.state == 'sales_status' and stage.sales_status_selection == 'tentative/final approval':
                #                 #
                #                 #             rec.opportunity_id.stage_id = stage.id
                #                 #             rec.opportunity_id.check_status = 'compatible'
                #                 #
                #                 #         else:
                #                 #             if self._context:
                #                 #                 if self._context.get('default_opportunity_id'):
                #                 #                     check_quotations = self.env['crm.lead'].search(
                #                 #                         [('id', '=',
                #                 #                           self._context['default_opportunity_id'])]).quotation_ids.ids
                #                 #                     if stage.state == 'sales_status' and stage.sales_status_selection == 'draft':
                #                 #                         if len(check_quotations) >= 1:
                #                 #                             rec.opportunity_id.check_status = 'compatible'
                #                 #                             rec.opportunity_id.write({'stage_id': stage.id})
                #                 #                     else:
                #                 #                         rec.opportunity_id._compute_quotation_count()
                #                 #                         rec.opportunity_id.check_status = 'not_compatible'
                #                 #         rec.opportunity_id.check_status = 'not_compatible'

                # elif rec.picking_ids:
                #     for rec1 in rec.picking_ids:
                #         if rec1.state == 'draft':
                #             for stage in stages:
                #                 if stage.state == 'Operation Type-Sale':
                #                     if rec.opportunity_id.id:
                #                         if rec.opportunity_id.stage_id.id != stage.id:
                #                             rec.opportunity_id.check_status = 'compatible'
                #                             rec.opportunity_id.stage_id = stage.id

                # else:
                #     for stage in stages:
                #         if stage.state == 'sales_status' and stage.sales_status_selection == 'sale':
                #             rec.opportunity_id.check_status = 'compatible'
                #             rec.opportunity_id.stage_id = stage.id
                #         # else:
                #         #
                #         #     """get the final approval to here"""
                #         #     "/////////////////////////////////////////////////"
                #         #
                #         #     if stage.state == 'sales_status' and stage.sales_status_selection == 'tentative/final approval':
                #         #
                #         #         rec.opportunity_id.stage_id = stage.id
                #         #         rec.opportunity_id.check_status = 'compatible'
                #         #
                #         #     else:
                #         #         if self._context:
                #         #             if self._context.get('default_opportunity_id'):
                #         #                 check_quotations = self.env['crm.lead'].search(
                #         #                     [('id', '=', self._context['default_opportunity_id'])]).quotation_ids.ids
                #         #                 if stage.state == 'sales_status' and stage.sales_status_selection == 'draft':
                #         #                     if len(check_quotations) >= 1:
                #         #                         rec.opportunity_id.check_status = 'compatible'
                #         #                         rec.opportunity_id.write({'stage_id': stage.id})
                #         #                 else:
                #         #                     rec.opportunity_id._compute_quotation_count()
                #         #                     rec.opportunity_id.check_status = 'not_compatible'
                #         #     rec.opportunity_id.check_status = 'not_compatible'

    # def action_cancel(self):
    #     res = super().action_cancel()
    #     new_stage = self.env['crm.stage'].search(
    #         [('state', '=', 'sales_status'), ('sales_status_selection', '=', 'cancel')], order='id desc', limit=1)
    #     if new_stage:
    #
    #         self.opportunity_id.check_status = 'compatible'
    #         self.opportunity_id.stage_id = new_stage.id
    #     else:
    #         stage_seq = len(self.env['crm.stage'].search([])) - 1
    #         self.opportunity_id.check_status = 'not_compatible'
    #         self.opportunity_id.stage_id = self.env['crm.stage'].search(
    #             [('sequence', '=', stage_seq)], order='id desc', limit=1).id
    #     return res
    #
    # def action_quotation_send(self):
    #     res = super().action_quotation_send()
    #     stages = self.env['crm.stage'].search([], order='sequence desc')
    #     for stage in stages:
    #         if stage.state == 'sales_status' and stage.sales_status_selection == 'sent':
    #             self.opportunity_id.check_status = 'compatible'
    #             self.opportunity_id.stage_id = stage.id
    #             return res
    #         # else:
    #
    #         # if self._context:
    #         #     if self._context.get('default_opportunity_id'):
    #         #         check_quotations = self.env['crm.lead'].search(
    #         #             [('id', '=', self._context['default_opportunity_id'])]).quotation_ids.ids
    #         #         if stage.state == 'sales_status' and stage.sales_status_selection == 'draft':
    #         #             if len(check_quotations) >= 1:
    #         #                 self.opportunity_id.check_status = 'not_compatible'
    #         #                 self.opportunity_id.write({'stage_id': stage.id})
    #         #                 return res
    #         #
    #         #         else:
    #         #             self.opportunity_id.check_status = 'not_compatible'
    #         #             return res
    #
    # def action_draft(self):
    #     res = super().action_draft()
    #
    #     stages = self.env['crm.stage'].search([], order='sequence desc')
    #     for stage in stages:
    #
    #         if stage.state == 'sales_status' and stage.sales_status_selection == 'draft':
    #             self.opportunity_id.check_status = 'compatible'
    #             self.opportunity_id.stage_id = stage.id
    #             return res
    #         # else:
    #
    #         # if self._context:
    #         #     if self._context.get('default_opportunity_id'):
    #         #         check_quotations = self.env['crm.lead'].search(
    #         #             [('id', '=', self._context['default_opportunity_id'])]).quotation_ids.ids
    #         #         if stage.state == 'sales_status' and stage.sales_status_selection == 'draft':
    #         #
    #         #             if len(check_quotations) >= 1:
    #         #                 self.opportunity_id.check_status = 'not_compatible'
    #         #                 self.opportunity_id.write({'stage_id': stage.id})
    #         #
    #         #         else:
    #         #
    #         #             self.opportunity_id.check_status = 'not_compatible'
    #
    # def action_done(self):
    #     res = super().action_done()
    #     stages = self.env['crm.stage'].search([], order='sequence desc')
    #     for stage in stages:
    #         if stage.state == 'sales_status' and stage.sales_status_selection == 'done':
    #             self.opportunity_id.check_status = 'compatible'
    #             self.opportunity_id.stage_id = stage.id
    #             return res
    #         # else:
    #
    #         # if stage.state == 'sales_status' and stage.sales_status_selection == 'sale':
    #         #     self.opportunity_id.check_status = 'not_compatible'
    #         #     self.opportunity_id.write({'stage_id': stage.id})
    #         #
    #         # else:
    #         #     '/////////////////////////////////////////////////'
    #         #     for rec in self:
    #         #         stages = self.env['crm.stage'].search([], order='sequence desc')
    #         #
    #         #         if rec.mrp_production_ids:
    #         #
    #         #             for rec1 in rec.mrp_production_ids:
    #         #                 if rec1.state == 'draft':
    #         #                     for stage in stages:
    #         #                         if stage.state == 'manufacturing' and stage.manufacturing_selection == 'draft':
    #         #                             if rec.opportunity_id.id:
    #         #                                 if rec.opportunity_id.stage_id.id != stage.id:
    #         #                                     rec.opportunity_id.check_status = 'compatible'
    #         #                                     rec.opportunity_id.stage_id = stage.id
    #         #                         else:
    #         #                             if stage.state == 'sales_status' and stage.sales_status_selection == 'sale':
    #         #
    #         #                                 rec.opportunity_id.check_status = 'compatible'
    #         #                                 rec.opportunity_id.stage_id = stage.id
    #         #                             else:
    #         #
    #         #                                 """get the final approval to here"""
    #         #                                 "///////////////////////////////////////////////////////////////////////////////////"
    #         #
    #         #                                 if stage.state == 'sales_status' and stage.sales_status_selection == 'tentative/final approval':
    #         #
    #         #                                     rec.opportunity_id.stage_id = stage.id
    #         #                                     rec.opportunity_id.check_status = 'compatible'
    #         #
    #         #                                 else:
    #         #                                     if self._context:
    #         #                                         if self._context.get('default_opportunity_id'):
    #         #                                             check_quotations = self.env['crm.lead'].search(
    #         #                                                 [('id', '=',
    #         #                                                   self._context[
    #         #                                                       'default_opportunity_id'])]).quotation_ids.ids
    #         #                                             if stage.state == 'sales_status' and stage.sales_status_selection == 'draft':
    #         #                                                 if len(check_quotations) >= 1:
    #         #                                                     rec.opportunity_id.check_status = 'compatible'
    #         #                                                     rec.opportunity_id.write({'stage_id': stage.id})
    #         #                                             else:
    #         #                                                 rec.opportunity_id._compute_quotation_count()
    #         #                                                 rec.opportunity_id.check_status = 'not_compatible'
    #         #                                 rec.opportunity_id.check_status = 'not_compatible'
    #         #
    #         #         else:
    #         #             for stage in stages:
    #         #                 if stage.state == 'sales_status' and stage.sales_status_selection == 'sale':
    #         #
    #         #                     rec.opportunity_id.check_status = 'compatible'
    #         #                     rec.opportunity_id.stage_id = stage.id
    #         #                 else:
    #         #
    #         #                     """get the final approval to here"""
    #         #                     "/////////////////////////////////////////////////"
    #         #
    #         #                     if stage.state == 'sales_status' and stage.sales_status_selection == 'tentative/final approval':
    #         #
    #         #                         rec.opportunity_id.stage_id = stage.id
    #         #                         rec.opportunity_id.check_status = 'compatible'
    #         #
    #         #                     else:
    #         #                         if self._context:
    #         #                             if self._context.get('default_opportunity_id'):
    #         #                                 check_quotations = self.env['crm.lead'].search(
    #         #                                     [(
    #         #                                      'id', '=', self._context['default_opportunity_id'])]).quotation_ids.ids
    #         #                                 if stage.state == 'sales_status' and stage.sales_status_selection == 'draft':
    #         #                                     if len(check_quotations) >= 1:
    #         #                                         rec.opportunity_id.check_status = 'compatible'
    #         #                                         rec.opportunity_id.write({'stage_id': stage.id})
    #         #                                 else:
    #         #                                     rec.opportunity_id._compute_quotation_count()
    #         #                                     rec.opportunity_id.check_status = 'not_compatible'
    #         #                     rec.opportunity_id.check_status = 'not_compatible'
