from enum import Enum

class Grade(Enum):

    INFANTIL = "Ensino Infantil"
    ANO_1 = "1ᵒ Ano"
    ANO_2 = "2ᵒ Ano"
    ANO_3 = "3ᵒ Ano"
    ANO_4 = "4ᵒ Ano"
    ANO_5 = "5ᵒ Ano"


class Purpose(Enum):
    EDUCACAO = "Educacional"
    ENTRETENIMENTO = "Lúdico"