"""Modelo de pedido y transiciones de estado."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Estado(str, Enum):
    REGISTRADO = "registrado"
    PREPARADO = "preparado"
    DESPACHADO = "despachado"
    ENTREGADO = "entregado"
    ANULADO = "anulado"


TRANSICIONES = {
    Estado.REGISTRADO: {Estado.PREPARADO, Estado.ANULADO},
    Estado.PREPARADO: {Estado.DESPACHADO, Estado.ANULADO},
    Estado.DESPACHADO: {Estado.ENTREGADO},
    Estado.ENTREGADO: set(),
    Estado.ANULADO: set(),
}


class TransicionInvalida(Exception):
    """Se intento una transicion de estado no permitida."""


@dataclass
class Linea:
    sku: str
    cantidad: int
    precio_unitario: float

    def subtotal(self) -> float:
        return round(self.cantidad * self.precio_unitario, 2)


@dataclass
class Pedido:
    codigo: str
    cliente: str
    lineas: list[Linea] = field(default_factory=list)
    estado: Estado = Estado.REGISTRADO
    creado_en: datetime = field(default_factory=datetime.now)

    def agregar_linea(self, linea: Linea) -> None:
        if self.estado is not Estado.REGISTRADO:
            raise TransicionInvalida(
                "solo se pueden agregar lineas a un pedido registrado"
            )
        self.lineas.append(linea)

    def total(self) -> float:
        return round(sum(linea.subtotal() for linea in self.lineas), 2)

    def unidades(self) -> int:
        return sum(linea.cantidad for linea in self.lineas)

    def cambiar_estado(self, nuevo: Estado) -> None:
        permitidos = TRANSICIONES[self.estado]
        if nuevo not in permitidos:
            raise TransicionInvalida(
                f"no se puede pasar de {self.estado.value} a {nuevo.value}"
            )
        self.estado = nuevo

    def esta_cerrado(self) -> bool:
        return self.estado in (Estado.ENTREGADO, Estado.ANULADO)


def agrupar_por_cliente(pedidos: list[Pedido]) -> dict[str, list[Pedido]]:
    agrupados: dict[str, list[Pedido]] = {}
    for pedido in pedidos:
        agrupados.setdefault(pedido.cliente, []).append(pedido)
    return agrupados


def pedidos_abiertos(pedidos: list[Pedido]) -> list[Pedido]:
    return [p for p in pedidos if not p.esta_cerrado()]

def calcular_descuento_por_volumen(pedido: Pedido) -> float:
    # Funcion para el ejercicio 3
    if pedido.esta_cerrado():
        return 0.0

    unidades = pedido.unidades()
    total = pedido.total()
    descuento = 0.0

    if unidades >= 50:
        descuento = 0.15
    elif unidades >= 20:
        descuento = 0.10
    elif unidades >= 10:
        descuento = 0.05

    if total > 5000:
        descuento += 0.05
    elif total > 2000:
        descuento += 0.02

    if descuento > 0.20:
        descuento = 0.20

    return round(total * descuento, 2)
