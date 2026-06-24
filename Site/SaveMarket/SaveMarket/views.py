from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import authenticate, login

# Importação unificada das Models da equipe
from SaveMarket.Produtos.models import Produto, MercadoParceiro

def home(request):
    produtos = Produto.objects.filter(validade__gte=timezone.now().date())
    mercados = MercadoParceiro.objects.all()

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

    # TAREFA LARANJA: Gerencia os tipos de ordenação selecionados pelo Dropdown
    sort = request.GET.get('sort', 'validade')

    if sort == 'preco':
        produtos = produtos.order_by('preco_desconto')
    elif sort == 'recentes':
        produtos = produtos.order_by('-data_criacao')
    elif sort == 'desconto':
        produtos = sorted(produtos, key=lambda p: p.percentual_desconto, reverse=True)
    else:
        produtos = produtos.order_by('validade')

    return render(request, 'home.html', {
        'produtos': produtos,
        'mercados': mercados,
        'categoria': categoria,
    })

# TAREFA VERMELHA: Sistema de recebimento de Avaliações
def produto_view(request, pk=None):
    if pk:
        produto = get_object_or_404(Produto, pk=pk)
        
        # Se o usuário enviar uma nota via POST
        if request.method == 'POST':
            nota = request.POST.get('nota')
            comentario = request.POST.get('comentario', '')
            if nota:
                from SaveMarket.Produtos.models import Avaliacao
                Avaliacao.objects.create(produto=produto, nota=int(nota), comentario=comentario)
                return redirect(request.path)

        return render(request, 'detalhes-produto.html', {'produto': produto})
    
    return render(request, 'detalhes-produto.html')

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
            User.objects.create_user(username=email, email=email, password=senha, first_name=nome)
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
            return redirect('home')
        else:
            mensagem = 'E-mail ou senha incorretos.'
    return render(request, 'login.html', {'mensagem': mensagem})

@login_required
def perfil_view(request):
    return render(request, 'perfil.html')