
-----

### **R1 (Router Principal - MikroTik)**

Los comandos están adaptados para que las VLANs y las conexiones coincidan con el diagrama: `ether3` para el switch principal, `ether2` para R2, y `ether1` para la nube de internet.

```batch
# Crear VLAN Gestión en ether3
/interface vlan
add name=VLAN_GESTION vlan-id=199 interface=ether3

# Crear VLAN P2P en ether2
add name=VLAN_P2P vlan-id=999 interface=ether2

# Direcciones IP
/ip address
add address=10.10.9.59/29 interface=VLAN_GESTION
add address=10.10.9.65/30 interface=VLAN_P2P

# NAT para salida a Internet
/ip firewall nat
add chain=srcnat out-interface=ether1 action=masquerade

# Ruta estática hacia la red remota (10.10.9.72/29) a través de R2
/ip route
add dst-address=10.10.9.72/29 gateway=10.10.9.66
```

-----

### **R2 (Router Remoto - MikroTik)**

Aquí, la conexión al switch remoto es a través de `ether2` y la conexión P2P con R1 es a través de `ether1`.

```batch
# Crear VLAN de Gestión Remota en ether2
/interface vlan
add name=VLAN_GESTION_REMOTA vlan-id=199 interface=ether2

# Crear VLAN P2P en ether1
add name=VLAN_P2P vlan-id=999 interface=ether1

# Direcciones IP
/ip address
add address=10.10.9.66/30 interface=VLAN_P2P
add address=10.10.9.73/29 interface=VLAN_GESTION_REMOTA

# NAT para salida a Internet desde la red remota
/ip firewall nat
add chain=srcnat out-interface=VLAN_P2P action=masquerade
```

-----

### **SW1 (Switch Principal - Cisco/IOS)**

El script está actualizado para reflejar los puertos del diagrama:

  * `e0/0` para R1 (troncal)
  * `e0/1` para PC Sysadmin (acceso)
  * `e0/2`, `e0/3`, `e1/0` para otros dispositivos (acceso)


```batch
conf t
!
hostname SwitchLOCAL
!
vlan 199
name VLAN_GESTION
exit
!
interface vlan 199
ip address 10.10.9.60 255.255.255.248
no shutdown
exit
!
ip default-gateway 10.10.9.59
!
username admin privilege 15 secret Admin123
!
line vty 0 4
transport input ssh
login local
exit
!
ip domain-name redes.local
!
crypto key generate rsa modulus 1024
ip ssh version 2
!
interface ethernet0/0
switchport trunk encapsulation dot1q
switchport mode trunk
switchport trunk allowed vlan 199
exit
!
interface ethernet0/1
switchport mode access
switchport access vlan 199
exit
!
interface ethernet0/2
switchport mode access
switchport access vlan 199
exit
!
interface ethernet0/3
switchport mode access
switchport access vlan 199
exit
!
interface ethernet1/0
switchport mode access
switchport access vlan 199
exit
!
interface ethernet1/1
switchport mode access
switchport access vlan 199
exit
!
do wr
```

-----

### **SW2 (Switch Remoto - Cisco/IOS)**

Este script se actualiza para los puertos del diagrama:

  * `e0/0` para R2 (troncal)
  * `e0/1` para el usuario remoto (acceso)


```batch
conf t
!
hostname SwitchREMOTO
!
vlan 199
name VLAN_GESTION
exit
!
interface vlan 199
ip address 10.10.9.61 255.255.255.248
no shutdown
exit
!
ip default-gateway 10.10.9.60
!
username admin privilege 15 secret Admin123
!
line vty 0 4
transport input ssh
login local
exit
!
ip domain-name redes.local
!
crypto key generate rsa modulus 1024
ip ssh version 2
!
interface Ethernet0/0
switchport trunk encapsulation dot1q
switchport mode trunk
switchport trunk allowed vlan 199
no shutdown
exit
!
interface Ethernet0/1
switchport mode access
switchport access vlan 199
no shutdown
exit
!
exit
!
do wr
```


### **Linux (Servidor - Debian 12)**

```batch
  sudo ip addr add 10.10.9.57/29 dev enp0s3
  sudo ip link set enp0s3 up
  sudo ip route add default via 10.10.9.59

```