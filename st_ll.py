
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
# Ejecución
# ==================
if __name__ == "__main__":
    sw1_local()
    sw2_remoto()
    r1_local()
    r2_remoto()