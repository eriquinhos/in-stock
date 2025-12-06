# inStock - Sistema de Gerenciamento de Estoque

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?style=flat-square&logo=django&logoColor=white)
![MySQL](https://img.shields.io/badge/-MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![HTML5](https://img.shields.io/badge/-HTML5-E34C26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/-CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)
![Black](https://img.shields.io/badge/Black-000000?style=flat&logo=python&logoColor=white)
![isort](https://img.shields.io/badge/isort-1672B6?style=flat&logo=python&logoColor=white)
![Flake8](https://img.shields.io/badge/Flake8-264653?style=flat&logo=python&logoColor=white)
![DigitalOcean](https://img.shields.io/badge/DigitalOcean-0080FF?style=flat&logo=digitalocean&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat&logo=gunicorn&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat&logo=nginx&logoColor=white)
![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)

> Um sistema completo de controle de estoque para pequenas e médias empresas, com foco em organização, rastreabilidade e eficiência operacional.

## 👥 Contribuidores

|| Nome | Papel |
|------|------|-------|
| <img src="in_stock/app/static/images/team/Amanda.jpeg" width=32 height=32> | **Amanda Nogueira Lino** | Desenvolvimento Frontend / UI |
| <img src="in_stock/app/static/images/team/Eric.jpeg"   width=32 height=32> | **Eric Victor do Amaral da Silva** | DevOps / Backend / Testes / QA |
| <img src="in_stock/app/static/images/team/Gabi.jpeg"   width=32 height=32> | **Gabriela Cristina Moreira dos Santos** | Frontend / UX |
| <img src="in_stock/app/static/images/team/Nicole.jpeg" width=32 height=32> | **Nicole Cristine de Faria Santos** | Frontend / UI |
| <img src="in_stock/app/static/images/team/Tamires.jpeg" width=32 height=32> | **Tamires Morais Rodrigues** | Backend / Testes / QA |

## 📋 Descrição do Projeto

O inStock é uma aplicação web desenvolvida em Django que oferece uma solução robusta e intuitiva para gerenciamento de inventário. O sistema foi desenvolvido como projeto da disciplina de Engenharia de Software, seguindo boas práticas de desenvolvimento, testes automatizados e CI/CD.

### Principais Features

🔒 Autenticação e Controle de Acesso

📦 Gestão de Produtos

🔛 Controle de Movimentações

📊 Relatórios e Análises

⚙️ Gerenciamento de Fornecedores

## 🚀 Configuração e execução

### 1. Clonar o Repositório

```bash
git clone https://github.com/eriquinhos/in-stock.git
cd in-stock
```

### 2. Configurar o ambiente

🐧 Para Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
python pip install --upgrade pip
pip install -r requirements.txt
```

🪟 Para Windows

``` bash
python -m venv .venv
. .venv\Scripts\Activate
python pip install --upgrade pip
pip install -r requirements.txt
```

Alternativamente no ambiente Windows, pode-se executar o arquivo `venv-config.bat` para fazer a configuração automática do ambiente virtual

### 3. Configurar Banco de Dados

```bash
# Aplicar migrações
python manage.py migrate

# Criar superusuário (admin)
python manage.py createsuperuser
```

### 5. Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 6. Executar Servidor de Desenvolvimento

```bash
python manage.py runserver
```

Acesse a aplicação em: `http://localhost:8000` ou `127.0.0.1:8000`

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Dê um commit com as suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 🎯 Próximos passos

- [ ] API REST com DRF (Django REST Framework)
- [ ] Autenticação com OAuth2
- [ ] Integração com APIs de E-commerce
- [ ] App mobile (React Native/Flutter)
- [ ] Notificações em tempo real (WebSocket)
- [ ] Analytics avançado com Machine Learning
- [ ] Suporte multilíngue (i18n)

⭐ Se este projeto foi útil, considere dar uma estrela!
