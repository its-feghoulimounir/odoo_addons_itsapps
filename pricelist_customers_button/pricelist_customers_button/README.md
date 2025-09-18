# Pricelist Customers Smart Button (Odoo 17)

## Objectif
Ouvrir en un clic la liste des clients pertinents pour une liste de prix, avec des règles métier claires et utiles pour le CRM/ventes.

## Règles d’affichage
- **Affectation explicite uniquement** via `property_product_pricelist` (pas d’héritage par défaut société).
- **Entités commerciales uniquement** (commercial partner) : adresses/contacts enfants exclus.
- **Sociétés** (root, `is_company=True`) : visibles même sans ventes si la LP est explicitement affectée (directement ou via un enfant).
- **Personnes racine** (root, `is_company=False`) : visibles uniquement si elles ont ≥ 1 **ligne** de vente (commande non annulée) où elles apparaissent en client/facturation/livraison.
- **Multi-sociétés** : si la LP est liée à une société, les commandes prises en compte sont filtrées sur `company_id`.

## Installation
1. Copier le module dans vos addons custom.
2. Mettre à jour la liste des applis et installer le module.

## Utilisation
- Depuis la **vue formulaire** d’une liste de prix, utilisez le smart button **Clients**.
- Depuis la **vue liste**, cliquez sur le bouton **Clients** sur la ligne souhaitée.

## Méthode de test
1. Créez une LP-A.
2. Créez: une société **ACME** (sans ventes), une personne **John Root** (sans ventes), une personne **Jane Root** (avec 1 commande non annulée et 1 ligne).
3. Affectez **LP-A explicitement** sur ACME/une de ses adresses, John, Jane.
4. Ouvrez LP-A → bouton **Clients** :
   - **ACME** visible (société affectée, même sans ventes).
   - **John Root** invisible (pas de ligne).
   - **Jane Root** visible (≥ 1 ligne).
5. Supprimez la seule ligne de Jane → **Jane Root** devient invisible.
