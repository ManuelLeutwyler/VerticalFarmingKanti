###Authored by Manuel Leutwyler

from requests import get

while True:
    pH_Wert_becken_1 = get('https://dweet.io/get/dweets/for/verticalfarmingkanti')['with']['content']['ch2']
    pH_Wert_becken_2 = get('https://dweet.io/get/dweets/for/verticalfarmingkanti')['with']['content']['ch3']

    print(pH_Wert_becken_1, pH_Wert_becken_2)
