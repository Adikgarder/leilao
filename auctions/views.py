from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest
from .forms import EmailForm
from django.shortcuts import render
from .models import auctionlist
from .models import bids




def listingpage(request):
    allbids = bids.objects.all()

    return render(request, "auctions/listingpage.html", {
        "allbids": allbids,
    })

def index(request):    
    return render(request, "auctions/index.html",{
        "a1": auctionlist.objects.filter(active_bool = True),
            })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "As senhas devem ser iguais"
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Nome de usuário já utilizado."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url='login')
def create(request):
    if request.method == "POST":
        m = auctionlist()
        m.user = request.user.username
        m.title = request.POST["create_title"]
        m.desc = request.POST["create_desc"]
        m.starting_bid = request.POST["create_initial_bid"]
        m.image_url = request.POST["img_url"]
        m.category = request.POST["category"]
        # m = auctionlist(title = title, desc=desc, starting_bid = starting_bid, image_url = image_url, category = category)
        m.save()
        return redirect("index")
    return render(request, "auctions/create.html")


@login_required(login_url='login')
def dashboard(request):

    winnners = winner.objects.all().order_by('?')

    context = {
        'winnners': winnners,

    }

    return render(request, "auctions/dashboard.html", context=context)

def send_email(request):
    if request.method == 'POST':
        # Get the email form data from the POST request
        email = request.POST.get('Email')
        subject = request.POST.get('Subject')
        message = request.POST.get('Comment')

        # Send the email using Django's built-in send_mail function
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email='from@example.com',
                recipient_list=[email],
                fail_silently=False,
            )
            return HttpResponse('Email enviado com sucesso!')
        except Exception as e:
            return HttpResponseBadRequest(f'Error sending email {e}')
    else:
        return HttpResponseBadRequest('Invalid request method')


def listingpage(request, bidid):
    biddesc = auctionlist.objects.get(pk = bidid, active_bool = True)
    bids_present = bids.objects.filter(listingid = bidid)

    return render(request, "auctions/listingpage.html",{
        "list": biddesc,
        "comments" : comments.objects.filter(listingid = bidid),
        "present_bid": minbid(biddesc.starting_bid, bids_present),
        "allbids":bids.objects.filter(listingid = bidid),
    })


@login_required(login_url='login')
def watchlistpage(request, username):

    # present_w = watchlist.objects.get(user = "username")
    list_ = watchlist.objects.filter(user = username)
    return render(request, "auctions/watchlist.html",{
        "user_watchlist" : list_,
    })


@login_required(login_url='login')
def addwatchlist(request):
    nid = request.GET["listid"]
    
    # below line of code will select a table of watchlist that has my name, then
    # when we loop in this watchlist, there r two fields present, to browse watch_list 
    # watch_list.id == auctionlist.id, similar for all

    list_ = watchlist.objects.filter(user = request.user.username)

    # when you below line, you shld convert id to int inorder to compare or else == wont work

    for items in list_:
        if int(items.watch_list.id) == int(nid):
            return watchlistpage(request, request.user.username)

    newwatchlist = watchlist(watch_list = auctionlist.objects.get(pk = nid), user = request.user.username)
    newwatchlist.save()
        # this message remains untill u reload
    messages.success(request, "Item added to watchlist")

    return listingpage(request, nid)


@login_required(login_url='login')
def deletewatchlist(request):
    rm_id = request.GET["listid"]
    list_ = watchlist.objects.get(pk = rm_id)

    # this message remains untill u reload
    messages.success(request, f"{list_.watch_list.title} foi excluído da sua lista de observação.")
    list_.delete()

    # you cannot call a fuction  from views as a return value
    return redirect("index")


# this function returns minimum bid required to place a user's bid
def minbid(min_bid, present_bid):
    for bids_list in present_bid:
        if min_bid < int(bids_list.bid):
            min_bid = int(bids_list.bid)
    return min_bid


@login_required(login_url='login')
def bid(request):
    bid_amnt = request.GET["bid_amnt"]
    list_id = request.GET["list_d"]
    bids_present = bids.objects.filter(listingid = list_id)
    startingbid = auctionlist.objects.get(pk = list_id)
    min_req_bid = startingbid.starting_bid
    min_req_bid = minbid(min_req_bid, bids_present)

    if int(bid_amnt) > int(min_req_bid):
        mybid = bids(user = request.user.username, listingid = list_id , bid = bid_amnt)
        mybid.save()
        messages.success(request, "Lance Colocado")
        return redirect("index")

    messages.warning(request, f"O lance de {bid_amnt}MT é menor do que o lance mínimo de {min_req_bid}MT para este item. Por favor, faça um lance mais alto.")
    return listingpage(request, list_id)

   
# shows comments made by different user and allows to add comments
@login_required(login_url='login')
def allcomments(request):
    comment = request.GET["comment"]
    username = request.user.username
    list_id = request.GET["listid"]
    new_comment = comments(user = username, comment = comment, listingid = list_id)
    new_comment.save()
    return listingpage(request, list_id)


# shows message abt winner when bid is closed
def win_ner(request):
    bid_id = request.GET["listid"]
    bids_present = bids.objects.filter(listingid = bid_id)
    biddesc = auctionlist.objects.get(pk = bid_id, active_bool = True)
    max_bid = minbid(biddesc.starting_bid, bids_present)
    try:
        # checks if anyone other than list_owner win the bid
        winner_object = bids.objects.get(bid = max_bid, listingid = bid_id)
        winner_obj = auctionlist.objects.get(id = bid_id)
        win = winner(bid_win_list = winner_obj, user = winner_object.user)
        winners_name = winner_object.user
    
    except:
        #if no-one placed a bid, and if bid is closed by list_owner, owner wins the bid
        winner_obj = auctionlist.objects.get(starting_bid = max_bid, id = bid_id)
        win = winner(bid_win_list = winner_obj, user = winner_obj.user)
        winners_name = winner_obj.user

    #Check Django Documentary for Updating attributes based on existing fields.
    biddesc.active_bool = False
    biddesc.save()

    # saving winner details
    win.save()
    messages.success(request, f"{winners_name} won {win.bid_win_list.title}.")
    return redirect("index")

# checks winner
def winnings(request):
    try:
        your_win = winner.objects.filter(user = request.user.username)
    except:
        your_win = None

    return render(request, "auctions/winnings.html",{
        "user_winlist" : your_win,
    })

#shows lists that are present in a specific category
def cat(request, category_name):
    category = auctionlist.objects.filter(category = category_name)
    return render(request, "auctions/index.html",{
        "a1" : category,
    })

#shows all categories in which object is listed
def cat_list(request):

    # unlike filter that takes a values of object_name in model, to 
    # display objectname use .values('name of section from your object')
    # and when you add distinct() along with it
    # it shows only unique names, omits duplicates

    category_present = auctionlist.objects.values('category').distinct()
    return render(request, "auctions/category.html",{
        "cat_list" : category_present,
    })
    
    
def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')



def search_view(request):
    query = request.GET.get('q')  # Obtém o valor do campo de pesquisa do formulário

    results = auctionlist.objects.filter(title__icontains=query)  # Substitua 'YourModel' pelo seu modelo real

    context = {
        'results': results,
        'query': query,
    }

    return render(request, 'seu_template_de_resultados.html', context)