from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from main.models import Position

def edit(response):
    if response.method == "POST":
        selector = response.POST['search_by']
        if selector == '1':
            username = response.POST['usersearch']   
            positions = Position.objects.filter(user__username=username)
            return render(response, "editorial/edit.html", {'positions':positions})
        elif selector == '2':
            position_id = response.POST['positionsearch']
            positions = Position.objects.filter(position_id=position_id)
            return render(response, "editorial/edit.html", {'positions':positions})
        elif selector == '3':
            unique_id = response.POST['idsearch']
            positions = Position.objects.filter(id=unique_id)
            return render(response, "editorial/edit.html", {'positions':positions})
    return render(response, "editorial/edit.html", {'positions':[]})

def updatepos(response):
    if response.method == "POST":
        quantity = response.POST['posquantity']
        fill_price = response.POST['fillprice']
        unique_id = response.POST['uniqueid']
        position = Position.objects.get(id=unique_id)
        position.quantity = quantity
        position.fill_price = fill_price
        position.save()
        return redirect('/editorial/edit')
