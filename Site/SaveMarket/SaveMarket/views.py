from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from SaveMarket.Produtos.models import Produto, MercadoParceiro
from django.db.models import Q

def home(request):
    produtos = Produto.objects.filter(validade__gte=timezone.now().date())
    mercados = MercadoParceiro.objects.all()

    # Busca
    # Busca
    q = request.GET.get('q', '')

    if q:
        produtos = produtos.filter(
         Q(titulo__icontains=q) |
         Q(mercado__nome__icontains=q)
    )

    # Filtro por categoria
    categoria = request.GET.get('categoria', '')

    if categoria:
        produtos = produtos.filter(categoria__iexact=categoria)

    # Filtro por faixa de desconto
    desconto = request.GET.get('desconto', '')

    if desconto:
        desconto_minimo = float(desconto)
        produtos = [
            produto for produto in produtos
            if produto.percentual_desconto >= desconto_minimo
        ]

    # Ordenação
    sort = request.GET.get('sort', 'validade')

    if sort == 'desconto':
        produtos = sorted(produtos, key=lambda p: p.percentual_desconto, reverse=True)
    elif sort == 'preco':
        produtos = sorted(produtos, key=lambda p: p.preco_desconto)
    else:
        produtos = sorted(produtos, key=lambda p: p.validade)

    return render(request, 'home.html', {
    'produtos': produtos,
    'mercados': mercados,
    'categoria': categoria,
    'desconto': desconto,
    })
    


def produto_view(request, pk=None):
    if pk:
        produto = get_object_or_404(Produto, pk=pk)
        return render(request, 'produto.html', {'produto': produto})
    return render(request, 'produto.html')


def mercado_view(request, pk):
    mercado = get_object_or_404(MercadoParceiro, pk=pk)
    produtos = mercado.produtos.all().order_by('validade')
    return render(request, 'mercado.html', {'mercado': mercado, 'produtos': produtos})


@staff_member_required
def admin_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})


def registro_view(request):
    mensagem = ''
    if request.method == 'POST':
        nome  = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
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
        email    = request.POST.get('email')
        password = request.POST.get('password')
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            username = None
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('ofertas')
        else:
            mensagem = 'E-mail ou senha incorretos.'
    return render(request, 'login.html', {'mensagem': mensagem})


@login_required
def perfil_view(request):
    return render(request, 'perfil.html')


@login_required
def dashboard_mercado(request):
    produtos = Produto.objects.all().order_by('validade')

    produtos_risco = produtos.filter(
        validade__lte=timezone.now().date() + timedelta(days=3)
    )

    total_produtos = produtos.count()
    total_risco = produtos_risco.count()

    return render(request, 'dashboard_mercado.html', {
        'produtos': produtos,
        'produtos_risco': produtos_risco,
        'total_produtos': total_produtos,
        'total_risco': total_risco,
    })