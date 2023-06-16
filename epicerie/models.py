from django.db import models


class Categorie(models.Model):
    id_categorie = models.IntegerField(verbose_name='ID', auto_created=True, primary_key=True)
    nom_categorie = models.CharField(max_length=10, blank=False)


class Produit(models.Model):
    id_produit = models.IntegerField(verbose_name='ID', auto_created=True, primary_key=True)
    categorie = models.ForeignKey(Categorie, blank=False, on_delete=models.CASCADE)
    nom_produit = models.CharField(max_length=100, blank=False)
    prix_produit = models.IntegerField(blank=False)


class Vendre(models.Model):
    id_vendre = models.IntegerField(verbose_name='ID', auto_created=True, primary_key=True)
    produit = models.ForeignKey(Produit, blank=True, on_delete=models.CASCADE, null=True)
    quantite_vendre = models.FloatField(blank=True, null=True)
    prix_total_vendre = models.IntegerField(blank=False)
    date_vendre = models.DateField(blank=False)


class StockProduit(models.Model):
    id_stock = models.IntegerField(verbose_name='ID', auto_created=True, primary_key=True)
    produit = models.ForeignKey(Produit, blank=False, on_delete=models.CASCADE)
    quantite_stock = models.FloatField(blank=False)
    prix_total = models.IntegerField(blank=False)
    date_stock = models.DateField(blank=True)


class TotalStock(models.Model):
    id_total = models.IntegerField(verbose_name='ID', auto_created=True, primary_key=True)
    total = models.IntegerField(blank=False)
    date_total = models.DateField(blank=False)


class Inventaire(models.Model):
    id_inventaire = models.IntegerField(verbose_name='ID', auto_created=True, primary_key=True)
    produit = models.ForeignKey(Produit, null=True, on_delete=models.CASCADE)
    nb_produit = models.FloatField(blank=False)
    total_prix = models.IntegerField(blank=False)
    date_inventaire = models.DateField(blank=False)


class StockRestant(models.Model):
    id_restant = models.IntegerField(verbose_name='ID', auto_created=True, primary_key=True)
    stock_restant = models.IntegerField(blank=False)
    date_restant = models.DateField(blank=False)
