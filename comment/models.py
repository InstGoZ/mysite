import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

# 多线程方式解决发送邮件的延时问题
class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, '', settings.EMAIL_HOST_USER, [self.email], self.fail_silently, html_message=self.text)


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    cmt_text = models.TextField()
    cmt_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    # 可实现对评论的评论，即对评论进行回复
    root = models.ForeignKey('self', related_name="root_comment", null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name="parent_comment", null=True, on_delete=models.CASCADE)
    reply_to = models.ForeignKey(User, related_name="replies", null=True, on_delete=models.CASCADE)

    def send_mail(self):
        # 发送邮件通知
        if self.parent is None:
            # 评论
            subject = '有人评论你的博客'            
            email = self.content_object.get_email()
        else:
            # 回复
            subject = '有人回复你的评论'
            email = self.reply_to.email             
        if email != '':
            context = {}
            context['comment_text'] = self.cmt_text
            context['url'] = self.content_object.get_url()
            text = render_to_string('comment/send_mail.html', context)
            send_mail = SendMail(subject, text, email)
            send_mail.start()


    def __str__(self):
        return self.cmt_text

    class Meta:
        ordering = ['cmt_time']