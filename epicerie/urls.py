from django.urls import path
from epicerie.views import Connexion, deconnexion, accueil, produit_list, Produitvendu,\
    SaveProduit, SaveStock, Stock, ModProduit, supp_stock, supp_produit, supp_vente,\
    supp_tout_vente, total, PrixTotal, ModStock, list_total, supp_total, inventaire,\
    supp_tout, save_inventaire

urlpatterns = [
    path('', Connexion.as_view(), name='connexion'),
    path('deconnexion', deconnexion, name='deconnexion'),
    path('accueil', accueil, name='accueil'),
    path('enregistrement/', Produitvendu.as_view(), name='enregistrement'),
    path('produit/', produit_list, name='produit_list'),
    path('enregistre_produit/', SaveProduit.as_view(), name='enregistre_produit'),
    path('stock_enregistrement/', SaveStock.as_view(), name='stock_enregistrement'),
    path('stock/', Stock.as_view(), name='stock_produit'),
    path('mod_produit/<int:id_pro>', ModProduit.as_view(), name='mod_produit'),
    path('supp_produit/<int:id_pro>', supp_produit, name='supp_produit'),
    path('supp_vente/', supp_vente, name='supp_vente'),
    path('supp_tout_vente/', supp_tout_vente, name='supp_tout_vente'),
    path('supp_stock', supp_stock, name='supp_stock'),
    path('total', total, name='total'),
    path('prix_total', PrixTotal.as_view(), name='calcul_total_2date'),
    path('mod_stock/<int:id_stock>', ModStock.as_view(), name='mod_stock'),
    path('total_list/', list_total, name='list_total'),
    path('supp_total/', supp_total, name='supp_total'),
    path('inventaire/', inventaire, name='inventaire'),
    path('inventaire/Supprimer', supp_tout, name='supp_tout'),
    path('inventaire/ajouter', save_inventaire.as_view(), name='ajouter_inventaire'),
]
