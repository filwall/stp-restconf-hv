import requests
import urllib3
import re 
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def starta_interface():
    for i in range(1, 4):
        for interface in range(1, 5):
            r = requests.patch(
                f"https://10.0.0.{i}/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1%2F0%2F{interface}/config",
                json={"openconfig-interfaces:config": {"enabled": True}},
                headers={"Content-Type": "application/yang-data+json"},
                auth=("admin", "admin"),
                verify=False,
                timeout=5
            )
            print(f"10.0.0.{i} G1/0/{interface}: {r.status_code}")

def hastighet():
  for i in range(1, 4):
    for j in range(3, 5):
      url = f"https://10.0.0.{i}/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1%2F0%2F{j}/openconfig-if-ethernet:ethernet/config"

      payload = {
          "openconfig-if-ethernet:config": {
              "auto-negotiate": False,
              "port-speed": "openconfig-if-ethernet:SPEED_100MB",
              "enable-flow-control": True,
          }
      }

      headers = {
          "Content-Type": "application/yang-data+json",
          "Accept": "application/yang-data+json",
      }

      try:
        r = requests.put(
            url,
            json=payload,
            headers=headers,
            auth=("admin", "admin"),
            verify=False,
            timeout=5,
        )
        
        #print(r.status_code)
      except Exception:
        raise ValueError(f"S{i} misslyckades")

def hämta_mac():
    mac_addr = []
    for i in range(1,4):
        ip = f'10.0.0.{i}'
        url = f"https://{ip}/restconf/data/Cisco-IOS-XE-spanning-tree-oper:stp-details?fields=stp-detail/bridge-address"

        headers = {
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }

        r = requests.get(
            url,
            headers=headers,
            auth=("admin", "admin"),
            verify=False
        )
        
        try:
            data = r.json()
            mac = data['Cisco-IOS-XE-spanning-tree-oper:stp-details']['stp-detail'][0]['bridge-address']
            mac_addr.append(mac)
            #print(f'S{i} {mac}')
            högst = max(mac_addr)
            if högst == mac:
                svar = ip
        except:
            pass  
    return svar
    


def trunk_router(ip): 

    url = f"https://{ip}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F5"

    payload = {
        "Cisco-IOS-XE-native:GigabitEthernet": {
            "name": "1/0/5",
            "switchport": {
                "Cisco-IOS-XE-switch:mode": {
                    "trunk": {}
                },
                "Cisco-IOS-XE-switch:trunk": {
                    "allowed": {
                        "vlan": {
                            "vlans": "10,20,30,99"
                        }
                    }
                }
            }
        }
    }

    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }


    try:
        r = requests.put(
            url,
            json=payload,
            headers=headers,
            auth=("admin", "admin"),
            verify=False,
            timeout=5
        )
        print(r.text)
        if r.status_code not in [200, 201, 204]:
            print('skiten fungerar inte')
            
    except requests.exceptions.RequestException as e:
        print(f"Kunde inte nå {ip}: {e}")


def sätt_native():
    for i in range(1, 4):
        ip = f'10.0.0.{i}'
        for interface in range(1, 6):
            url = f"https://{ip}/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1%2F0%2F{interface}/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan"

            payload = {
                "openconfig-vlan:switched-vlan": {
                    "config": {
                        "interface-mode": "TRUNK",
                        "native-vlan": 99
                    }
                }
            }

            headers = {
                "Content-Type": "application/yang-data+json",
                "Accept": "application/yang-data+json"
            }

            try:
                r = requests.patch(
                    url,
                    json=payload,
                    headers=headers,
                    auth=("admin", "admin"),
                    verify=False,
                    timeout=5
                )
            except requests.exceptions.RequestException as e:
                print(f"Kunde inte nå {ip}: {e}")



def skapa_vlan(): 
    import random
    lista = ['ARTIO', 'CALLISTO', 'DAGGONATH_KINGS', 'ZULRAH', 'BARROWS_BROTHERS', 'ROBERTS_ROLIGA_REGENTER', 'SIMONS_SKONA_SNUBBAR', 'HANIS_HARLIGA_HERRAR', 'JOHANS_JORDNARA_JATTAR', 'KIMS_KOOLA_KILLAR', 'PATRIKS_PARTY_PINGLOR', 'WOW_JOCKE', 'LARS_OLOF_', 'RONNY_RAGGE', 'Annie', 'Alistar', 'Anivia', 'Xiao_Xiaos_Xona_Xnubbar']
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }

    for i in range(1, 4):
        ip = f'10.0.0.{i}'
        print(f"Ansluter till enhet: {ip}")
        for interface in [10,20,30,99]:
            url = f"https://{ip}/restconf/data/openconfig-vlan:vlans/vlan={interface}"
            
            #namn = f'vlan_{interface}'
            namn = f'{lista[random.randint(0, len(lista)-1)]}_{interface}'
            print(namn)
            
            payload = {
              "openconfig-vlan:vlan": {
                "vlan-id": interface,
                "config": {
                  "vlan-id": interface,
                  "name": namn
                }
              }
            }

            try:
                r = requests.put(
                    url,
                    json=payload,
                    headers=headers,
                    auth=("admin", "admin"),
                    verify=False,
                    timeout=5
                )
                
                if r.status_code not in [200, 201, 204]:
                    print('skiten fungerar inte')
                
                #if r.status_code in [200, 201, 204]:
                    #print(f"VLAN {interface} skapades på {ip}")
                #else:
                    #print(f"Kunde inte skapa VLAN {interface} på {ip}. Statuskod: {r.status_code}, Svar: {r.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Kunde inte nå {ip}: {e}")
                

def kör_vtp():
    for i in range(1, 4):
        url = f"https://10.0.0.{i}/restconf/data/Cisco-IOS-XE-native:native/vtp"

        payload = {
            "Cisco-IOS-XE-native:vtp": {
                "Cisco-IOS-XE-vtp:domain": "Gabbes_gubbar",
                "Cisco-IOS-XE-vtp:mode": {
                    "transparent": {}
                }
            }
        }

        headers = {
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json",
        }

        try:
            r = requests.patch(
                url,
                json=payload,
                headers=headers,
                auth=("admin", "admin"),
                verify=False,
                timeout=5,
            )

            if r.status_code not in [200, 201, 204]:
                print(f"S{i}: {r.text}")

        except Exception:
            raise ValueError(f"S{i} misslyckades")

def sätt_stp_prio(ip):
    for i in [1,10,20,30,99]:
        url = f"https://{ip}/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={i}/config"

        payload = {
            "openconfig-spanning-tree:config": {
                "bridge-priority": 4096
            }
        }

        headers = {
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }
            
        r = requests.patch(
            url,
            json=payload,
            headers=headers,
            auth=("admin", "admin"),
            verify=False,
            timeout=5,
        )

        if r.status_code not in [200, 201, 204]:
            r = requests.post(
                f"https://{ip}/restconf/data/openconfig-spanning-tree:stp/rapid-pvst",
                json={
                    "openconfig-spanning-tree:vlan": [{
                        "vlan-id": i,
                        "config": {"vlan-id": i, "bridge-priority": 4096}
                    }]
                },
                headers=headers,
                auth=("admin", "admin"),
                verify=False,
                timeout=5,
            )

        if r.status_code not in [200, 201, 204]:
            r = requests.patch(
                f"https://{ip}/restconf/data/Cisco-IOS-XE-native:native/spanning-tree",
                json={
                    "Cisco-IOS-XE-native:spanning-tree": {
                        "Cisco-IOS-XE-spanning-tree:vlan": [{"id": i, "priority": 4096}]
                    }
                },
                headers=headers,
                auth=("admin", "admin"),
                verify=False,
                timeout=5,
            )
    print(f'{ip} är root bridge')

def skapa_access():
    lista = [10,20,30]
    räknare = 0
    for i in range(1, 4):
        ip = f'10.0.0.{i}'
        for j in range(22, 25):
            url = f"https://{ip}/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1%2F0%2F{j}/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan"
            
            payload = {
                "openconfig-vlan:switched-vlan": {
                    "config": {
                        "interface-mode": "ACCESS",
                        "access-vlan": lista[räknare]
                    }
                }
            }
            räknare += 1
            if räknare == 3:
                räknare = 0
            headers = {
                "Content-Type": "application/yang-data+json",
                "Accept": "application/yang-data+json"
            }

            try:
                r = requests.patch(
                    url,
                    json=payload,
                    headers=headers,
                    auth=("admin", "admin"),
                    verify=False,
                    timeout=5
                )
                if r.status_code not in [200, 201, 204]:
                    print('skiten fungerar inte')
                    
            except requests.exceptions.RequestException as e:
                print(f"Kunde inte nå {ip}: {e}")
    if r.status_code in [200, 201, 204]:
        print('Accessportar skapades')

                



def router_vlan():
    for i in [10, 20, 30, 99]:
        url = f"https://10.0.0.4/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet0%2F0%2F0/subinterfaces/subinterface={i}"

        payload = {
            "openconfig-interfaces:subinterface": {
                "index": i,
                "config": {
                    "index": i,
                    "description": f"VLAN {i}",
                    "enabled": True
                },
                "openconfig-if-ip:ipv4": {
                    "addresses": {
                        "address": [
                            {
                                "ip": f"192.168.{i}.1",
                                "config": {
                                    "ip": f"192.168.{i}.1",
                                    "prefix-length": 24
                                }
                            }
                        ]
                    }
                },
                "openconfig-if-ip:ipv6": {
                    "config": {
                        "enabled": False
                    }
                }
            }
        }

        headers = {
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }

        try:
            r = requests.put(
                url,
                json=payload,
                headers=headers,
                auth=("admin", "admin"),
                verify=False,
                timeout=5
            )
            if r.status_code not in [200, 201, 204]:
                print('skiten fungerar inte')
                print(r.text)

        except Exception:
            print('error')
    if r.status_code in [200, 201, 204]:
        print('Vlan skapade på Router')


def router_starta_int():
    url = f"https://10.0.0.4/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet0%2F0%2F0/config"

    payload = {
        "openconfig-interfaces:config": {
            "enabled": True
        }
    }

    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }

    try:
        r = requests.patch(
            url,
            json=payload,
            headers=headers,
            auth=("admin", "admin"),
            verify=False,
            timeout=5
        )
        print(r.text)
        if r.status_code not in [200, 201, 204]:
            print('skiten fungerar inte')
            print(r.text)

    except requests.exceptions.RequestException as e:
        print(f"Kunde inte nå {ip}: {e}")

        headers = {
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }

        try:
            r = requests.put(
                url,
                json=payload,
                headers=headers,
                auth=("admin", "admin"),
                verify=False,
                timeout=5
            )
            if r.status_code not in [200, 201, 204]:
                print('skiten fungerar inte')
                print(r.text)



        except requests.exceptions.RequestException as e:
            print(f"Kunde inte nå {ip}: {e}")

    if r.status_code in [200, 201, 204]:
        print('g0/0/0 startades')
        
      




def grundconf():
    import time, serial
    
    for i in range(1, 5):
        if i < 4:
            x,z = 'S', 'g0/0'
        else:
            x,z = 'R', 'g0'

        input(f"Koppla in switch {i} och tryck enter")
        #ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
        ser = serial.Serial("COM1", 9600, timeout=1)
        for rad in ["", "en", "conf t", "no ip domain lookup", f"hostname {x}{i}", "ip domain name vetej",
                    "username admin priv 15 sec admin", "aaa new-model",
                    "aaa authentication login default local", "aaa authorization exec default local",
                    "ip http secure-server", "restconf", f"int {z}",
                    f"ip add 10.0.0.{i} 255.255.255.0", "no shut", "end"]:
            ser.write((rad + "\r").encode())
            time.sleep(0.3)
            print(ser.read(ser.in_waiting).decode(errors="ignore"))
        ser.close()
        print(f"{x} {i} klar")


def reload():
    import time, serial
    
    for i in range(1, 5):
        #ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
        ser = serial.Serial("COM1", 9600, timeout=1)
        for rad in ["", "en", "delete vlan.dat", "reload", "no", ""]:
            ser.write((rad + "\r").encode())
            time.sleep(0.3)
            print(ser.read(ser.in_waiting).decode(errors="ignore"))
        ser.close()
#grundconf()

####CONFA####
starta_interface()
hastighet()
trunk_router(hämta_mac())
sätt_native()
skapa_vlan()
sätt_stp_prio(hämta_mac()) 
kör_vtp()
skapa_access()
router_vlan()
router_starta_int()
router_vlan()




#

#print(r.text)
#print(f"{ip} {v.split(':')[-1]}")


