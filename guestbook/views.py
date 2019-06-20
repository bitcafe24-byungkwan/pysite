from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from guestbook.models import GuestBook


def list(request):
    if request.method == 'GET':
        guestbook = GuestBook.objects.all().order_by('-id')
        data = {'article_list': guestbook}
        return render(request, 'guestbook/list.html', data)
    else:
        return HttpResponse('Foo')


def add(request):
    article = GuestBook()

    article.name = request.POST['name']
    article.password = request.POST['pass']
    article.contents = request.POST['content']
    article.save()

    return HttpResponseRedirect('/guestbook')


def delete_form(request, article_id=0):
    return render(request, 'guestbook/deleteform.html', {'no': article_id})


def delete(request):
    if request.method == 'POST':
        no = request.POST['no']
        password = request.POST['password']

        article = GuestBook.objects.filter(id=no).filter(password=password)
        article.delete()

    return HttpResponseRedirect('/guestbook')
