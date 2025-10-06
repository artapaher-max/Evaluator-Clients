import math
import numpy_financial as npf
from app.services.settings_service import SettingsService

def calcular_pago_mensual(capital, tasa_anual, plazo):
  tasa_mensual = tasa_anual / 12
  nper = plazo
  pago = npf.pmt(tasa_mensual, nper, -capital)
  return pago

def generar_prompt_cliente(data, perfil_similar=None, moto_similar=None, cast_similar=None, riesgo_similar=None, numero=None, numero_riesgos=None, indice_paz=None):
    
    settings_service = SettingsService()
    settings = settings_service.load_settings()
    
    producto = data.get('producto', '').strip().lower()
    
    porcentaje_liquidacion = settings.get('PORCENTAJE_LIQUIDACION', 0.66)
    solvencia_monto_minimo = settings.get('SOLVENCIA_ACEPTABLE_MONTO_MINIMO', 3000)
    solvencia_porcentaje_minimo = settings.get('SOLVENCIA_ACEPTABLE_PORCENTAJE_MINIMO', 20)
    excelente = settings.get('PUNTOS_REPORTE_EXCELENTE', 0.7)
    bueno = settings.get('PUNTOS_REPORTE_BUENO', 0.5)
    regular = settings.get('PUNTOS_REPORTE_REGULAR', 0.3)
    malo_pequeno = settings.get('PUNTOS_REPORTE_MALO_PEQUENO', -0.3)
    muy_malo = settings.get('PUNTOS_REPORTE_MALO_GRANDE', -1.0)
    sin_historial = 0.0
    excelente2 = settings.get('PUNTOS_REPORTE_EXCELENTE_AVAL', 0.3)
    bueno2 = settings.get('PUNTOS_REPORTE_BUENO_AVAL', 0.2)
    regular2 = settings.get('PUNTOS_REPORTE_REGULAR_AVAL', 0.1)
    malo_pequeno2 = settings.get('PUNTOS_REPORTE_MALO_PEQUENO_AVAL', -0.1)
    muy_malo2 = settings.get('PUNTOS_REPORTE_MALO_GRANDE_AVAL', -0.2)
    sin_historial2 = 0.0
    negativos = settings.get('NEGATIVOS', "NO")
    utilizar_ia = data.get('utilizar_ia', "SI")
    ingresosdiariobruto = settings.get('IDB', 350)
    aval = data.get('aval',"no")
    
    if indice_paz:
        Calificaciones = indice_paz.get('CalHom', 0) + indice_paz.get('CalDel', 0) + indice_paz.get('CalViol', 0) + indice_paz.get('CalArm', 0) + indice_paz.get('CalMie', 0)
    else:
        Calificaciones = 0 # Asignamos 0 si no se encontró un perfil de índice de paz
    CalRiesgo = Calificaciones * 10 / 25
    
    monto_str = data.get('monto_credito', 0)
    monto = float(monto_str)
    capital_prestamo = monto  # Monto del prestamo
    
    interes = data.get('tasa', "76")
    interes_num = float(interes)

    if interes_num>=100:
        tasa_str = interes
        tasa = float(tasa_str)/100
    else:    
        tasa_str = "0." + interes
        if tasa_str=="0.10" or tasa_str=="0.20" or tasa_str=="0.30" or tasa_str=="0.40" or tasa_str=="0.50" or tasa_str=="0.60" or tasa_str=="0.70" or tasa_str=="0.80" or tasa_str=="0.90":
            tasa_str = tasa_str
            tasa = float(tasa_str)
            
        elif tasa_str=="0.1" or tasa_str=="0.2" or tasa_str=="0.3" or tasa_str=="0.4" or tasa_str=="0.5" or tasa_str=="0.6" or tasa_str=="0.7" or tasa_str=="0.8" or tasa_str=="0.9":
            tasa_str = "0.0" + interes
            tasa = float(tasa_str)
        else:
            tasa = float(tasa_str)
        
    # print(tasa)
    
    # try:
    #     tasa_str = "0." + data.get('tasa', 76)
    #     tasa = float(tasa_str)
    #     if tasa==0.1 or tasa==0.2 or tasa==0.3 or tasa==0.4 or tasa==0.5 or tasa==0.6 or tasa==0.7 or tasa==0.8 or tasa==0.9:
    #         tasa_str = "0.0" + data.get('tasa', 0)
    #         tasa = float(tasa_str)
    #     else:
    #         tasa = tasa
    # except:
    #     tasa = 0.76
    tasa_interes_anual = tasa  # Tasa de interes anual
    
    tasa_mensual = tasa/12
    
    plazo_str = data.get('plazo_credito', 24)  # Plazo en años
    plazo_c = float(plazo_str)
    plazo = plazo_c

    pago = calcular_pago_mensual(capital_prestamo, tasa_interes_anual, plazo)
    pago = float(pago)
    total_pagos = abs(pago * plazo)
    
    ingresos_str = data.get('ingresos', 0)
    egresos_str= data.get('egresos', 0)
    ingresos = float(ingresos_str)
    egresos = float(egresos_str)
    ingreso_limpio = ingresos - egresos
    ingreso_neto = ingreso_limpio - pago
    
    
    if moto_similar:
        ingresos_moto_str = moto_similar.get('RangoIngresoDiarioBruto', ingresosdiariobruto)
        ingresos_moto = float(ingresos_moto_str)
    else:
        # Usamos el valor por defecto si no se encontró un perfil de moto
        ingresos_moto = float(ingresosdiariobruto)
    
    ingresos_moto_25 = ingresos_moto * 25
    
    por_ingresos_str = data.get('ingresos', 1500)
    por_ingresos = float(por_ingresos_str)
    
    ingresos_total_str = data.get('ingresos_extra', "0")
    ingresos_total = float(ingresos_total_str) + ingreso_neto
    
    ingreso_por = (ingresos_total / ingresos)*100
    
    
    # Calculo del monto a liquidar minimo (esto es si se desea liquidar despues de una cantidad de meses minima definida idea)
    
    tasa_mensual = tasa/12
    
    liqui = monto * porcentaje_liquidacion # <-- Variable modificable en un panel de control
    liquidacion = liqui / pago
    liqui_meses = math.ceil(liquidacion)
    
    suma_interes = 0
    suma_abono = 0
    abono_capital = 0
    k = 1
    limite_k = plazo

    while suma_abono < liqui and k <= limite_k:
        abono_capital = (pago - (monto * tasa_mensual)) * ((1 + tasa_mensual) ** (k - 1))
        suma_abono = suma_abono + abono_capital
        abono_interes = pago - abono_capital
        suma_interes = suma_interes + abono_interes
        k += 1
        
    liqui_monto = abs(monto - suma_abono)
    
    punto_reporte_credito = 0.0
    
    reporte = data.get('reporte_credito')
    if reporte == "excelente":
        punto_reporte_credito = excelente
    elif reporte == "bueno":
        punto_reporte_credito = bueno
    elif reporte == "regular":
        punto_reporte_credito = regular
    elif reporte == "malo_pequeno":
        punto_reporte_credito = malo_pequeno
    elif reporte == "muy_malo":
        punto_reporte_credito = muy_malo
    elif reporte == "sin_historial":
        punto_reporte_credito = sin_historial
    else:
        punto_reporte_credito
        
    punto_reporte_credito_aval = 0.0
    
    reporte_aval = data.get('reporte_credito_aval')
    if reporte_aval == "excelente":
        punto_reporte_credito_aval = excelente2
    elif reporte_aval == "bueno":
        punto_reporte_credito_aval = bueno2
    elif reporte_aval == "regular":
        punto_reporte_credito_aval = regular2
    elif reporte_aval == "malo_pequeno":
        punto_reporte_credito_aval = malo_pequeno2
    elif reporte_aval == "muy_malo":
        punto_reporte_credito_aval = muy_malo2
    elif reporte_aval == "sin_historial":
        punto_reporte_credito_aval = sin_historial2
    else:
        punto_reporte_credito_aval
        
    # PROCESO DE CALCULO PARA CALIFICACION MANUAL FINAL
    
    resilencia = float(indice_paz.get('Resiliencia', 'N/A'))
    mora_min = riesgo_similar.get('IM_min', 'N/A')
    mora_max = riesgo_similar.get('IM_max', 'N/A')
    mora_prom = riesgo_similar.get('IM_prom', 'N/A')
    
    score_manual = 0
    
    if ingreso_neto >= solvencia_monto_minimo: score_manual += 0.5
    
    if ingreso_por <= 20: score_manual += 0 
    elif ingreso_por > 20 and ingreso_por <= 30: score_manual += 0.5
    elif ingreso_por > 30 and ingreso_por <= 50: score_manual += 1
    elif ingreso_por > 50: score_manual += 1.5
    
    if punto_reporte_credito: score_manual += punto_reporte_credito
    
    if CalRiesgo >= 0 and CalRiesgo <= 2: score_manual += 1
    elif CalRiesgo > 2 and CalRiesgo <= 4: score_manual += 0.8
    elif CalRiesgo > 4 and CalRiesgo <= 6: score_manual += 0.6
    elif CalRiesgo > 6 and CalRiesgo <= 8: score_manual += 0.4
    elif CalRiesgo > 8 and CalRiesgo <= 10: score_manual += 0.2
    
    if aval == "si": score_manual += 0.5
    if punto_reporte_credito_aval: score_manual += punto_reporte_credito_aval
    
    if resilencia >= 0 and resilencia <= 6: score_manual += 1
    elif resilencia > 6 and resilencia <= 12: score_manual += 0.8
    elif resilencia > 12 and resilencia <= 18: score_manual += 0.6
    elif resilencia > 18 and resilencia <= 24: score_manual += 0.4
    elif resilencia > 24 and resilencia <= 32: score_manual += 0.2
    
    if mora_max < 1: score_manual += 0.5
    if mora_min == 0: score_manual += 0.5
    if mora_prom <= 1: score_manual += 0.5
    
    garantia = data.get('garantia', 'N/A')
    
    if garantia == "unidad_financiada": score_manual +=0.5
    elif garantia == "garantia_prendaria": score_manual +=0.4
    
    permiso = data.get('permiso', 'N/A')
    
    if permiso == "si": score_manual += 0.3
    if permiso == "tramite": score_manual += 0.1
    
    evaling = (ingreso_neto - pago)
    
    inv_evaling = ingresosdiariobruto * 20
    
    if producto == "c-movil":
        if evaling > 1000: score_manual += 0.2
    elif producto in ["c-facil","c-especial","c-auto","c-emprendedor nuevo"]:
        if inv_evaling > 1000: score_manual += 0.2
        
    # Calculos para calificar riesgo general del cliente:
    riesgo_calificacion_1 = 0
    indice_top = float(indice_paz.get('Clasificacion', 16))
    if indice_top >= 0 and indice_top <= 6: riesgo_calificacion_1 += 0.2
    elif indice_top > 6 and indice_top <= 12: riesgo_calificacion_1 += 0.4
    elif indice_top > 12 and indice_top <= 18: riesgo_calificacion_1 += 0.6
    elif indice_top > 18 and indice_top <= 24: riesgo_calificacion_1 += 0.8
    elif indice_top > 24 and indice_top <= 32: riesgo_calificacion_1 += 1
    
    Plazo_Promedio= riesgo_similar.get('Plazo_Promedio_Meses', 'N/A')
    plazo_riesgo = abs(plazo-Plazo_Promedio)
    if plazo_riesgo <= 2: riesgo_calificacion_1 += 0.3 # esto significa que el cliente paga sus pagos sin adelantar tantos pagos comparado con el promedio de un perfil de riesgo
    elif plazo_riesgo > 3: riesgo_calificacion_1 += 0.5 # esto significa que el cliente paga sus pagos y adelanta pagos comparado con el promedio de un perfil de riesgo riesgo un poco mayor por que se percibia pago en tiempo pero el adelantar es aunque bueno un acto que requiere comprobacion de ingresos
    
    # comparaciones para evaluar con informacion de castigados aqui solo se suma hasta un maximo de 1 punto a riesgo_calificacion_1
    
    por_cast = cast_similar.get('%CapCastProm', 'N/A')
    min_cast_mes = cast_similar.get('MinMeses', 'N/A')
    max_cast_mes = cast_similar.get('MaxMeses', 'N/A')
    
    if por_cast <= 10: riesgo_calificacion_1 += 0.2
    if por_cast > 10 and por_cast <= 40: riesgo_calificacion_1 += 0.5
    if por_cast > 40 and por_cast <= 70: riesgo_calificacion_1 += 0.7
    if por_cast > 70 and por_cast <= 100: riesgo_calificacion_1 += 1
    
    # ---
    
    pago_min = perfil_similar.get('Pago_Minimo', 0)
    pago_max = perfil_similar.get('Pago_Maximo', 1)
    
    if pago >= pago_max: riesgo_calificacion_1 += 1
    if pago >= pago_min and pago <= pago_max: riesgo_calificacion_1 += 0.5
    if pago <= pago_min: riesgo_calificacion_1 +=0.2
    
    tasa_prom = float(perfil_similar.get('Interes', 'N/A'))
    
    if pago > tasa_prom: riesgo_calificacion_1 += 1
    if pago <= tasa_prom: riesgo_calificacion_1 += 0.5
    
    if mora_prom > 1: riesgo_calificacion_1 += 0.5
    
    # Calificacion maxima en riesgo_calificacion_1 es 5 entonces la convertimos en una calificacion en base a 10
    
    riesgo_calif = riesgo_calificacion_1 * 10 / 5
    
    # --- ya con eso hacemos una operacion donde le damos un valor a CalifRiesgo que es la variable resultante del Riesgo segun las variables del indice de paz que no incluyen las consideradas en riesgos_calif y la sumamos a riesgos_calif
    
    if CalRiesgo > 0 and CalRiesgo <= 2: riesgo_calif += 0.2
    elif CalRiesgo > 2 and CalRiesgo <= 4: riesgo_calif += 0.4
    elif CalRiesgo > 4 and CalRiesgo <= 6: riesgo_calif += 0.6
    elif CalRiesgo > 6 and CalRiesgo <= 8: riesgo_calif += 0.8
    elif CalRiesgo > 8 and CalRiesgo <= 10: riesgo_calif += 1
    
    Bajo = "Bajo"
    Medio = "Medio"
    Alto = "Alto"
    Critico = "Critico"
    
    texto_riesgo = ""
    
    if riesgo_calif == 0: texto_riesgo = "Nulo"
    elif riesgo_calif > 0 and riesgo_calif <= 3: texto_riesgo = Bajo
    elif riesgo_calif > 3 and riesgo_calif <= 6.5: texto_riesgo = Medio
    elif riesgo_calif > 6.5 and riesgo_calif <= 8.5: texto_riesgo = Alto
    elif riesgo_calif > 8.5 and riesgo_calif <= 10: texto_riesgo = Critico
    else: texto_riesgo = "No se puedo Calcular el Riesgo"
    
    # hasta aqui la calificacion maxima es 8 por lo que se adapta una ecuacion para obtener un valor sobre una escala de 10
    
    score_final = score_manual * 10 / 8 # <-- Regla de tres JAJA
    
    A = "Autorizado"
    B = "Pre-Autorizado"
    C = "Observado Condicionado Nivel 1"
    D = "Condicionado Nivel 2"
    F = "Rechazado"
    
    texto_calif = ""
    
    if score_final >= 0 and score_final <= 5.5: texto_calif = F
    elif score_final > 5.5 and score_final <= 6.5: texto_calif = D
    elif score_final > 6.5 and score_final <= 7.5: texto_calif = C
    elif score_final > 7.5 and score_final <= 8.5: texto_calif = B
    elif score_final > 8.5 and score_final <= 10: texto_calif = A
    else: texto_calif
    
    # FIN DE CALCULO DE CALIFICACION MANUAL FINAL
        
    perfil_info = "No se encontraron datos historicos de un perfil directamente comparable."
    if perfil_similar:
        perfil_info = f"""
    Adicionalmente, hemos encontrado un perfil C-MOVIL en nuestra base de datos que coincide 
    con el cliente. Informacion util para evaluar:
    - Entidad: {perfil_similar.get('Entidad', 'N/A')}
    - Sucursal: {perfil_similar.get('Sucursal', 'N/A')}
    - Producto: {perfil_similar.get('Producto', 'N/A')}
    - Rango de Edad: {perfil_similar.get('RangoEdad', 'N/A')}
    - Numero de Clientes en este perfil: {perfil_similar.get('Numero_de_Clientes', 'N/A')}
    - Monto de Credito Promedio Otorgado: ${perfil_similar.get('Promedio_de_Monto', 0):,.2f}
    - Plazo Promedio: {perfil_similar.get('Plazo_Promedio_Meses', 'N/A')} meses
    - Saldo Promedio por Cliente (Insoluto/Clientes): ${perfil_similar.get('Insoluto/Clientes', 0):,.2f}
    - Genero Mas Comun: {perfil_similar.get('Genero_Comun', 'N/A')}
    - Estado Civil Mas Comun: {perfil_similar.get('EstCiv_Comun', 'N/A')}
    """
    
    if producto in ["c-movil", "c-mototaxista"]:
        producto_info = "No se encontraron datos historicos de un Mototaxi directamente comparable."
        if moto_similar:
            producto_info = f"""
    Adicionalmente, se agregan datos de un perfil de cliente, informativo que coincide 
    con la ubicacion para un C-MOVIL. Informacion util para evaluar:
    - Entidad o Sucursal: {moto_similar.get('EntidadSucursal', 'N/A')}
    - Estatus Legal: {moto_similar.get('EstatusLegal', 'N/A')}
    - Marco Legal: {moto_similar.get('MarcoLegal', 'N/A')}
    - Costos Regulatorios: {moto_similar.get('CostosRegulatorios', 'N/A')}
    - Promedio Ingreso Diario Bruto: {moto_similar.get('RangoIngresoDiarioBruto', 'N/A')}
    - Costos Operativos Diarios Promedio: {moto_similar.get('CostosOperativosDiariosPromedio', 'N/A')}
    - Ganancia Neta Diaria Estimada: {moto_similar.get('GananciaNetaDiariaEstimada', 'N/A')}
    - Notas Clave: {moto_similar.get('NotasClave', 'N/A')}
    - Interes promedio en el perfil: {perfil_similar.get('Interes', 'N/A')}%
    - Pago minimo realizado: $ {perfil_similar.get('Pago_Minimo', 'N/A'):,.2f}
    - Pago maximo realizado: $ {perfil_similar.get('Pago_Maximo', 'N/A'):,.2f}
    
    """
    elif producto == "c-facil":
        producto_info = "No se encontraron datos historicos de un C-Facil directamente comparable."
        if moto_similar:
            producto_info = f"""
    Adicionalmente, hemos encontrado en nuestra base de datos un perfil que coincide 
    con el producto C-FACIL. Informacion util para evaluar:
    - Entidad: {moto_similar.get('Entidad', 'N/A')}
    - Sucursal: {moto_similar.get('Sucursal', 'N/A')}
    - Rango Edad Cliente promedio: {moto_similar.get('RangoEdad', 'N/A')}
    - Rango de dias que tarda en pagar: {moto_similar.get('BUCKET', 'N/A')}
    - Monto Comun solicitado: $ {moto_similar.get('Monto_Comun', 'N/A'):,.2f}
    - Plazo Promedio: {moto_similar.get('Plazo_Promedio_Meses', 'N/A')}
    - Estado Civil Comun: {moto_similar.get('EstCiv_Comun', 'N/A')}
    - Interes promedio en el perfil: {moto_similar.get('Interes', 'N/A')}%
    - Pago minimo realizado: $ {moto_similar.get('Pago_Minimo', 'N/A'):,.2f}
    - Pago maximo realizado: $ {moto_similar.get('Pago_Maximo', 'N/A'):,.2f}
    - Cantidad maxima de pagos hechos: {moto_similar.get('Pagos_Promedio', 'N/A')} (en 12 meses entran entre 26 y 27 pagos promedio)
    - Genero: {moto_similar.get('Genero', 'N/A')}
    - Estado Civil Comun: {moto_similar.get('EstCiv_Comun', 'N/A')}
    - Numero de Clientes que cumplen este perfil: {moto_similar.get('Numero_de_Clientes', 'N/A')} de un total de {numero}
    
    """
    elif producto == "c-emprendedor nuevo":
        producto_info = "No se encontraron datos historicos de un C-Emprendedor Nuevo directamente comparable."
        if moto_similar:
            producto_info = f"""
    Adicionalmente, hemos encontrado en nuestra base de datos un perfil que coincide 
    con el producto C-EMPRENDEDOR NUEVO. Informacion util para evaluar:
    - Entidad: {moto_similar.get('Entidad', 'N/A')}
    - Sucursal: {moto_similar.get('Sucursal', 'N/A')}
    - Rango Edad Cliente promedio: {moto_similar.get('RangoEdad', 'N/A')}
    - Rango de dias que tarda en pagar: {moto_similar.get('BUCKET', 'N/A')}
    - Monto Comun solicitado: $ {moto_similar.get('Monto_Comun', 'N/A'):,.2f}
    - Plazo Promedio: {moto_similar.get('Plazo_Promedio_Meses', 'N/A')}
    - Estado Civil Comun: {moto_similar.get('EstCiv_Comun', 'N/A')}
    - Interes promedio en el perfil: {moto_similar.get('Interes', 'N/A')}%
    - Pago minimo realizado: $ {moto_similar.get('Pago_Minimo', 'N/A'):,.2f}
    - Pago maximo realizado: $ {moto_similar.get('Pago_Maximo', 'N/A'):,.2f}
    - Cantidad maxima de pagos hechos: {moto_similar.get('Pagos_Promedio', 'N/A')} (en 12 meses entran entre 26 y 27 pagos promedio)
    - Genero: {moto_similar.get('Genero', 'N/A')}
    - Estado Civil Comun: {moto_similar.get('EstCiv_Comun', 'N/A')}
    - Numero de Clientes que cumplen este perfil: {moto_similar.get('Numero_de_Clientes', 'N/A')} de un total de {numero}
    
    """
    elif producto == "c-auto":
        producto_info = "No se encontraron datos historicos de un C-Auto directamente comparable."
        if moto_similar:
            producto_info = f"""
    Adicionalmente, hemos encontrado en nuestra base de datos un perfil que coincide 
    con el producto C-AUTO. Informacion util para evaluar:
    - Entidad: {moto_similar.get('Entidad', 'N/A')}
    - Sucursal: {moto_similar.get('Sucursal', 'N/A')}
    - Rango Edad Cliente promedio: {moto_similar.get('RangoEdad', 'N/A')}
    - Rango de dias que tarda en pagar: {moto_similar.get('BUCKET', 'N/A')}
    - Monto Comun solicitado: $ {moto_similar.get('Monto_Comun', 'N/A'):,.2f}
    - Plazo Promedio: {moto_similar.get('Plazo_Promedio_Meses', 'N/A')}
    - Estado Civil Comun: {moto_similar.get('EstCiv_Comun', 'N/A')}
    - Interes promedio en el perfil: {moto_similar.get('Interes', 'N/A')}%
    - Pago minimo realizado: $ {moto_similar.get('Pago_Minimo', 'N/A'):,.2f}
    - Pago maximo realizado: $ {moto_similar.get('Pago_Maximo', 'N/A'):,.2f}
    - Cantidad maxima de pagos hechos: {moto_similar.get('Pagos_Promedio', 'N/A')} (en 12 meses entran entre 26 y 27 pagos promedio)
    - Genero: {moto_similar.get('Genero', 'N/A')}
    - Estado Civil Comun: {moto_similar.get('EstCiv_Comun', 'N/A')}
    - Numero de Clientes que cumplen este perfil: {moto_similar.get('Numero_de_Clientes', 'N/A')} de un total de {numero}
    
    """
    elif producto == "c-especial":
        producto_info = "No se encontraron datos historicos de un C-Especial directamente comparable."
        if moto_similar:
            producto_info = f"""
    Adicionalmente, hemos encontrado en nuestra base de datos un perfil que coincide 
    con el producto C-ESPECIAL. Informacion util para evaluar:
    - Entidad: {moto_similar.get('Entidad', 'N/A')}
    - Sucursal: {moto_similar.get('Sucursal', 'N/A')}
    - Rango Edad Cliente promedio: {moto_similar.get('RangoEdad', 'N/A')}
    - Rango de dias que tarda en pagar: {moto_similar.get('BUCKET', 'N/A')}
    - Monto Comun solicitado: $ {moto_similar.get('Monto_Comun', 'N/A'):,.2f}
    - Plazo Promedio: {moto_similar.get('Plazo_Promedio_Meses', 'N/A')}
    - Estado Civil Comun: {moto_similar.get('EstCiv_Comun', 'N/A')}
    - Interes promedio en el perfil: {moto_similar.get('Interes', 'N/A')}%
    - Pago minimo realizado: $ {moto_similar.get('Pago_Minimo', 'N/A'):,.2f}
    - Pago maximo realizado: $ {moto_similar.get('Pago_Maximo', 'N/A'):,.2f}
    - Cantidad maxima de pagos hechos: {moto_similar.get('Pagos_Promedio', 'N/A')} (en 12 meses entran entre 26 y 27 pagos promedio)
    - Genero: {moto_similar.get('Genero', 'N/A')}
    - Estado Civil Comun: {moto_similar.get('EstCiv_Comun', 'N/A')}
    - Numero de Clientes que cumplen este perfil: {moto_similar.get('Numero_de_Clientes', 'N/A')} de un total de {numero}
    
    """
    
    cast_info = "No se encontraron datos historicos de un Castigado directamente comparable."
    if cast_similar:
        cast_info = f"""
    Adicionalmente, hemos encontrado en nuestra base de datos un perfil que coincide con registros 
    de caracteristicas de un cliente Castigado. Informacion util para evaluar:
    - Entidad o Municipio: {cast_similar.get('Municipio', 'N/A')}
    - Genero: {cast_similar.get('Genero', 'N/A')}
    - Edad minima del perfil castigado: {cast_similar.get('EdadMin', 'N/A')}
    - Edad maxima del perfil castigado: {cast_similar.get('EdadMax', 'N/A')}
    - Financiamiento promedio: {cast_similar.get('PromCol', 'N/A')}
    - Capital Castigado promedio: {cast_similar.get('PromCast', 'N/A')}
    - Rango de Meses de Desembolso a Ultimo Deposito: Minimo {cast_similar.get('MinMeses', 'N/A')} - Maximo {cast_similar.get('MaxMeses', 'N/A')}
    - Numero de clientes en este perfil: {cast_similar.get('#Cli', 'N/A')}
    - Porcentaje promedio de capital castigado: {cast_similar.get('%CapCastProm', 'N/A')}%
    - Porcentaje promedio de capital cumplido: {cast_similar.get('%CoberturaCap', 'N/A')}%
    
    """
    
    riesgo_info = "No se encontraron datos historicos de Riesgo directamente comparable."
    if riesgo_similar:
        riesgo_info = f"""
    Adicionalmente, hemos encontrado en nuestra base de datos un perfil que coincide con registros 
    de caracteristicas de un cliente segun el siguiente Riesgo. Informacion util para evaluar:
    - Entidad: {riesgo_similar.get('Entidad', 'N/A')}
    - Sucursal: {riesgo_similar.get('Sucursal', 'N/A')}
    - Rango Edad Cliente promedio: {riesgo_similar.get('RangoEdad', 'N/A')}
    - Rango de dias que tarda en pagar: {riesgo_similar.get('BUCKET', 'N/A')}
    - Monto Comun solicitado: $ {riesgo_similar.get('Monto_Comun', 'N/A'):,.2f}
    - Plazo Promedio: {riesgo_similar.get('Plazo_Promedio_Meses', 'N/A')}
    - Estado Civil Comun: {riesgo_similar.get('EstCiv_Comun', 'N/A')}
    - Interes promedio en el perfil: {riesgo_similar.get('Interes', 'N/A')}%
    - Pago minimo realizado: $ {riesgo_similar.get('Pago_Minimo', 'N/A'):,.2f}
    - Pago maximo realizado: $ {riesgo_similar.get('Pago_Maximo', 'N/A'):,.2f}
    - Cantidad maxima de pagos hechos: {riesgo_similar.get('Pagos_Promedio', 'N/A'):.0f} (en 12 meses entran entre 26 y 27 pagos promedio)
    - Genero: {riesgo_similar.get('Genero', 'N/A')}
    - Estado Civil Comun: {riesgo_similar.get('EstCiv_Comun', 'N/A')}
    - Numero de Clientes que cumplen este perfil: {riesgo_similar.get('Numero_de_Clientes', 'N/A')} de un total de {numero_riesgos}
    - Rango del perfil en Indice de Mora = {riesgo_similar.get('IM_min', 'N/A')} - {riesgo_similar.get('IM_max', 'N/A')} con un promedio de {riesgo_similar.get('IM_prom', 'N/A')}
    - CALIFICACION DE RIESGO: {riesgo_calif:,.2f}/10 <--- Basandose en una combinacion de datos de indice, riesgos y castigos
    
    """
    
    indice_info = "No se encontraron datos historicos de Riesgo directamente comparable."
    if indice_paz:
        indice_info = f"""
    Adicionalmente, hemos encontrado en nuestra base de datos un perfil que coincide con registros 
    de caracteristicas de un cliente segun Indice de Paz. Informacion util para evaluar:
    - Entidad: {indice_paz.get('Estado', 'N/A')}
    - Clasificacion de seguridad: TOP {indice_paz.get('Clasificacion', 'N/A')} de 32
    - Riesgo: {indice_paz.get('Riesgo', 'N/A')}
    - Calificacion Homicidios: {indice_paz.get('CalHom', 'N/A')} de 5
    - Calificacion Delitos: {indice_paz.get('CalDel', 'N/A')} de 5
    - Calificacion Violencia: {indice_paz.get('CalViol', 'N/A')} de 5
    - Calificacion Armas: {indice_paz.get('CalArm', 'N/A')} de 5
    - Calificacion Miedo: {indice_paz.get('CalMie', 'N/A')} de 5
    - Porcentaje Desapariciones no resueltas: {indice_paz.get('PorDesa', 'N/A')}% de su total de desapariciones
    - Inversion en seguridad PIB Estatal: {indice_paz.get('InvPIB', 'N/A')}%
    - Impacto economico anual por Persona: ${indice_paz.get('ImpactoAnualPersona', 'N/A')} Por Persona
    - Resilencia de Control del crimen: TOP {indice_paz.get('Resiliencia', 'N/A')} de 32
    
    """
    
    if utilizar_ia == "SI" or utilizar_ia == "si":
        
        prompt = f"""
            
# INFORMACION ADICIONAL

---
{perfil_info}
---
{producto_info}
---
{cast_info}
---
{riesgo_info}
---
{indice_info}
---

# [La INFORMACION ADICIONAL solo utilizala para lo que te sirva en utilidad de evaluar]

# ROL Y OBJETIVO
Eres un experto analista de credito senior, especializado en microcreditos para emprendedores en Mexico. Tu principal objetivo es evaluar la capacidad de pago REAL y la viabilidad del cliente en su contexto, no solo aplicar metricas bancarias tradicionales. Debes ser pragmatico y entender que un credito es una herramienta de inversion.

# CONTEXTO
Analizaras la solicitud de un microcredito. No penalices tasas de interes que puedan parecer altas si la estructura financiera del cliente y el proposito del credito demuestran viabilidad. La prioridad es determinar si el cliente puede pagar la cuota y mantener una calidad de vida digna.

# DATOS A ANALIZAR (YA PROCESADOS PARA UN MEJOR ANALISIS)

# REGLAS DE ALTA IMPORTANCIA OBLIGATORIA
Las siguientes reglas deben hacerse antes de continuar con el Formato de Salida, ya que deben regir si se hace la puntuacion o no

* **Permitir negativos:** {negativos}
* Si **Permitir negativos** Es NO y si el siguiente valor: ${ingreso_neto:.2f}, es negativo entonces poner una puntuacion de 0/10 Rechazado
* Si **Permitir negativos** Es SI y si el siguiente valor: ${ingreso_neto:.2f}, es negativo entonces continua con la evaluacion.

# REGLAS DE EVALUACIoN OBLIGATORIAS
Sigue estas reglas en orden y con total precision para determinar la calificacion.

1.  **Reglas de Calificacion (Jerarquicas):**
* **Regla de Excelencia (Calificacion 10/10):** Si el **Porcentaje de Ingreso Restante:** es superior al 50%, se muy favoroso en tu conclusion.
* **Regla Sobresaliente (Calificacion 9/10):** Si el **Porcentaje de Ingreso Restante:** esta entre el 40% y el 49.99%, se favoroso en tu conclusion.
* **Regla de Solvencia Aceptable (Calificacion 6-8/10):** Si la `liquidez_final` es mayor a $ {solvencia_monto_minimo:,.2f} MXN Y el **Porcentaje de Ingreso Restante:** es mayor al {solvencia_porcentaje_minimo}%, considera esto un resultado bueno. El cliente tiene solvencia.
* **Casos Restantes:** Si no se cumple ninguna de las reglas anteriores, evalua el riesgo de forma mas tradicional, pero siempre explicando por que el cliente no cumple con los umbrales minimos de liquidez establecidos.
* **Datos Adicionales:** Adicional a la calificacion que concluyas en base a los puntos anteriores, compara la informacion que se tiene con los perfiles que se tienen y si esto esta dentro del rango que parece bueno cuentalo como favor.

3.  **Consideraciones:**
* **Ubicacion:** toma el dato del municipio del cliente, {data.get('municipio', 'N/A')}, y toma el dato de la sucursal {data.get('sucursal', 'N/A')} y has la busqueda para determinar el tiempo de viaje estimado en automovil entre el municipio del cliente y la sucursal, expresandolo en horas y minutos, a lo cual compara el tiempo de viaje, y consideralo para tu conclusion, poniendo en idea que tan dificil seria cobrar.
* **Permiso(Marco Legal):** Si el permiso del cliente es Si manten una postura positiva, si el permiso del cliente esta en Tramite tu postura debe ser observante, y si es No manten una postura Critica y basate en los datos adicionales de la moto otorgados para tu evaluacion.

4.  **Lectura:**
* **Brackets:** al leer considera leer lo que este dentro de los agrupadores '[]' como informacion para evaluar pero no entregues ese texto en la Salida.

Evalua el siguiente perfil de cliente para un credito o financiamiento. Tu objetivo es dar un analisis cualitativo y detallado, no una calificacion numerica. Analiza el perfil y determina si el cliente es apto o si existen riesgos importantes. Tomando en cosideracion la informacion que tengas sobre la ubicacion o domicilio del cliente.

# DATOS A EVALUAR
Proporciona tu respuesta como una CONCLUSION EVALUATORIA que sirva como referencia para que el comite de aprobacion de creditos tenga una mejor perspectiva con tu conclusion como segunda mente que piensa.
 
# FORMATO DE SALIDA asi tal cual como se muestra la informacion debe mantenerse a la hora de entregar la respuesta, solo donde se especifica tu evaluacion como IA vas a escribir.

 ## CALIFICACION OTORGADA: {score_final:.2f}/10 lo cual otorga un estado de {texto_calif}
 ## RIESGO CALCULADO:      {riesgo_calif}/10 lo cual otorga un riesgo {texto_riesgo}
 
 ## Datos del cliente que ayudan a evaluar
 - Cliente: {data.get('nombre', 'N/A')}
 - Edad: {data.get('edad', 'N/A')}
 - Genero: {data.get('genero', 'N/A')}
 - Estado Civil: {data.get('estado_civil', 'N/A')}
 - Pais: Mexico
 - Estado: {data.get('estado', 'N/A')}
 - Sucursal: {data.get('sucursal', 'N/A')}
 - Munipio: {data.get('municipio', 'N/A')}
 - Reporte de Circulo de Credito: {data.get('reporte_credito', 'N/A')}
 - Permiso (Segun el marco legal): {data.get('permiso', 'N/A')}
 - Aval: {data.get('aval', 'N/A')}
 - Reporte Credito Aval: {data.get('reporte_credito_aval', 'N/A')}
 - Relacion del Aval: {data.get('relacion_aval', 'N/A')}
 - Garantia: {data.get('garantia', 'N/A')}
 - Otros datos relevantes (discapacidad, estudios, giro economico, etc.): {data.get('otros_datos', 'Sin informacion adicional')}

 ## Resumen Financiero del Cliente
 
 - **Producto:** {data.get('producto', 'N/A')}
 - **Monto Solicitado:** ${monto:,.2f} a un interes del {data.get('tasa', 'N/A')}%
 - **Plazo:** {plazo} meses
 - **Pago Mensual Estimado:** ${pago:,.2f}
 - **Total a pagar:** $ {total_pagos:,.2f}
 
 ## Capacidad de Pago
 
 - **Ingresos Totales:** $ {ingresos:,.2f}
 - **Egresos Totales:** $ {egresos:,.2f}
 - **Ingreso Neto (Antes del crédito):** ${ingreso_limpio:,.2f}
 - **Sobrante Estimado (Después del pago):** ${ingreso_neto:,.2f}
 - **Porcentaje de Ingreso Restante:** {ingreso_por:.2f}%
 - **Ingresos Extra:** {data.get('ingresos_extra', 'N/A')}
 - **Ingresos Total:** $ {ingresos_total:,.2f}
 
## Analisis de Riesgo

 - **Indice de Paz Estado:** {indice_paz.get('Clasificacion', 0)} Donde: 1 Es muy Seguro y 32 es muy Inseguro
 - **Porcentaje de Desapariciones:** {indice_paz.get('PorDesa', 0)}% de desapariciones no resueltas
 - **Inversion en seguridad:** {indice_paz.get('InvPIB', 0)}% del PIB estatal en materia de seguridad
 - **Impacto Economico Anual:** ${indice_paz.get('ImpactoAnualPersona', 0)} 
 - **Resiliencia:** {indice_paz.get('Resiliencia', 0)} de un Rango 1 al 32 (1 es donde mas Control de Riesgos y Crimen se tiene y 32 donde menos)
 - **Calificacion de Riesgo:** {CalRiesgo:,.2f}/10 <--- Basandose en las Calificaciones de homicidos, delitos, violencia, armas y miedo. 1 Poco riesgo y 10 Mucho riesgo
 
 
 ## Posibilidad de Liquidación Anticipada
 
 - **Meses para liquidar el {porcentaje_liquidacion*100}%:** {liqui_meses} meses
 - **Monto estimado a liquidar:** Liquida con $ {liqui_monto:,.2f} Habiendo cubierto: $ {suma_interes:,.2f} de Intereses y $ {suma_abono:,.2f} de Capital

## CONCLUSION EVALUATORIA IA
[Escribe tu CONCLUSION EVALUATORIA aqui. No mas de 100 palabras.]
[Escribe una segunda conclusion evaluatoria mas favoreciente, buscando informacion en el internet sobre financiamientos similares a este tipo de peronas, que puedan ayudarle al cliente viendo el caso como si quisieramos apoyarlo, manteniendo nuestro objetivo de tener un cliente que nos pague. Tal que si hay algun dato que mejorar como bajar el financiamiento propon uno. No mas de 200 palabras.]
[Aqui escribe segun tu evaluacion de todos los datos e intrucciones datas, una calificacion del 1 al 10, en formato: 'CALIFICACION EVALUATORIA IA: X/10']
"""
        return prompt
        
    elif utilizar_ia == "NO" or utilizar_ia == "no":
        
        reporte_manual = f"""
     # ANÁLISIS MANUAL (IA DESACTIVADA)
     
     ## CALIFICACION OTORGADA: {score_final:.2f}/10 lo cual otorga un estado de {texto_calif}
     ## RIESGO CALCULADO:      {riesgo_calif}/10 lo cual otorga un riesgo {texto_riesgo}
     
     ## Resumen Financiero del Cliente
     
     - **Nombre:** {data.get('nombre', 'N/A')}
     - **Monto Solicitado:** ${monto:,.2f} a un interes del {data.get('tasa', 'N/A')}%
     - **Plazo:** {plazo} meses
     - **Pago Mensual Estimado:** ${pago:,.2f}
     - **Total a pagar:** $ {total_pagos:,.2f}
     
     ## Capacidad de Pago
     
     - **Ingresos Totales:** ${ingresos:,.2f}
     - **Egresos Totales:** ${egresos:,.2f}
     - **Ingreso Neto (Antes del crédito):** ${ingreso_limpio:,.2f}
     - **Sobrante Estimado (Después del pago):** ${ingreso_neto:,.2f}
     - **Porcentaje de Ingreso Restante:** {ingreso_por:.2f}%
     
    ## Analisis de Riesgo
    
     - **Indice de Paz Estado:** {indice_paz.get('Clasificacion', 0)} Donde: 1 Es muy Seguro y 32 es muy Inseguro
     - **Porcentaje de Desapariciones:** {indice_paz.get('PorDesa', 0)}% de desapariciones no resueltas
     - **Inversion en seguridad:** {indice_paz.get('InvPIB', 0)}% del PIB estatal en materia de seguridad
     - **Impacto Economico Anual:** ${indice_paz.get('ImpactoAnualPersona', 0)} 
     - **Resiliencia:** {indice_paz.get('Resiliencia', 0)} de un Rango 1 al 32 
                        (1 es donde mas Control de Riesgos y Crimen se tiene y 32 donde menos)
     - **Calificacion de Riesgo:** {CalRiesgo:,.2f}/10 <--- Basandose en las Calificaciones de 
                                                    homicidos, delitos, violencia, armas y miedo.
                                                    1 Poco riesgo y 10 Mucho riesgo
     
     
     ## Posibilidad de Liquidación Anticipada
     
     - **Meses para liquidar el {porcentaje_liquidacion*100}%:** {liqui_meses} meses
     - **Monto estimado a liquidar:** Liquida con $ {liqui_monto:,.2f}
                                      Habiendo cubierto:
                                          $ {suma_interes:,.2f} de Intereses
                                          $ {suma_abono:,.2f} de Capital
                                             
        ---
        {perfil_info}
        ---
        {producto_info}
        ---
        {cast_info}
        ---
        {riesgo_info}
        ---
        {indice_info}
        ---
        
    **NOTA:** Este es un resumen automático basado en los datos proporcionados. La IA está desactivada.
        """
        return reporte_manual
        
    
