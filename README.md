# Meu Novo Livro

Projeto desenvolvido com o intúito de facilitar a criação de livros através de uma diagramação facilitada para o usuário.

## Backend

Desenvolvimento utilizando Django e utilizando bibliotecas para executar algumas funções

### Bibliotecas utilizadas:

- weasyprint
- Pillow
- PyJWT
- Axios
- djangorestframework
- djangorestframework-simplejwt

### Dependências:

```
appnope==0.1.3
asgiref==3.7.2
asttokens==2.4.0
backcall==0.2.0
Brotli==1.1.0
cffi==1.16.0
cssselect2==0.7.0
decorator==5.1.1
Django==4.2.6
django-cors-headers==4.3.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
executing==2.0.0
fonttools==4.43.1
html5lib==1.1
ipython==8.16.1
jedi==0.19.1
matplotlib-inline==0.1.6
pango==0.0.1
parso==0.8.3
pexpect==4.8.0
pickleshare==0.7.5
Pillow==10.1.0
prompt-toolkit==3.0.39
ptyprocess==0.7.0
pure-eval==0.2.2
pycparser==2.21
pydyf==0.8.0
Pygments==2.16.1
PyJWT==2.8.0
pyphen==0.14.0
pytz==2023.3.post1
reportlab==4.0.6
setuptools==68.2.2
six==1.16.0
sqlparse==0.4.4
stack-data==0.6.3
tinycss2==1.2.1
traitlets==5.11.2
wcwidth==0.2.8
weasyprint==60.1
webencodings==0.5.1
zopfli==0.2.3
```

### Iniciar o projeto de forma local:

Clone o _[repositório](https://github.com/cosgon/meu_novo_livro_api)_

Execute o comando seguinte comando já dentro do repositório clonado e o pip configurado:

```
pip install -r requirements. txt
```

Após a instalação de todas as dependências rode o seguinte comando para iniciar o servidor:

```
python manage.py runserver
```

## Requisições

### Usuário

##### Registrar

> POST - api/register/
>
> Body
>
> ```json
> {
>   "username": "teste",
>   "email": "teste@teste.com",
>   "password": "112233",
>   "password2": "112233"
> }
> ```

##### Login

> POST - api/login/
>
> Body
>
> ```json
> {
>   "username": "teste",
>   "password": "112233"
> }
> ```

##### Atualização do usuário

> PATCH - api/users/\<user-id>/
>
> Header
>
> ```json
> {
>   "Authorization": "Bearer {token}"
> }
> ```
>
> Body
>
> ```json
> {
>   "first_name": "teste1",
>   "last_name": "Silva",
>   "cpf": "11026593980"
> }
> ```

##### Listar todos os usuários

> GET - api/users/
>
> Header
>
> ```json
> {
>   "Authorization": "Bearer {token}"
> }
> ```

### Livros

##### Listar todos os lívros

> GET - api/books/
>
> Não é necessário passar nenhuma informação

##### Listar livros de um usuário

> GET - api/books?user=\<user-id>
>
> Header
>
> ```json
> {
>   "Authorization": "Bearer {token}"
> }
> ```

##### Criar um livro

> POST - api/books/
>
> Header
>
> ```json
> {
>   "Authorization": "Bearer {token}"
> }
> ```
>
> Body (form-data)
>
> ```
> {
>   "name": "nome",
>   "content": "conteúdo",
>   "synopsis": "sinópse",
>   "value": valor,
>   "production": true,
>   "cover": file,
>   "title": "titulo"
>   "subtitle": "subtitulo",
>   "author": "nome do autor",
>   "isbn": "isbn",
>   "public_target": classificação indicativa,
>   "keywords": lista de palavras chave,
>   "book_style": (C, M) (clássico, moderno),
>   "price": preço
> }
> ```

##### Editar um livro

> PATCH - api/books/\<book_id>
>
> Header
>
> ```json
> {
>   "Authorization": "Bearer {token}"
> }
> ```
>
> Body (form-data)
>
> ```
> {
>   "content": "conteúdo",
>   "synopsis": "sinópse",
> }
> ```

##### Publicar um livro

> GET - api/books/\<book_id>/generate
>
> Header
>
> ```json
> {
>   "Authorization": "Bearer {token}"
> }
> ```
>
> Não precisa de body
