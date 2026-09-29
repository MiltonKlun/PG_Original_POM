"""Storefront copy (es-AR) that page objects and tests match against.

One place to update when the store changes its wording. Values marked
"simulated" exist only in the local storefront.
"""

import re

STORE_TITLE = re.compile("PG Original", re.I)

# Header, menu and footer
SEARCH_LINK = "Buscador"
SHOP = "SHOP"
ALL_PRODUCTS = "Ver todos los productos"

# Listing and product pages
OUT_OF_STOCK = "Sin stock"
NO_RESULTS = "No encontramos nada para"
LOAD_MORE = "Mostrar más productos"

# Cart drawer
REMOVE_LINE = "Quitar"

# Login and password reset
LOGIN_SUBMIT = re.compile("Iniciar", re.I)
LOGIN_EMAIL_LABEL = "Email"
LOGIN_PASSWORD_LABEL = "Contraseña"
FORGOT_PASSWORD = re.compile("Olvidaste")
RESET_HEADING = re.compile("CAMBIAR CONTRASE", re.I)
INVALID_CREDENTIALS = "Credenciales incorrectas"  # simulated

# Contact form
CONTACT_NAME = "Nombre"
CONTACT_EMAIL = "Email"
CONTACT_MESSAGE = "Mensaje"
CONTACT_SUBMIT = "Enviar"
