# Formato de números para es-cl: en Chile el separador de miles es el punto y el de decimales la coma (115.000,50)
# Django solo trae el formato de España (espacio como separador de miles), por eso se define uno propio
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','
NUMBER_GROUPING = 3
