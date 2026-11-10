from django.db import models

class Vendedor(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Cliente(models.Model):
    id_cliente = models.CharField(max_length=20, unique=True)
    razao_social = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    cep = models.CharField(max_length=10, null=True, blank=True)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    data_cadastro = models.DateField(null=True, blank=True)
    vendedor_responsavel = models.ForeignKey(Vendedor, on_delete=models.RESTRICT, related_name='clientes')
    precisa_revisao = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id_cliente} - {self.razao_social}"

class Auditoria(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='auditorias')
    campo = models.CharField(max_length=50)
    valor_original = models.CharField(max_length=255, null=True, blank=True)
    valor_tratado = models.CharField(max_length=255, null=True, blank=True)
    criterio = models.CharField(max_length=255)
    data_auditoria = models.DateTimeField(auto_now_add=True)

class CepCache(models.Model):
    cep = models.CharField(max_length=8, unique=True)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    valido = models.BooleanField(default=True)
    data_consulta = models.DateTimeField(auto_now_add=True)