import psutil
import socket

def get_wifi_ip():
    addrs = psutil.net_if_addrs()
    for interface, details in addrs.items():
       # print(f'Interface: {interface}')
        for detail in details:
            if detail.family == socket.AF_LINK:
                print(f'  MAC: {detail.address}')
            elif detail.family == socket.AF_INET:
                #print(f'  IP: {detail.address}')
                if 'Wi-Fi' in interface:
                    wifi_ip = detail.address
                    #print(f'O IP DA PLACA  DE Wi-Fi DO NOTEBOOK é: {wifi_ip}')
                    return print(f'O IP DA PLACA  DE Wi-Fi DO NOTEBOOK é: {wifi_ip}')
    return None

