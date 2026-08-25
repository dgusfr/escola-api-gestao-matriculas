import re


def cpf_valido(numero_cpf: str) -> bool:
    """Valida se o CPF é válido usando o algoritmo dos dígitos verificadores."""
    cpf = re.sub(r"\D", "", str(numero_cpf))

    if len(cpf) != 11:
        return False

    # CPFs com todos os dígitos iguais são inválidos
    if cpf == cpf[0] * 11:
        return False

    # Calcula primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito_1 = 0 if resto < 2 else 11 - resto
    if int(cpf[9]) != digito_1:
        return False

    # Calcula segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito_2 = 0 if resto < 2 else 11 - resto
    if int(cpf[10]) != digito_2:
        return False

    return True


def nome_valido(nome: str) -> bool:
    """Valida se o nome contém apenas letras e espaços."""
    if not nome or not str(nome).strip():
        return False
    return bool(re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$", str(nome).strip()))


def celular_valido(celular: str) -> bool:
    """Valida se o celular possui 11 dígitos numéricos com DDD válido (ex: 11988887777)."""
    numero = re.sub(r"\D", "", str(celular))
    return bool(re.match(r"^[1-9]{2}9[0-9]{8}$", numero))
