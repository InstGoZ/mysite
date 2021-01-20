from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import Comment
from ..forms import CommentForm

register = template.Library()

# 原本以下操作都直接在Blog App的View中完成
# 通过自定义模板标签可以将评论相关的操作都定义到Commnet App中，这样更加松耦合

# 该模板标签得到评论(包含回复)数量
@register.simple_tag
def get_comment_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()

# 该模板标签初始化评论表单
@register.simple_tag
def get_comment_form(obj):
    content_type = ContentType.objects.get_for_model(obj)
    comment_form = CommentForm(initial={'content_type':content_type.model, 'object_id':obj.pk, 'reply_comment_id': 0})
    return comment_form

# 该模板标签得到评论(不包含回复)列表
@register.simple_tag
def get_comment_list(obj):
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=content_type, object_id=obj.pk, parent=None)
    return comments.order_by('-cmt_time')
