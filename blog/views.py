from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from .models import Blog, BlogType
from read_statis.utils import read_statis_once_read

# 得到页码范围以及当页的博客对象
def getCommContext(request, blogs_all_list):
    # 生成分页器
    paginator = Paginator(blogs_all_list, settings.BLOGS_NUM_EACH_PAGE)
    page_num = request.GET.get('page', 1)      # 获取页面参数(Get请求)
    page_of_blogs = paginator.get_page(page_num)
    curPgNum = page_of_blogs.number            # 获取当前页码
    # 获取当前页前后两页范围并处理边界问题
    pgRange = list(range(max(curPgNum-2, 1),curPgNum)) + list(range(curPgNum, min(curPgNum+2, paginator.num_pages)+1))
    # 加上省略页标记
    if pgRange[0]-1>= 2:
        pgRange.insert(0, '...')
    if paginator.num_pages-pgRange[-1]>=2:
        pgRange.append('...')
    # 将首页和某页加入页码范围
    if pgRange[0]!=1:
        pgRange.insert(0, 1)
    if pgRange[-1]!=paginator.num_pages:
        pgRange.append(paginator.num_pages)

    # 获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year = blog_date.year, created_time__month = blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}    
    context['pgRange'] = pgRange
    context['page_of_blogs'] = page_of_blogs
    context['blogs'] = page_of_blogs.object_list
    context['blog_types'] = BlogType.objects.annotate(blog_count = Count('blog'))
    context['blog_dates'] = blog_dates_dict
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = getCommContext(request, blogs_all_list)
    return render(request,'blog/blog_list.html', context)

def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = getCommContext(request, blogs_all_list)
    context['blog_type'] = blog_type
    return render(request,'blog/blogs_with_type.html', context)

def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = getCommContext(request, blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' % (year, month)
    return render(request,'blog/blogs_with_date.html', context)

def blog_detail(request, blog_pk):
    curBlog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statis_once_read(request, curBlog)

    context = {}
    context['pre_blog'] = Blog.objects.filter(created_time__gt=curBlog.created_time).last()
    context['blog'] = curBlog
    context['next_blog'] = Blog.objects.filter(created_time__lt=curBlog.created_time).first()
    response = render(request, 'blog/blog_detail.html', context)
    response.set_cookie(read_cookie_key, 'true')         # 使用Cookie记录已读博客ID
    return response