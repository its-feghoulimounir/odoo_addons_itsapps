# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    customers_count = fields.Integer(
        string="Clients",
        compute="_compute_customers_count",
        help="Sociétés explicitement affectées (même sans ventes) + personnes racine avec au moins une ligne de vente. Adresses exclues."
    )

    def _get_explicit_partner_ids(self):
        """IDs des partenaires (toute fiche) ayant property_product_pricelist explicitement affectée à self."""
        self.ensure_one()
        IrProperty = self.env['ir.property'].sudo()
        value_ref = 'product.pricelist,%d' % self.id
        company_ids = [self.company_id.id] if self.company_id else (self.env.companies.ids + [False])
        props = IrProperty.search([
            ('name', '=', 'property_product_pricelist'),
            ('value_reference', '=', value_ref),
            ('res_id', '!=', False),
            ('company_id', 'in', company_ids),
        ])

        ids_ = []
        for p in props:
            if p.res_id and p.res_id.startswith('res.partner,'):
                try:
                    ids_.append(int(p.res_id.split(',')[1]))
                except Exception:
                    continue
        if not ids_:
            return []
        partners = self.env['res.partner'].search([('id', 'in', ids_), ('customer_rank', '>', 0)])
        return partners.ids

    def _commercial_partner_ids(self, partner_ids):
        if not partner_ids:
            return []
        partners = self.env['res.partner'].browse(partner_ids)
        return list({p.commercial_partner_id.id for p in partners})

    def _commercial_partners_with_sales_lines(self, commercial_ids):
        self.ensure_one()
        if not commercial_ids:
            return set()

        SaleOrder = self.env['sale.order'].sudo()
        SaleOrderLine = self.env['sale.order.line'].sudo()

        order_domain = [('state', '!=', 'cancel')]
        if self.company_id:
            order_domain.append(('company_id', '=', self.company_id.id))
        order_domain.extend(['|','|',
                             ('partner_id.commercial_partner_id', 'in', commercial_ids),
                             ('partner_invoice_id.commercial_partner_id', 'in', commercial_ids),
                             ('partner_shipping_id.commercial_partner_id', 'in', commercial_ids)])
        orders = SaleOrder.search(order_domain)
        if not orders:
            return set()

        groups = SaleOrderLine.read_group(
            [('order_id', 'in', orders.ids)],
            ['order_id'],
            ['order_id'],
        )
        orders_with_lines = {g['order_id'][0] for g in groups if g.get('order_id')}
        if not orders_with_lines:
            return set()

        res = set()
        for o in orders:
            if o.id not in orders_with_lines:
                continue
            for p in (o.partner_id, o.partner_invoice_id, o.partner_shipping_id):
                cid = p.commercial_partner_id.id
                if cid in commercial_ids:
                    res.add(cid)
        return res

    def _compute_customers_count(self):
        for pricelist in self:
            explicit = pricelist._get_explicit_partner_ids()
            commercials = pricelist._commercial_partner_ids(explicit)
            if not commercials:
                pricelist.customers_count = 0
                continue
            partners = self.env['res.partner'].browse(commercials)
            company_ids = {p.id for p in partners if p.parent_id.id is False and p.is_company}
            person_root_ids = {p.id for p in partners if p.parent_id.id is False and not p.is_company}
            with_lines = pricelist._commercial_partners_with_sales_lines(list(person_root_ids | company_ids))
            final_ids = company_ids | (with_lines & person_root_ids)
            pricelist.customers_count = len(final_ids)

    def action_view_customers(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_partner_form")

        explicit = self._get_explicit_partner_ids()
        commercials = self._commercial_partner_ids(explicit)

        partners = self.env['res.partner'].browse(commercials)
        company_ids = {p.id for p in partners if p.parent_id.id is False and p.is_company}
        person_root_ids = {p.id for p in partners if p.parent_id.id is False and not p.is_company}

        with_lines = self._commercial_partners_with_sales_lines(list(person_root_ids | company_ids))

        final_ids = list(company_ids | (with_lines & person_root_ids))

        ctx = dict(self.env.context or {})
        ctx.update({
            "default_property_product_pricelist": self.id,
        })

        action.update({
            "domain": [
                ('id', 'in', final_ids or [0]),
                ('parent_id', '=', False),
            ],
            "context": ctx,
        })
        return action
