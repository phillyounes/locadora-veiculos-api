from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect

from sqlalchemy.exc import IntegrityError

from model import Session, Carro
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="API Locadora Veículos", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
carro_tag = Tag(name="Carro", description="Inclusão, alteração, visualização e remoção de carros à base")
# comentario_tag = Tag(name="Comentario", description="Adição de um comentário à um produtos cadastrado na base")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/carro', tags=[carro_tag],
          responses={"200": CarroViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_carro(form: CarroSchema):
    """Adiciona um novo Carro à base de dados

    Retorna uma representação dos carros
    """
    carro = Carro(
        placa=form.placa,
        nome=form.nome,
        modelo=form.modelo,
        marca=form.marca,
        alugado=False
        )
    logger.debug(f"Adicionando carro de placa: '{carro.placa}'")
    try:
        
        session = Session() # criando conexão com a base
        session.add(carro) # adicionando carro
        session.commit() # efetivando o camando de adição de novo item na tabela
        logger.debug(f"Adicionado carro de placa: '{carro.placa}'")
        return apresenta_carro(carro), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Carro de mesma placa já salva na base :/"
        logger.warning(f"Erro ao adicionar carro da placa '{carro.placa}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e: # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo carro :/"
        logger.warning(f"Erro ao adicionar carro '{carro.placa}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/carros', tags=[carro_tag],
         responses={"200": ListagemCarrosSchema, "404": ErrorSchema})
def get_carros():
    """Faz a busca por todos os carros cadastrados

    Retorna uma representação da listagem de carros.
    """
    logger.debug(f"Coletando carros ")
    
    session = Session() # criando conexão com a base
    carros = session.query(Carro).all() # fazendo a busca

    if not carros:
        return {"carros": []}, 200
    else:
        logger.debug(f"%d carros encontrados" % len(carros))
        print(carros)
        return apresenta_carros(carros), 200


@app.get('/carro', tags=[carro_tag],
         responses={"200": CarroViewSchema, "404": ErrorSchema})
def get_carro(query: CarroBuscaSchema):
    """Faz a busca por um carro a partir da placa do carro

    Retorna uma representação dos carros.
    """
    carro_placa = query.placa
    logger.debug(f"Coletando dados sobre carro #{carro_placa}")
    
    session = Session() # criando conexão com a base
    carro = session.query(Carro).filter(Carro.placa == carro_placa).first() # fazendo a busca

    if not carro:
        # se o carro não foi encontrado
        error_msg = "Carro não encontrado na base :/"
        logger.warning(f"Erro ao buscar carro '{carro_placa}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Carro encontrado: '{carro.placa}'")
        return apresenta_carro(carro), 200 # retorna a representação de carro


@app.delete('/carro', tags=[carro_tag],
            responses={"200": CarroDelSchema, "404": ErrorSchema})
def del_carro(query: CarroBuscaSchema):
    """Deleta um carro a partir do id do carro informado

    Retorna uma mensagem de confirmação da remoção.
    """
    carro_placa = query.placa
    print(carro_placa)
    logger.debug(f"Deletando dados sobre carro #{carro_placa}")
    
    session = Session() # criando conexão com a base
    count = session.query(Carro).filter(Carro.placa == carro_placa).delete() # fazendo a remoção
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado carro #{carro_placa}")
        return {"mesage": "carro removido", "id": carro_placa}
    else:
        # se o carro não foi encontrado
        error_msg = "Carro não encontrado na base :/"
        logger.warning(f"Erro ao deletar carro #'{carro_placa}', {error_msg}")
        return {"mesage": error_msg}, 404

@app.put('/carro/aluga', tags=[carro_tag],
         responses={"200": CarroViewSchema, "404": ErrorSchema})
def aluga_carro(query: CarroBuscaSchema):
    """Marca carro como alugado = True
    Retorna uma mensagem de confirmação do aluguel.
    """
    
    carro_placa = query.placa
    print(carro_placa)
    logger.debug(f"Marcando carro #{carro_placa} como alugado")
    
    count = atualizaCarroAlugado(carro_placa, True)

    if (count == -1):
        logger.debug(f"Carro #{carro_placa} já está alugado. Faça a devolução para poder alugar novamente.")
        return {"mesage": "Carro já está alugado. Faça a devolução para poder alugar novamente.", "placa": carro_placa}

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Carro #{carro_placa} alugado")
        return {"mesage": "carro alugado", "placa": carro_placa}
    else:
        # se o carro não foi encontrado
        error_msg = "Carro não encontrado na base :/"
        logger.warning(f"Erro ao alugar o carro #'{carro_placa}', {error_msg}")
        return {"mesage": error_msg}, 404

@app.put('/carro/devolve', tags=[carro_tag],
         responses={"200": CarroViewSchema, "404": ErrorSchema})
def devolve_carro(query: CarroBuscaSchema):
    """Marca carro como alugado = False
    Retorna uma mensagem de confirmação da devolução
    """
    
    carro_placa = query.placa
    print(carro_placa)
    logger.debug(f"Marcando carro #{carro_placa} como devolvido")
    
    count = atualizaCarroAlugado(carro_placa, False)

    if (count == -1):
        logger.debug(f"Carro #{carro_placa} deve estar alugado para ser devolvido")
        return {"mesage": "carro deve estar alugado para ser devolvido", "placa": carro_placa}

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Carro #{carro_placa} devolvido")
        return {"mesage": "carro devolvido", "placa": carro_placa}
    else:
        # se o carro não foi encontrado
        error_msg = "Carro não encontrado na base :/"
        logger.warning(f"Erro ao alugar o carro #'{carro_placa}', {error_msg}")
        return {"mesage": error_msg}, 404

def atualizaCarroAlugado(carro_placa: str, flagAlugado: bool):
    session = Session() # criando conexão com a base

    carro = session.query(Carro).filter(Carro.placa == carro_placa).first()
    
    if (carro.placa == ''):
        return 0
    elif (carro.alugado == flagAlugado):
        return -1


    count = session.query(Carro).filter(Carro.placa == carro_placa) \
        .update({Carro.alugado: flagAlugado}, synchronize_session=False)
    session.commit()
    return count