
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    customers_count = fields.Integer(
        string="Customers",
        compute="_compute_customers_count",
        help="Number of customers whose effective pricelist equals this one (company-dependent resolution).",
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _customers_action_context(self):
        self.ensure_one()
        ctx = dict(self.env.context or {})
        # Resolve company-dependent fields in the pricelist's company
        if self.company_id:
            ctx["allowed_company_ids"] = [self.company_id.id]
        return ctx

    def _customers_domain(self):
        """Domain to fetch top-level active customers for this pricelist.

        Precedence (if custom field exists on res.partner):
          1) specific_property_product_pricelist == self.id
          2) OR (specific_property_product_pricelist is False AND property_product_pricelist == self.id)

        Otherwise: property_product_pricelist == self.id

        Always restrict to:
          - active customers
          - customer_rank > 0
          - top-level only (companies or contacts without parent)
        """
        self.ensure_one()
        base = [
            ("active", "=", True),
            ("customer_rank", ">", 0),
            "|", ("parent_id", "=", False), ("is_company", "=", True),
        ]
        Partner = self.env["res.partner"]
        has_specific = "specific_property_product_pricelist" in Partner._fields
        if has_specific:
            domain = base + [
                "|",
                ("specific_property_product_pricelist", "=", self.id),
                "&",
                ("specific_property_product_pricelist", "=", False),
                ("property_product_pricelist", "=", self.id),
            ]
        else:
            domain = base + [("property_product_pricelist", "=", self.id)]
        return domain

    # ------------------------------------------------------------------
    # Computed fields / Actions
    # ------------------------------------------------------------------
    @api.depends("company_id")
    def _compute_customers_count(self):
        for pricelist in self:
            if not pricelist.id:
                pricelist.customers_count = 0
                continue
            Partner = self.env["res.partner"].with_context(pricelist._customers_action_context())
            domain = pricelist._customers_domain()
            try:
                groups = Partner.read_group(domain, ["commercial_partner_id"], ["commercial_partner_id"]) or []
                pricelist.customers_count = len(groups)
            except Exception:
                pricelist.customers_count = Partner.search_count(domain)

    def action_open_customers(self):
        self.ensure_one()
        action = self.env.ref("pricelist_customers_button.action_pricelist_customers").read()[0]
        # Domain for immediate result is defined on the ir.actions.act_window itself.
        # Provide context for company-dependent resolution and pricelist id.
        ctx = self._customers_action_context()
        ctx.update({
            "pricelist_id": self.id,
            "active_id": self.id,
            "active_ids": [self.id],
            "active_model": "product.pricelist",
        })
        action["context"] = ctx
        action["name"] = f"Clients — {self.display_name}"
        return action
        try:
            from lxml import etree
            arch = res.get("arch") or ""
            if not arch:
                return res
            root = etree.fromstring(arch.encode("utf-8"))
            if root.tag not in ("list", "tree"):
                return res
            # don't duplicate
            if root.xpath(".//button[@name='action_open_customers']"):
                res["arch"] = etree.tostring(root, encoding="unicode")
                return res
            # create the button (standard Odoo style)
            btn = etree.Element("button", {
                "name": "action_open_customers",
                "type": "object",
                "string": "Clients",
                "class": "btn-link",
                "icon": "fa-user",
            })
            # place after the 'name' column if present
            anchor = root.xpath(".//field[@name='name']")
            if anchor:
                idx = root.index(anchor[0])
                root.insert(idx + 1, btn)
            else:
                root.append(btn)
            res["arch"] = etree.tostring(root, encoding="unicode")
        except Exception:
            # if anything fails, keep original view
            return res
        return res
