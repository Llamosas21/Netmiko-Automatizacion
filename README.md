## Descripción
Este repositorio contiene un script Python diseñado para automatizar la configuración de una infraestructura de red corporativa. El script gestiona switches Cisco y routers MikroTik, permitiendo la creación de VLANs, enlaces punto a punto y la configuración de NAT para acceso a Internet.

## Funcionalidades
- Configuración remota de dispositivos de red vía SSH.
- Definición de VLANs de gestión y enlaces P2P.
- Asignación de direcciones IP y gateways.
- Implementación de reglas de NAT y rutas estáticas.
- Pruebas de conectividad y comandos de verificación.
- Seguridad reforzada con usuarios y privilegios.

## Instrucciones de Uso
1. Prepara la PC SYSADMIN con la IP y gateway indicados.
2. Instala Python y Netmiko según la guía incluida.
3. Ejecuta el script para aplicar la configuración en todos los equipos.

## Resultado Esperado
- Red configurada automáticamente y lista para operar.
- Conectividad entre sedes y acceso seguro a Internet.

## Requisitos
- Python 3
- Netmiko
- Acceso SSH a los dispositivos
