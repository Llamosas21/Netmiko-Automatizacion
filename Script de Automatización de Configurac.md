# Script de Automatización de Configuración de Red -- Santiago Llamosas

## Descripción
Script Python que automatiza la configuración de dispositivos de red (switches Cisco y routers MikroTik) para implementar una red corporativa multi-sede con VLANs de gestión, enlaces P2P y conectividad a Internet.
Este documento explica cómo establecer la configuración básica de la PC SYSADMIN para poder conectarse a los dispositivos de red mediante SSH. Incluye la asignación de dirección IP en la VLAN de gestión, la instalación de Python y Netmiko, y los pasos para ejecutar los scripts de automatización.

## 1. Verificar interfaz de red activa
Usá este comando para ver qué interfaz tenés disponible:
```bash
ip a
```
Ignorá la interfaz `lo`. La que identifiques será la que uses para configurar tu IP.

## 2. Asignar IP estática y ruta por defecto
Ejecutar los siguientes comandos (reemplazá `enp0s3` si tu interfaz tiene otro nombre):
```bash
sudo ip addr add 10.10.9.57/29 dev enp0s3
sudo ip link set enp0s3 up
sudo ip route add default via 10.10.9.59
```
- `10.10.9.57/29` → IP de tu PC SYSADMIN
- `10.10.9.59` → IP del MikroTik que actúa como gateway

## 3. Verificar conectividad
Probar comunicación con la puerta de enlace, una IP pública y un dominio:
```bash
ping 10.10.17.59     # MikroTik
ping 8.8.8.8         # IP pública (Google)
```
 

## 4. Instalar Python y pip
Actualizar repositorios e instalar:
```bash
sudo apt update
sudo apt install python3 python3-pip
```
Verificar versiones:
```bash
python3 --version
pip3 --version
``` 

## 5. Ejecutar el script
Ejecutar el archivo Python:
```bash
python3 Script.py
```

### Script Completo
```python
from netmiko import ConnectHandler

# ==================
# Dispositivos
# ==================
devices = {
    'SW1-LOCAL':{
        'device_type': 'cisco_ios',
        'host': '10.10.17.58',  # IP de gestión del SW1
        'username': 'admin',
        'password': 'admin',
        'secret': 'admin'
    },
    'SW2-REMOTO':{
        'device_type': 'cisco_ios',
        'host': '10.10.17.61',  # IP de gestión del SW2
        'username': 'admin',
        'password': 'admin',
        'secret': 'admin'
    },
    'R1-LOCAL':{
        'device_type': 'mikrotik_routeros',
        'host': '10.10.17.59',  # IP de gestión del R1
        'username': 'admin',
        'password': 'admin',
        'port': 22
    },
    'R2-REMOTO':{
        'device_type': 'mikrotik_routeros',
        'host': '10.10.17.60',  # IP de gestión del R2
        'username': 'admin',
        'password': 'admin',
        'port': 22
    }
}

# ==================
# Configuración R1 (MikroTik)
# ==================
def r1_local():
    """
    Configura el router R1-LOCAL (MikroTik) con:
    - VLAN de gestión (199) en ether3
    - VLAN P2P (999) en ether2  
    - Direccionamiento IP
    - NAT para Internet
    - Ruta estática hacia red remota
    """
    r1 = ConnectHandler(**devices['R1-LOCAL'])
    commands = [
        "/interface vlan add name=VLAN_GESTION vlan-id=199 interface=ether3",
        "/interface vlan add name=VLAN_P2P vlan-id=999 interface=ether2",
        "/ip address add address=10.10.9.59/29 interface=VLAN_GESTION",
        "/ip address add address=10.10.9.65/30 interface=VLAN_P2P",
        "/ip firewall nat add chain=srcnat out-interface=ether1 action=masquerade",
        "/ip route add dst-address=10.10.9.72/29 gateway=10.10.9.66"
    ]
    output = r1.send_config_set(commands)
    print(output)
    r1.disconnect()

# ==================
# Configuración R2 (MikroTik)
# ==================
def r2_remoto():
    """
    Configura el router R2-REMOTO (MikroTik) con:
    - VLAN de gestión remota (199) en ether2
    - VLAN P2P (999) en ether1
    - Direccionamiento IP
    - NAT para Internet
    """
    r2 = ConnectHandler(**devices['R2-REMOTO'])
    commands = [
        "/interface vlan add name=VLAN_GESTION_REMOTA vlan-id=199 interface=ether2",
        "/interface vlan add name=VLAN_P2P vlan-id=999 interface=ether1",
        "/ip address add address=10.10.9.66/30 interface=VLAN_P2P",
        "/ip address add address=10.10.9.73/29 interface=VLAN_GESTION_REMOTA",
        "/ip firewall nat add chain=srcnat out-interface=VLAN_P2P action=masquerade"
    ]
    output = r2.send_config_set(commands)
    print(output)
    r2.disconnect()

# ==================
# Configuración SW1 (Cisco)
# ==================
def sw1_local():
    """
    Configura el switch SW1-LOCAL (Cisco) con:
    - Hostname y VLAN de gestión
    - Interface VLAN con IP
    - Gateway por defecto
    - Usuario administrativo y SSH
    - Puertos trunk y access
    """
    sw1 = ConnectHandler(**devices['SW1-LOCAL'])
    sw1.enable()
    commands = [
        "hostname SwitchLOCAL",
        "vlan 199",
        " name VLAN_GESTION",
        "exit",
        "interface vlan 199",
        " ip address 10.10.9.60 255.255.255.248",
        " no shutdown",
        "exit",
        "ip default-gateway 10.10.9.59",
        "username admin privilege 15 secret Admin123",
        "line vty 0 4",
        " transport input ssh",
        " login local",
        "exit",
        "ip domain-name redes.local",
        "crypto key generate rsa modulus 1024",
        "ip ssh version 2",
        # Trunk hacia R1
        "interface ethernet0/0",
        " switchport trunk encapsulation dot1q",
        " switchport mode trunk",
        " switchport trunk allowed vlan 199",
        "exit",
        # Access ports
        "interface ethernet0/1",
        " switchport mode access",
        " switchport access vlan 199",
        "exit",
        "interface ethernet0/2",
        " switchport mode access",
        " switchport access vlan 199",
        "exit",
        "interface ethernet0/3",
        " switchport mode access",
        " switchport access vlan 199",
        "exit",
        "interface ethernet1/0",
        " switchport mode access",
        " switchport access vlan 199",
        "exit",
        "interface ethernet1/1",
        " switchport mode access",
        " switchport access vlan 199",
        "exit",
        "do wr"
    ]
    output = sw1.send_config_set(commands)
    print(output)
    sw1.disconnect()

# ==================
# Configuración SW2 (Cisco)
# ==================
def sw2_remoto():
    """
    Configura el switch SW2-REMOTO (Cisco) con:
    - Hostname y VLAN de gestión
    - Interface VLAN con IP
    - Gateway por defecto
    - Usuario administrativo y SSH
    - Puertos trunk y access
    """
    sw2 = ConnectHandler(**devices['SW2-REMOTO'])
    sw2.enable()
    commands = [
        "hostname SwitchREMOTO",
        "vlan 199",
        " name VLAN_GESTION",
        "exit",
        "interface vlan 199",
        " ip address 10.10.9.61 255.255.255.248",
        " no shutdown",
        "exit",
        "ip default-gateway 10.10.9.60",
        "username admin privilege 15 secret Admin123",
        "line vty 0 4",
        " transport input ssh",
        " login local",
        "exit",
        "ip domain-name redes.local",
        "crypto key generate rsa modulus 1024",
        "ip ssh version 2",
        # Trunk hacia R2
        "interface ethernet0/0",
        " switchport trunk encapsulation dot1q",
        " switchport mode trunk",
        " switchport trunk allowed vlan 199",
        " no shutdown",
        "exit",
        # Access port
        "interface ethernet0/1",
        " switchport mode access",
        " switchport access vlan 199",
        " no shutdown",
        "exit",
        "do wr"
    ]
    output = sw2.send_config_set(commands)
    print(output)
    sw2.disconnect()

# ==================
# Ejecución Principal
# ==================
if __name__ == "__main__":
    """
    Orden de ejecución:
    1. Configurar switches primero
    2. Configurar routers después
    """
    print("Iniciando configuración automática de red...")
    
    print("\nConfigurando SW1-LOCAL...")
    sw1_local()
    
    print("\nConfigurando SW2-REMOTO...")
    sw2_remoto()
    
    print("\nConfigurando R1-LOCAL...")
    r1_local()
    
    print("\nConfigurando R2-REMOTO...")
    r2_remoto()
    
    print("\n Configuración completada para todos los dispositivos!")
```

## ¿Cómo ejecutar?
1. Guarda el script como `network_automation.py`
2. Asegúrate de tener conectividad a las IPs de gestión
3. Ejecuta: `python network_automation.py`

## Resultado Esperado
El script configurará automáticamente:
- ✅ 2 switches Cisco con VLAN de gestión
- ✅ 2 routers MikroTik con enlace P2P
- ✅ Conectividad entre sedes
- ✅ Acceso a Internet
- ✅ Seguridad SSH habilitada

**Nota**: Asegúrate de que los puertos, credenciales y IPs coincidan con tu entorno real antes de ejecutar.

---