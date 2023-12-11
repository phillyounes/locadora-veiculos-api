from sqlalchemy import Column, String, Integer, DateTime, Boolean
from datetime import datetime
from typing import Union

from  model import Base

class Carro(Base):
    __tablename__ = 'carro'

    id = Column("id_carro", Integer, primary_key=True)
    placa = Column(String(10), unique=True)
    nome = Column(String(50))
    modelo = Column(String(50))
    marca = Column(String(50))
    alugado = Column(Boolean, default=False)
    data_cadastro = Column(DateTime, default=datetime.now())

    def __init__(self, placa:str, nome:str, modelo:str, marca:str, alugado: Union[bool,None] = False,
                 data_cadastro:Union[DateTime, None] = None):
        """
        Cria o registro de um Carro

        Argumentos:
            placa: placa do carro
            nome: nome do carro
            modelo: modelo do carro
            marca: marca do carro
            alugado: define se o carro está alugado
            data_cadastro: data de quando o carro foi cadastrado
        """
        self.placa = placa
        self.nome = nome
        self.modelo = modelo
        self.marca = marca

        if alugado:
            self.alugado = alugado
        if data_cadastro:
            self.data_cadastro = data_cadastro