from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from datetime import date
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

from epicerie.models import Categorie, Vendre, Produit, StockProduit, TotalStock, Inventaire, StockRestant


def accueil(request):
    if request.user.is_authenticated:
        active = 'active'
        date_now = date.today()
        # calcul du restant dans le stock
        stock_pro = StockProduit.objects.all()
        stock_pro = stock_pro.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
        total_stock(stock_pro, date_now)
        data = Vendre.objects.order_by('-date_vendre').all()
        # Calcul du Total de tout les ventes
        vendre_all = Vendre.objects.all()
        vendre_all = vendre_all.aggregate(Sum('prix_total_vendre'))['prix_total_vendre__sum'] or 0
        # Calcul de vente d'aujourd'hui
        vendre_now = Vendre.objects.filter(date_vendre=date_now).all()
        vendre_now = vendre_now.aggregate(Sum('prix_total_vendre'))['prix_total_vendre__sum'] or 0
        totalstock = TotalStock.objects.get(date_total=date_now).total
        total_st = stock_pro + vendre_now
        total_st1 = 0
        total_st2 = 0
        if total_st > totalstock:
            total_st2 = total_st - totalstock
        elif total_st < totalstock:
            total_st1 = totalstock - total_st
        donne = {'vendu': data, 'stock': stock_pro, 'vendre_all': vendre_all, 'vendre_now': vendre_now,
                 'total': totalstock, 'total_st1': total_st1, 'total_st': total_st2, 'active_accueil': active}
        return render(request, 'accueil.html', donne)
    else:
        messages.warning(request, f'Vous devriez vous connecté d\'abord !')
        return redirect('connexion')


def total(request):
    if request.user.is_authenticated:
        active = 'active'
        vente = Vendre.objects.order_by('-id_vendre').all()
        paginator = Paginator(vente, 10)
        page = request.GET.get('page')
        data = paginator.get_page(page)
        donne = {'active_accueil': active, 'data': data}
        return render(request, "total.html", donne)
    else:
        messages.warning(request, f'Vous devriez vous connecté d\'abord !')
        return redirect('connexion')


class PrixTotal(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            active = 'active'
            datedeb = request.GET.get('datedeb')
            datefin = request.GET.get('datefin')
            if datedeb > datefin:
                messages.warning(request, f'La Date Début ne doit pas être superieure à la Date Fin !')
                return render(request, 'total.html')
            else:
                prix_total = Vendre.objects.filter(date_vendre__range=[datedeb, datefin])
                prix = prix_total.aggregate(Sum('prix_total_vendre'))['prix_total_vendre__sum'] or 0
                vendu = Vendre.objects.filter(date_vendre__range=[datedeb, datefin])
                donne = {'active_accueil': active, 'prix_total': prix, 'data': vendu}
                return render(request, 'total.html', donne)
        else:
            messages.warning(request, f'Vous devriez vous connecté d\'abord !')
            return redirect('connexion')


class Connexion(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            return redirect('accueil')
        return render(request, 'connexion.html')

    @staticmethod
    def post(request):
        nom = request.POST['UsernameCompte']
        mot = request.POST['MotPasseCompte']
        try:
            user = User.objects.get(username=nom)
            check_pass = check_password(mot, user.password)
            if check_pass:
                user = authenticate(request, username=nom, password=mot)
                login(request, user)
                return redirect('accueil')
            else:
                messages.error(request, 'Mot de passe incorrect')
        except User.DoesNotExist:
            messages.error(request, f'Votre nom d\'utilisateur n\'existe pas !')
        return render(request, 'connexion.html')


def deconnexion(request):
    logout(request)
    return redirect('connexion')


def supp_total(request):
    if request.user.is_authenticated:
        list_supp = request.GET.getlist('total_select')
        if list_supp:
            for i_d in list_supp:
                total_list = get_object_or_404(TotalStock, id_total=i_d)
                total_list.delete()
            messages.success(request, f'Total supprimer avec succès !')
        else:
            messages.warning(request, f'Veuillez coché les elements que vous voulez supprimer !')
        return redirect('list_total')
    else:
        messages.warning(request, f'Vous devriez vous connecté d\'abord !')
        return redirect('connexion')


def supp_vente(request):
    if request.user.is_authenticated:
        list_supp = request.GET.getlist('id_vendre')
        if list_supp:
            for i_d in list_supp:
                vente = get_object_or_404(Vendre, id_vendre=i_d)
                vente.delete()
            messages.success(request, f'Produit vendu supprimer avec succès !')
        else:
            messages.warning(request, f'Veuillez coché les elements que vous voulez supprimer !')
        return redirect('accueil')
    else:
        messages.warning(request, f'Vous devriez vous connecté d\'abord !')
        return redirect('connexion')


def supp_tout_vente(request):
    if request.user.is_authenticated:
        Vendre.objects.all().delete()
        messages.success(request, f'Tout Supprimer avec succès !')
        return redirect('accueil')
    else:
        messages.warning(request, f'Vous devriez vous connecté d\'abord !')
        return redirect('connexion')


class Produitvendu(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            list_produit = StockProduit.objects.order_by('produit__nom_produit').all()
            return render(request, 'produit_vendu.html', {'list': list_produit})
        else:
            messages.warning(request, f'Vous devriez vous connecté d\'abord !')
            return redirect('connexion')

    @staticmethod
    def post(request):
        produit_id = request.POST['produit_id']
        if produit_id == 'vide':
            prix_produit = request.POST['prix_produit']
            if prix_produit:
                prix_produit = int(prix_produit)
                date_new = request.POST['date_new']
                Vendre.objects.create(
                    prix_total_vendre=prix_produit,
                    date_vendre=date_new,
                )
                messages.success(request, f'Enregistrer avec succès !')
                return redirect('accueil')
            else:
                messages.warning(request, f'Vous ne pouvez pas entré un quantité pour le produit \"Vide\" ')
                return redirect('enregistrement')
        else:
            stock_new = get_object_or_404(StockProduit, produit_id=produit_id)
            pro = get_object_or_404(Produit, id_produit=produit_id)
            pro_categorie = pro.categorie_id
            quantite_stock = stock_new.quantite_stock
            cate = stock_new.produit.categorie.nom_categorie
            quantite_produit = request.POST['quantite_produit']
            prix_produit = request.POST['prix_produit']

            if quantite_produit and prix_produit:
                messages.warning(request, f"Vous ne pouvez remplir qu'un seul champs !")
                return redirect('enregistrement')

            if cate == 'Nombre':
                if quantite_produit:
                    date_new = request.POST['date_new']
                    if quantite_produit.isdigit():
                        quantite_produit = int(quantite_produit)
                        if quantite_produit <= quantite_stock:
                            prix_vendu = pro.prix_produit * quantite_produit
                            stock_new.quantite_stock -= quantite_produit
                            stock_new.prix_total -= prix_vendu
                            stock_new.save()
                            Vendre.objects.create(
                                produit_id=produit_id,
                                quantite_vendre=quantite_produit,
                                prix_total_vendre=prix_vendu,
                                date_vendre=date_new,
                            )
                            messages.success(request, f'\"{quantite_produit}\" \"{stock_new.produit.nom_produit}\"'
                                                      f' vendu avec succès !')
                            return redirect('accueil')

                        elif quantite_stock == 0:
                            messages.error(request, f"Le stock du produit \"{pro.nom_produit}\" est épuisé !")
                        else:
                            messages.warning(request, f'Il ne rest plus que \"{stock_new.quantite_stock}'
                                                      f'{stock_new.produit.categorie.nom_categorie}\"'
                                                      f' de \"{pro.nom_produit}\" dans votre stock!')
                    else:
                        messages.warning(request, f'Entrer un nombre qui ne contient pas de virgule pour '
                                                  f'le produit \"{stock_new.produit.nom_produit}\"')
                    return redirect('enregistrement')

                elif prix_produit:
                    messages.warning(request, f'Nombre dans le champ Quantité pour le produit '
                                              f'\"{stock_new.produit.nom_produit}\"')
                    return redirect('enregistrement')
            else:
                if quantite_produit:
                    date_new = request.POST['date_new']
                    quantite_produit = float(quantite_produit)
                    if quantite_produit <= quantite_stock:
                        prix_vendu = pro.prix_produit * quantite_produit
                        stock_new.quantite_stock = round(stock_new.quantite_stock - quantite_produit, 2)
                        stock_new.prix_total -= prix_vendu
                        stock_new.save()
                        Vendre.objects.create(
                            produit_id=produit_id,
                            quantite_vendre=quantite_produit,
                            prix_total_vendre=prix_vendu,
                            date_vendre=date_new,
                        )
                        messages.success(request, f'\"{quantite_produit}\" \"{stock_new.produit.nom_produit}\"'
                                                  f' vendu avec succès !')
                        return redirect('accueil')

                    elif quantite_stock == 0:
                        messages.error(request, f"Le stock du produit \"{pro.nom_produit}\" est épuisé !")
                    else:
                        messages.warning(request, f'Il ne rest plus que \"{stock_new.quantite_stock}'
                                                  f'{stock_new.produit.categorie.nom_categorie}\"'
                                                  f' de \"{pro.nom_produit}\" dans votre stock!')
                    return redirect('enregistrement')

                if prix_produit:
                    prix_produit = int(prix_produit)
                    date_new = request.POST['date_new']
                    prix_stock = stock_new.prix_total
                    if prix_produit <= prix_stock:
                        if pro_categorie == 2 or pro_categorie == 4 or pro_categorie == 3:
                            quantite_vendu = (stock_new.quantite_stock * prix_produit) / prix_stock
                            quantite_vendu = round(quantite_vendu, 2)
                            quantite_stock = stock_new.quantite_stock - quantite_vendu
                            stock_new.quantite_stock = round(quantite_stock, 2)
                            stock_new.prix_total -= prix_produit
                            stock_new.save()
                            Vendre.objects.create(
                                produit_id=produit_id,
                                quantite_vendre=quantite_vendu,
                                prix_total_vendre=prix_produit,
                                date_vendre=date_new,
                            )
                            messages.success(request, f'\"{stock_new.produit.nom_produit}\" enregistrer avec succès !')
                            return redirect('accueil')
                        else:
                            messages.warning(request, f'Nombre dans le champ Quantité pour le produit '
                                                      f'\"{stock_new.produit.nom_produit}\"')
                            return redirect('enregistrement')
                    else:
                        messages.warning(request, f'Il ne rest plus que \"{stock_new.quantite_stock}'
                                                  f'{stock_new.produit.categorie.nom_categorie}\"'
                                                  f'({stock_new.prix_total}Ar) de \"{pro.nom_produit}\"'
                                                  f' dans votre stock!')
                        return redirect('enregistrement')


class SaveProduit(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            categ = Categorie.objects.all()
            return render(request, 'produit.html', {'list': categ})
        else:
            messages.warning(request, f'Vous devriez vous connecté d\'abord !')
            return redirect('connexion')

    @staticmethod
    def post(request):
        nom_produit = request.POST['nom_produit']
        prix_produit = request.POST['prix_produit']
        catego = request.POST['categorie']

        produit_exist = Produit.objects.filter(nom_produit=nom_produit).exists()
        if produit_exist:
            messages.warning(request, f'Le produit \"{nom_produit}\" exist déjà !')
            return redirect('enregistre_produit')
        else:
            Produit.objects.create(
                nom_produit=nom_produit,
                prix_produit=prix_produit,
                categorie_id=catego,
            )
            messages.success(request, f'Le produit \"{nom_produit}\" est enregistré avec succès !')
            return redirect('produit_list')


class ModProduit(View):
    @staticmethod
    def get(request, id_pro):
        if request.user.is_authenticated:
            prod = get_object_or_404(Produit, id_produit=id_pro)
            cat = Categorie.objects.all()
            donne = {'produit': prod, 'list': cat}
            return render(request, 'mod_produit.html', donne)
        else:
            messages.warning(request, f'Vous devriez vous connecté d\'abord !')
            return redirect('connexion')

    @staticmethod
    def post(request, id_pro):
        prod = get_object_or_404(Produit, id_produit=id_pro)
        prod_stock = StockProduit.objects.filter(produit_id=id_pro).first()
        if prod_stock:
            prix_new = int(request.POST['prix_produit'])
            prod.nom_produit = request.POST['nom_produit']
            prod.prix_produit = prix_new
            prod.categorie_id = request.POST['categorie']
            prod.save()
            prod_stock.prix_total = prod_stock.quantite_stock * prix_new
            prod_stock.save()
        else:
            prod.nom_produit = request.POST['nom_produit']
            prod.prix_produit = request.POST['prix_produit']
            prod.categorie_id = request.POST['categorie']
            prod.save()

        messages.success(request, f'Le produit \"{prod.nom_produit}\" est modifié avec succès !')
        return redirect('produit_list')


def supp_produit(request, id_pro):
    if request.user.is_authenticated:
        prod = get_object_or_404(Produit, id_produit=id_pro)
        if prod:
            prod.delete()
            messages.success(request, f'Le produit \"{prod.nom_produit}\" est supprimer avec succès !')
        else:
            messages.error(request, f'Une erreur est survenue lors de la suppression !')
        return redirect('produit_list')
    else:
        messages.warning(request, f'Vous devriez vous connecté d\'abord !')
        return redirect('connexion')


def produit_list(request):
    if request.user.is_authenticated:
        active = 'active'
        list_produit = Produit.objects.all()
        donne = {'list': list_produit, 'active_produit': active}
        return render(request, 'list_produit.html', donne)
    else:
        messages.warning(request, f'Vous devriez vous connecté d\'abord !')
        return redirect('connexion')


class SaveStock(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            list_produit = Produit.objects.order_by('nom_produit').all()
            return render(request, 'enregistrer_stock.html', {'list': list_produit})
        else:
            messages.warning(request, f'Vous devriez vous connecté d\'abord !')
            return redirect('connexion')

    @staticmethod
    def post(request):
        quantite = float(request.POST['quantite_stock'])
        produit_id = request.POST['nom_produit']
        prix = get_object_or_404(Produit, id_produit=produit_id)
        prix_total = quantite * prix.prix_produit
        date_now = date.today()

        stock_exist = StockProduit.objects.filter(produit_id=produit_id).first()
        if stock_exist:
            stock_exist.quantite_stock += quantite
            stock_exist.prix_total += prix_total
            stock_exist.date_stock = date_now
            stock_exist.save()
            total_exist(prix_total, date_now)
            messages.success(request, f'\"{quantite} {prix.categorie.nom_categorie}\" du produit'
                                      f' \"{stock_exist.produit.nom_produit}\"'
                                      f' est ajouté avec succès !')
        else:
            StockProduit.objects.create(
                produit_id=produit_id,
                quantite_stock=quantite,
                prix_total=prix_total,
                date_stock=date_now,
            )
            total_exist(prix_total, date_now)
            messages.success(request, f'Le produit \"{prix.nom_produit}\" '
                                      f'est enregistré avec succès dans le stock !')
        return redirect('stock_produit')


class Stock(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            active = 'active'
            stock_pro = StockProduit.objects.order_by('-date_stock').all()
            stock_all = stock_pro.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            donne = {'list': stock_pro, 'active_stock': active, 'prix_all': stock_all}
            return render(request, 'stock_produit.html', donne)
        else:
            messages.warning(request, f'Vous devriez vous connecté d\'abord !')
            return redirect('connexion')


def supp_stock(request):
    if request.user.is_authenticated:
        list_stock = request.GET.getlist('id_stock')
        if list_stock:
            for id_stock in list_stock:
                stock_pro = get_object_or_404(StockProduit, id_stock=id_stock)
                stock_pro.delete()
                messages.success(request, f'Le produit \"{stock_pro.produit.nom_produit}\" est supprimé avec succès !')
        else:
            messages.warning(request, f'Veuillez coché les elements que vous voulez supprimer !')
        return redirect('stock_produit')
    else:
        messages.warning(request, f'Vous devriez vous connecté d\'abord !')
        return redirect('connexion')


class ModStock(View):
    @staticmethod
    def get(request, id_stock):
        if request.user.is_authenticated:
            stock = get_object_or_404(StockProduit, id_stock=id_stock)
            return render(request, 'mod_stock.html', {'stock': stock})
        else:
            messages.warning(request, f'Vous devriez vous connecté d\'abord !')
            return redirect('connexion')

    @staticmethod
    def post(request, id_stock):
        stock = get_object_or_404(StockProduit, id_stock=id_stock)
        mod_quantite = float(request.POST['quantite_produit'])
        date_now = date.today()
        if mod_quantite < stock.quantite_stock:
            prix_total = stock.prix_total - (mod_quantite * stock.produit.prix_produit)
            total_mod(prix_total, date_now)
        else:
            prix_total = (mod_quantite * stock.produit.prix_produit) - stock.prix_total
            total_exist(prix_total, date_now)
        stock.quantite_stock = mod_quantite
        stock.prix_total = mod_quantite * stock.produit.prix_produit
        stock.date_stock = date_now
        stock.save()
        messages.success(request, f'La quantité du produit \"{stock.produit.nom_produit}\" '
                                  f'dans le stock est modifié avec succès !')
        return redirect('stock_produit')


def total_stock(stock_total, date_now):
    date_exist = TotalStock.objects.filter(date_total=date_now).exists()
    if not date_exist:
        TotalStock.objects.create(
            total=stock_total,
            date_total=date_now,
        )


def total_exist(total_st, date_now):
    date_exist = TotalStock.objects.filter(date_total=date_now).exists()
    if date_exist:
        totalexist = get_object_or_404(TotalStock, date_total=date_now)
        totalexist.total += total_st
        totalexist.save()


def total_mod(total_st, date_now):
    date_exist = TotalStock.objects.filter(date_total=date_now).exists()
    if date_exist:
        totalexist = get_object_or_404(TotalStock, date_total=date_now)
        totalexist.total -= total_st
        totalexist.save()


def list_total(request):
    active = 'active'
    total_list = TotalStock.objects.all()
    return render(request, 'total_list.html', {'total': total_list, 'active_list': active})


def inventaire(request):
    if request.user.is_authenticated:
        active = 'active'
        stock_all = TotalStock.objects.last()
        stock_restant(stock_all.total, stock_all.date_total)
        stock_rest = StockRestant.objects.first()
        stock_reste = stock_rest.stock_restant
        inventair = Inventaire.objects.all()
        stock_pro = StockProduit.objects.all()
        stock_pro = stock_pro.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
        total_inve = inventair.aggregate(Sum('total_prix'))['total_prix__sum'] or 0
        manque = 0
        trop = 0
        egal = False
        if stock_pro > total_inve:
            manque = stock_pro - total_inve
        elif stock_pro < total_inve:
            trop = total_inve - stock_pro
        else:
            egal = True
        donne = {'active_rendu': active, 'total_restant': stock_reste, 'date_restant': stock_rest.date_restant,
                 'total_inve': total_inve, 'manque': manque, 'trop': trop, 'egal': egal,
                 'inventaire': inventair, 'stock': stock_pro}
        return render(request, 'Inventaire.html', donne)
    else:
        messages.warning(request, f'Vous devriez vous connecté d\'abord !')
        return redirect('connexion')


class save_inventaire(View):
    @staticmethod
    def get(request):
        produit = Produit.objects.all()
        donne = {'produit': produit}
        return render(request, 'save_inventaire.html', donne)

    @staticmethod
    def post(request):
        produit_id = request.POST['nom_produit']
        quantite_stock = float(request.POST['quantite_stock'])
        produit_prix = Produit.objects.filter(id_produit=produit_id).first().prix_produit
        quantite = StockProduit.objects.filter(produit_id=produit_id).first().quantite_stock
        inv_exist = Inventaire.objects.filter(produit_id=produit_id).exists()
        if inv_exist:
            get_inve = get_object_or_404(Inventaire, produit_id=produit_id)
            get_inve.nb_produit += quantite_stock
            get_inve.total_prix = get_inve.nb_produit * produit_prix
            get_inve.save()
        else:
            total_prix = quantite_stock * produit_prix
            date_inventaire = date.today()
            Inventaire.objects.create(
                produit_id=produit_id,
                nb_produit=quantite_stock,
                total_prix=total_prix,
                date_inventaire=date_inventaire
            )
        messages.success(request, f"Produit enrgistrer dans l'inventaire avec succès !")
        return redirect('inventaire')


def stock_restant(stock_Restant, date_restant):
    StockRestant.objects.create(
        stock_restant=stock_Restant,
        date_restant=date_restant,
    )


def supp_tout(request):
    if request.user.is_authenticated:
        Inventaire.objects.all().delete()
        StockRestant.objects.all().delete()
        messages.success(request, f'Tout Supprimer avec succès !')
        return redirect('inventaire')
    else:
        messages.warning(request, f'Vous devriez vous connecté d\'abord !')
        return redirect('connexion')
