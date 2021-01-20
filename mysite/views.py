import datetime
from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from django.urls import reverse
from read_statis.utils import get_7days_read_data, get_today_hot_data
from blog.models import Blog

# 得到前七天的热门博客
def get_7days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects\
                .filter(read_details__date__lt=today, read_details__date__gte=date)\
                .annotate(read_num_sum=Sum('read_details__read_num'))\
                .order_by('-read_num_sum')
    return blogs[:7]

# 首页加载
def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_7days_read_data(blog_content_type)

    # 获取７天热门博客的缓存数据
    hot_blogs_7days = cache.get('hot_blogs_7days')
    # 如果没有缓存则新建
    if not hot_blogs_7days:
        hot_blogs_7days = get_7days_hot_blogs()
        cache.set('hot_blogs_7days', hot_blogs_7days, 3600)

    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_dat'] = get_today_hot_data(blog_content_type)
    context['hot_blogs_7days'] = hot_blogs_7days
    return render(request,'home.html', context)