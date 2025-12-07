from django.shortcuts import render


def minha_view_de_produtos(request):
    # Aqui sim você aponta para o nome do arquivo HTML físico
    return render(request, "GestaoProdutos.html")
