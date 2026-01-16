def normalizar_evento(nombre):
    n = str(nombre).lower()

    if "incompleto" in n or "perdido" in n:
        return "perdida"

    if "completo" in n or "ganado" in n:
        return "ganado"

    return "otro"


def carril(x):
    if x < 100/3:
        return "Izquierdo"
    elif x < 2*100/3:
        return "Central"
    else:
        return "Derecho"


def zona(y):
    if y < 33:
        return "Defensiva"
    if y < 66:
        return "Creación"
    return "Finalización"

def enrich(df):
    df["evento_raw"] = df["event"]
    df["event"] = df["event"].apply(normalizar_evento)

    # 🔁 Normalizamos eje X (sentido de ataque)
    df["x_norm"] = 100 - df["x"]

    # 🎯 Carriles en tercios exactos
    df["carril"] = df["x_norm"].apply(carril)
    df["zona"] = df["y"].apply(zona)

    return df
