from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
 
 
class MercadoParceiro(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome")
    endereco = models.CharField(max_length=500, verbose_name="Endereço")
 
    class Meta:
        verbose_name = "Mercado Parceiro"
        verbose_name_plural = "Mercados Parceiros"
 
    def __str__(self):
        return self.nome
 
 
class Produto(models.Model):
    mercado = models.ForeignKey(
        MercadoParceiro,
        on_delete=models.CASCADE,
        related_name="produtos",
        verbose_name="Mercado Parceiro",
    )
    titulo = models.CharField(max_length=255, verbose_name="Título")

    categoria = models.CharField(
    max_length=100,
    verbose_name="Categoria",
    default="Outros"
    )
    preco_original = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Preço Original"
    )
    preco_desconto = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Preço com Desconto"
    )
    validade = models.DateField(verbose_name="Validade")
 
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["validade"]
 
    def __str__(self):
        return f"{self.titulo} — {self.mercado.nome}"
 
    @property
    def percentual_desconto(self):
        if self.preco_original > 0:
            desconto = (1 - self.preco_desconto / self.preco_original) * 100
            return round(desconto, 1)
        return 0

    @property
    def dias_para_vencer(self):
      delta = self.validade - timezone.now().date()
      return max(delta.days, 0)

class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritos')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='favoritado_por')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'produto')
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"

    def __str__(self):
        return f"{self.usuario.username} - {self.produto.titulo}"