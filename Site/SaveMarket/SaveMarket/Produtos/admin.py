from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import MercadoParceiro, Produto


class ProdutoInline(admin.TabularInline):
    model = Produto
    extra = 1
    fields = ('titulo', 'estoque', 'preco_original', 'preco_desconto', 'validade', 'imagem')


@admin.register(MercadoParceiro)
class MercadoParceiroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco', 'total_produtos')
    search_fields = ('nome',)
    inlines = [ProdutoInline]

    def total_produtos(self, obj):
        return obj.produtos.count()
    total_produtos.short_description = 'Produtos'


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'mercado', 'estoque', 'preco_original', 'preco_desconto', 'validade', 'status_validade')
    list_filter = ('mercado', 'validade')
    search_fields = ('titulo',)
    ordering = ('validade',)
    list_per_page = 20
    date_hierarchy = 'validade'

    def status_validade(self, obj):
        hoje = timezone.now().date()
        dias = (obj.validade - hoje).days
        if dias < 0:
            return format_html('<span style="color:red">{}</span>', 'Vencido')
        elif dias == 0:
            return format_html('<span style="color:orange">{}</span>', 'Vence hoje')
        elif dias <= 3:
            return format_html('<span style="color:#cc8800">⚠ {} dias</span>', dias)
        return format_html('<span style="color:green">{} dias</span>', dias)
    status_validade.short_description = 'Validade'