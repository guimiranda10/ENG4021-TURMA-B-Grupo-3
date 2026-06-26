from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from SaveMarket.Produtos.models import Produto, MercadoParceiro, Favorito
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout


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
    # TAREFA 1: Ordenação e Menor Preço (Unindo a lógica do grupo com a nossa do HTML)
    ordenar = request.GET.get('ordenar', '') # Nosso botão do HTML
    sort = request.GET.get('sort', 'validade') # Botão original do grupo

    if sort == 'preco':
        produtos = produtos.order_by('preco_desconto')
    elif sort == 'recentes':
        produtos = produtos.order_by('-data_criacao')
    elif sort == 'desconto':
        produtos = sorted(produtos, key=lambda p: p.percentual_desconto, reverse=True)
    else:
        produtos = sorted(produtos, key=lambda p: p.validade)

    return render(request, 'home.html', {
        'produtos': produtos,
        'mercados': mercados,
        'categoria': categoria,
        'desconto': desconto,
        'ofertas': produtos,
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
    produtos = mercado.produtos.filter(validade__gte=timezone.now().date()).order_by('validade')
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

#####INICIO PERFIL#####
@login_required
def perfil_view(request):
    return render(request, 'perfil.html')

@login_required
def meus_dados_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
 
        perfil = user.perfil
        perfil.telefone = request.POST.get('telefone', '')
 
        # Processa upload da foto (se enviada)
        if request.FILES.get('foto'):
            perfil.foto = request.FILES['foto']
 
        perfil.save()
 
        messages.success(request, 'Dados atualizados com sucesso!')
        return redirect('meus_dados')
 
    return render(request, 'meus_dados.html')
 
 
@login_required
def enderecos_view(request):
    if request.method == 'POST':
        Endereco.objects.create(
            user=request.user,
            rua=request.POST.get('rua'),
            numero=request.POST.get('numero'),
            bairro=request.POST.get('bairro'),
            cidade=request.POST.get('cidade'),
            estado=request.POST.get('estado').upper(),
            cep=request.POST.get('cep'),
        )
        messages.success(request, 'Endereço adicionado com sucesso!')
        return redirect('enderecos')
 
    enderecos = request.user.enderecos.all()
    return render(request, 'enderecos.html', {'enderecos': enderecos})
 
 
@login_required
def remover_endereco_view(request, pk):
    endereco = get_object_or_404(Endereco, pk=pk, user=request.user)
    endereco.delete()
    messages.success(request, 'Endereço removido.')
    return redirect('enderecos')
 
 
def logout_view(request):
    logout(request)
    return redirect('home')

#####FINAL PERFIL#####



@login_required
def carrinho_view(request):
    carrinho = request.session.get('carrinho', {})
 
    itens = []
    total_original = 0
    total_com_desconto = 0
 
    for produto_id, quantidade in carrinho.items():
        produto = get_object_or_404(Produto, pk=produto_id)
        subtotal_original = produto.preco_original * quantidade
        subtotal_desconto = produto.preco_desconto * quantidade
 
        itens.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal_original': subtotal_original,
            'subtotal_desconto': subtotal_desconto,
        })
 
        total_original += subtotal_original
        total_com_desconto += subtotal_desconto
 
    economia = total_original - total_com_desconto
 
    return render(request, 'carrinho.html', {
        'itens': itens,
        'total_original': total_original,
        'total_com_desconto': total_com_desconto,
        'economia': economia,
    })
 
 
@login_required
def adicionar_carrinho(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    carrinho = request.session.get('carrinho', {})

    pk_str = str(pk)
    carrinho[pk_str] = carrinho.get(pk_str, 0) + 1
    request.session['carrinho'] = carrinho

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        total_itens = sum(carrinho.values())
        return JsonResponse({'sucesso': True, 'total_itens': total_itens})

    messages.success(request, f'"{produto.titulo}" adicionado ao carrinho.')
    return redirect('home')
 
 
@login_required
def remover_carrinho(request, pk):
    carrinho = request.session.get('carrinho', {})
    pk_str = str(pk)
 
    if pk_str in carrinho:
        del carrinho[pk_str]
        request.session['carrinho'] = carrinho
 
    return redirect('carrinho')
 
 
@login_required
def atualizar_carrinho(request, pk):
    if request.method == 'POST':
        carrinho = request.session.get('carrinho', {})
        pk_str = str(pk)
        nova_quantidade = int(request.POST.get('quantidade', 1))
 
        if nova_quantidade <= 0:
            carrinho.pop(pk_str, None)
        else:
            carrinho[pk_str] = nova_quantidade
 
        request.session['carrinho'] = carrinho
 
    return redirect('carrinho')

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
@login_required
def alternar_favorito(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    favorito, criado = Favorito.objects.get_or_create(usuario=request.user, produto=produto)
    
    if not criado:
        favorito.delete()
        
    return redirect(request.META.get('HTTP_REFERER', 'home'))
