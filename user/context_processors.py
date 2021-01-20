from .forms import LoginForm

# 建立此文件后再将路径加入settings->TEMPLATES->context_processors,就可以成为模板公用变量
def login_modal_form(request):
    return {'login_modal_form': LoginForm()}
