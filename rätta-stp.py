import requests 
import urllib3
import re 
import json
        
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    

def get_native():
    alla_är_trunk = True
    
    for i in range(1, 4):
        ip = f'10.0.0.{i}'
        for interface in range(1, 5):
            url = f"https://{ip}/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1%2F0%2F{interface}"

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
            match = re.search(r'"native-vlan"\s*:\s*(\d+)', r.text)
            #\s* kan finnas ett eller flera mellanslag. (\d+) efter : kommer en eller flera siffror
            
            if match:
                native_vlan = match.group(1) # 0 är  "native-vlan": 99 och 1 är 99
            else:
                native_vlan = "Okänt"
                
            
            if 'TRUNK' in r.text:
                print(f"{ip} G1/0/{interface} är en trunk och native vlan: {native_vlan}")
            else:
                print(f"{ip} G1/0/{interface} är INTE en trunk och native vlan: {native_vlan}")
                alla_är_trunk = False
            
    
    return alla_är_trunk

def hämta_hastighet():
  for i in range(1, 4):
    rätt = True
    for j in range(1, 5):
      url = f"https://10.0.0.{i}/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1%2F0%2F{j}/openconfig-if-ethernet:ethernet/state"

      headers = {
          "Accept": "application/yang-data+json",
      }

      try:
        r = requests.get(
            url,
            headers=headers,
            auth=("admin", "admin"),
            verify=False,
            timeout=5,
        )

        hastighet = r.json()["openconfig-if-ethernet:state"]["port-speed"]
      except Exception:
        raise ValueError(f"S{i} misslyckades")

      if j <= 2 and "SPEED_1GB" not in hastighet:
        ok = False
      if j >= 3 and "SPEED_100MB" not in hastighet:
        rätt = False

    return rätt



def hämta_vtp():
    rätt = True
    for i in range(1, 4):
        url = f"https://10.0.0.{i}/restconf/data/Cisco-IOS-XE-native:native/vtp"

        headers = {
            "Accept": "application/yang-data+json",
        }

        try:
            r = requests.get(
                url,
                headers=headers,
                auth=("admin", "admin"),
                verify=False,
                timeout=5,
            )

            vtp = r.json()["Cisco-IOS-XE-native:vtp"]
        except Exception:
            raise ValueError(f"S{i} misslyckades")

        domain = vtp.get("Cisco-IOS-XE-vtp:domain")
        mode = vtp.get("Cisco-IOS-XE-vtp:mode", {})

        if not (domain == "Gabbes_gubbar" and "transparent" in mode):
            rätt = False
    return rätt

def get_stp():      
    stp = True      
    for i in range(1,4):
            
        ip = f'10.0.0.{i}'
        url = f"https://{ip}/restconf/data/openconfig-spanning-tree:stp/global/state"
        
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
            
            
        if 'RAPID_PVST' not in r.text:
            stp = False
    if stp:
        return True



def hämta_vlan():
    headers = {
        "Accept": "application/yang-data+json"
    }

    for i in range(1, 4):
        ip = f'10.0.0.{i}'
        rätt = True
        for interface in [10, 20, 30, 99]:
            url = f"https://{ip}/restconf/data/openconfig-vlan:vlans/vlan={interface}"

            try:
                r = requests.get(
                    url,
                    headers=headers,
                    auth=("admin", "admin"),
                    verify=False,
                    timeout=5
                )

                if r.status_code != 200:
                    rätt = False

            except requests.exceptions.RequestException as e:
                print(f"Kunde inte nå {ip}: {e}")
                rätt = False

        return rätt




def hämta_router_vlan(ip):
    for i in [10, 20, 30, 99]:
        url = f"https://{ip}/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet0%2F0%2F0/subinterfaces/subinterface={i}"

        headers = {
            "Accept": "application/yang-data+json"
        }

        try:
            r = requests.get(
                url,
                headers=headers,
                auth=("admin", "admin"),
                verify=False,
                timeout=5
            )

            sub = r.json()["openconfig-interfaces:subinterface"]
            if isinstance(sub, list):
                sub = sub[0]

            adress = sub["openconfig-if-ip:ipv4"]["addresses"]["address"][0]["config"]
            enabled = sub["config"]["enabled"]

        except Exception:
            return False
    return True

def hämta_trunk_router(ip):
    url = f"https://{ip}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet"

    try:
        r = requests.get(url, headers={"Accept": "application/yang-data+json"},
                         auth=("admin", "admin"), verify=False, timeout=5)
        interfaces = r.json()["Cisco-IOS-XE-native:GigabitEthernet"]
    except Exception:
        return False

    vlans = []
    for gi in interfaces:
        vlan = gi.get("encapsulation", {}).get("dot1Q", {}).get("vlan-id")
        if vlan:
            vlans.append(int(vlan))

    for v in [10, 20, 30, 99]:
        if v not in vlans:
            return False

    return True

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

def hämta_access():
    lista = [10,20,30]
    räknare = 0
    for i in range(1, 4):
        ip = f'10.0.0.{i}'
        rätt = True
        for j in range(22, 25):
            url = f"https://{ip}/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1%2F0%2F{j}/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan"

            förväntad = lista[räknare]
            räknare += 1
            if räknare == 3:
                räknare = 0
            headers = {
                "Accept": "application/yang-data+json"
            }

            try:
                r = requests.get(
                    url,
                    headers=headers,
                    auth=("admin", "admin"),
                    verify=False,
                    timeout=5
                )
                svar = r.json()["openconfig-vlan:switched-vlan"]["config"]

                if svar.get("interface-mode") != "ACCESS" or svar.get("access-vlan") != förväntad:
                    rätt = False
            except Exception as e:
                print(f"Kunde inte nå {ip}: {e}")
                rätt = False

        return rätt

if get_stp():
    print('ALLA ÄR RAPID_PVST')
else:
    print('ALLA ÄR INTE RAPID_PVST')
get_native()

if hämta_hastighet():
    print('Hastighet Rätt')
if hämta_vtp():
    print('VTP Rätt')
if hämta_vlan():
    print('Vlan Rätt')

print(hämta_mac(), 'är stp root bridge')

if hämta_access():
    print('Accessportar rätt')
else:
    print('ACCESSPORTAR FEL')

if hämta_router_vlan('10.0.0.4'):
    print('Alla vlan finns på Routern')

if hämta_trunk_router('10.0.0.4'):
    print('Router on a stick fungerar')
else:
    print('Router on a stick trasig')

