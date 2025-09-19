# Pricelist Customers Smart Button — Odoo 18

Ajoute un bouton **Clients** sur les listes de prix pour ouvrir, en un clic, les partenaires **réellement** concernés, tout en filtrant les contacts enfants et en respectant le multi‑sociétés.

---

## Fonctionnalités

- **Smart button “Clients”** dans la vue *form* de la liste de prix (compteur inclus).
- **Bouton “Clients” en fin de ligne** dans la vue *list* des listes de prix.
- **Filtrage métier précis** des partenaires liés à une liste de prix (LP), avec priorité au champ `specific_property_product_pricelist` lorsqu’il est présent (Odoo 18).
- **Compatibilité multi‑sociétés** : la résolution des champs dépendants de société suit le contexte (`allowed_company_ids`).

---

## Règles d’affichage (résumé)

- **Actifs & clients** : uniquement `active = True` et `customer_rank > 0`.
- **Niveau affiché** : afficher uniquement les **sociétés** (`is_company = True`) ou les **contacts racine** (`parent_id = False`).  
  Les adresses filles (facturation/expédition) **ne sont jamais** listées.
- **Périmètre LP (priorité Odoo 18)** :  
  1) si `specific_property_product_pricelist` existe : afficher si  
  `specific_property_product_pricelist = pricelist_id` **OU**  
  (`specific_property_product_pricelist` vide **ET** `property_product_pricelist = pricelist_id`);  
  2) sinon : afficher si `property_product_pricelist = pricelist_id`.
- **Multi‑sociétés** : le contexte de société de la LP pilote la résolution des champs.

---

## UI ajoutée

- **Vue formulaire LP** : smart button `oe_stat_button` + `statinfo` (icône `fa-user`, compteur `customers_count`).
- **Vue liste LP** (`product.product_pricelist_view_list`) : bouton **“Clients”** en **fin de ligne**, `type="object"`, `class="btn-link"`, `icon="fa-user"`.

---

## Compatibilité Odoo 18

- **Modèle de propriétés** : les champs dépendants de société sont stockés/résolus via le contexte de société.
- **Types de vues** : utiliser `list` (et non `tree`) pour éviter l’erreur *“View types not defined tree”*.

---

## Installation

1. Déposez le module `pricelist_customers_button` dans votre répertoire `addons`.
2. Mettez à jour la liste des modules et installez‑le depuis **Applications**.
3. Donnez accès aux utilisateurs concernés (Menus Ventes / Produits).

**Dépendances recommandées :** `product` (base des listes de prix).  
**Version Odoo :** 18.0.

---

## Configuration

Aucune configuration obligatoire. Vérifiez simplement que :

- Vos **listes de prix** sont actives et cohérentes par société ;
- Le **contexte de société** de l’utilisateur inclut bien la/les société(s) visée(s) (multi‑sociétés).

---

## Utilisation

1. Ouvrez **Ventes → Produits → Listes de prix**.  
2. Depuis la **vue liste**, cliquez sur **Clients** au bout de la ligne souhaitée **ou** ouvrez la LP en **vue formulaire** et cliquez sur le **smart button Clients**.  
3. La vue des partenaires s’ouvre **déjà filtrée** selon les règles ci‑dessus.
