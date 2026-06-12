from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

@staff_member_required  # só admin acessa
def admin_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})



def registro_view(request):
    mensagem = ''

    if request.method == 'POST':
        nome     = request.POST.get('nome')
        email    = request.POST.get('email')
        senha    = request.POST.get('senha')

        if User.objects.filter(email=email).exists():
            mensagem = 'E-mail já cadastrado.'
        else:
            User.objects.create_user(username=email, email=email, 
                                     password=senha, first_name=nome)
            return redirect('login')

    return render(request, 'registro.html', {'mensagem': mensagem})



def login_view(request):
    mensagem = ''

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # busca usuário pelo email
        from django.contrib.auth.models import User
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            username = None

        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            return redirect('home')  # redireciona após login
        else:
            mensagem = 'E-mail ou senha incorretos.'

    return render(request, 'login.html', {'mensagem': mensagem})

def perfil_view(request):
    return render(request, 'perfil.html')

def produto_view(request):
    return render(request, 'produto.html')