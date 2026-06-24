from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

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
    
    
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Adicionado em")

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


class Avaliacao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='avaliacoes')
    nota = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Nota (1 a 5)")
    comentario = models.TextField(blank=True, null=True, verbose_name="Comentário")
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        ordering = ['-data_avaliacao']

    def __str__(self):
        return f"{self.nota} estrelas - {self.produto.titulo}"