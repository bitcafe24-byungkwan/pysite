import math

from django.core.paginator import Paginator
from django.db.models import Max, F
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from board.models import Board
from user.models import User


def get_session_user_id(request):
    try:
        res_id = request.session['authuser']['id']
    except Exception as e:
        res_id = None

    return res_id


def article_list(request, page_id=1):
    all_articles = Board.objects.all().order_by('-groupno', 'orderno')
    paginated_articles = Paginator(all_articles, 10)

    articles = paginated_articles.get_page(page_id)
    page_id = articles.number
    page_list = list(filter(lambda x: x > 0, range(page_id - 2, page_id + 3)))
    page_list = [x for x in page_list if int(x) <= paginated_articles.num_pages]
    print(page_list)
    data = {'article_list': articles, 'page_list': page_list}
    return render(request, 'board/list.html', data)


def view(request, article_id=1):
    article = Board.objects.get(id=article_id)
    data = {'article': article}
    return render(request, 'board/view.html', data)


def write_form(request):
    if not get_session_user_id(request):
        return HttpResponseRedirect('/board/1')
    return render(request, 'board/write.html')


def write(request):
    user_id = get_session_user_id(request)
    if not user_id:
        return HttpResponseRedirect('/board/1')

    article = Board()
    article.user = User.objects.get(id=user_id)
    article.title = request.POST['title']
    article.content = request.POST['content']

    if request.POST["write_type"] == "new":
        value = Board.objects.aggregate(max_groupno=Max('groupno'))
        if value["max_groupno"] is not None:
            article.groupno = value["max_groupno"] + 1
            print("new")
    else:
        obj = Board.objects.get(id=request.POST["write_type"])
        article.groupno = obj.groupno
        article.orderno = obj.orderno + 1
        article.depth = obj.depth + 1
        Board.objects.filter(groupno=obj.groupno). \
            filter(orderno__gt=obj.orderno). \
            update(orderno=F('orderno') + 1)

    article.save()
    obj = Board.objects.latest('id')

    return HttpResponseRedirect('/board/view/' + str(obj.id))


def delete(request, article_id=0):
    user_id = get_session_user_id(request)
    if not user_id:
        return HttpResponseRedirect('/board/1')
    if user_id == Board.objects.get(id=article_id).user.id:
        Board.objects.filter(id=article_id).update(valid=False)

    return HttpResponseRedirect('/board/1')


def modify_form(request, article_id=0):
    user_id = get_session_user_id(request)
    if not user_id:
        return HttpResponseRedirect('/board/1')

    if user_id != Board.objects.get(id=article_id).user.id:
        return HttpResponseRedirect('/board/1')

    old_article = Board.objects.get(id=article_id)
    data = {'base_article': old_article}
    return render(request, 'board/modify.html', data)


def modify(request, article_id):
    user_id = get_session_user_id(request)
    if not user_id:
        return HttpResponseRedirect('/board/1')
    if user_id != Board.objects.get(id=article_id).user.id:
        return HttpResponseRedirect('/board/1')

    update_article = {"title": request.POST["title"], "content": request.POST["content"]}
    Board.objects.filter(id=article_id).update(**update_article)
    return HttpResponseRedirect('/board/view/' + str(article_id))


def reply_form(request, article_id):
    user_id = get_session_user_id(request)
    if not user_id:
        return HttpResponseRedirect('/board/1')

    origin_article = Board.objects.get(id=article_id)
    data = {'origin_article': origin_article}

    return render(request, 'board/write.html', data)
