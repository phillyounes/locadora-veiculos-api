from pydantic import BaseModel
from typing import List
from model.carro import Carro

class CarroSchema(BaseModel):
    """ Define como um novo carro a ser inserido deve ser representado
    """
    placa: str = "ABC1A23"
    nome: str = "Honda Fit"
    modelo: str = "Fit"
    marca: str = "Honda"


class CarroBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no Id do carro.
    """
    placa: str = "ABC1A23"


class ListagemCarrosSchema(BaseModel):
    """ Define como uma listagem de carros será retornada.
    """
    carros:List[CarroSchema]


def apresenta_carros(carros: List[Carro]):
    """ Retorna uma representação do carro seguindo o schema definido em
        CarroViewSchema.
    """
    result = []
    for carro in carros:
        result.append({
            "placa": carro.placa,
            "nome": carro.nome,
            "modelo": carro.modelo,
            "marca": carro.marca,
            "alugado": carro.alugado,
        })

    return {"carros": result}


class CarroViewSchema(BaseModel):
    """ Define como um carro será retornado: carro.
    """
    id: int = 1
    placa: str = "ABC1A23"
    nome: str = "Honda Fit"
    modelo: str = "Fit"
    marca: str = "Honda"
    alugado: bool = False

class CarroDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str
    nome: str

def apresenta_carro(carro: Carro):
    """ Retorna uma representação do carro seguindo o schema definido em
        CarroViewSchema.
    """
    return {
        "id": carro.id,
        "placa": carro.placa,
        "nome": carro.nome,
        "modelo": carro.modelo,
        "marca": carro.marca,
        "alugado": carro.alugado
    }
