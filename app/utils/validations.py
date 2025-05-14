import re

def validar_rut(rut: str) -> bool:
    rut = rut.upper().replace("-", "").replace(".", "")
    aux = rut[:-1]
    dv = rut[-1:]
    revertido = map(int, reversed(aux))
    factores = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(revertido, factores))
    res = (-s) % 11
    if res == 10:
        return dv == "K"
    else:
        return dv == str(res)

def validar_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validar_telefono(telefono: str) -> bool:
    return telefono.isdigit() and (8 <= len(telefono) <= 12)
