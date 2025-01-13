import os

COOKIES = {
    "JivoSiteLoaded": "1",
    "L": "Vhl0aX5+CQBhdlBEBHhbRnpyUEAJdVxKVj89CgMGADpQbXI=.1718692556.15777.385658.6605e6c0f527a8babbcabe3a0d459370",
    "PHPSESSID": "nkdf0chtqphr55kt0cqr7udjnu",
    "Session_id": "3:1736451565.5.0.1710921309676:UyWolzNJuIyBHDADoB8AKg:1.1.2:1|1918876230.7771247.2.2:7771247.3:1718692556|3:10301041.933941.1r4D4ZTMYSLqRGcvldihXryzbWM",
    "_ga": "GA1.1.729973931.1712940258",
    "_ga_PLRTBHGSEL": "GS1.1.1712940257.1.1.1712940292.25.0.1993651985",
    "_yasc": "XR+6ODqwrj/Dct8pvq1y4+DYyEQ1tuxel0jj0dBazvhjMqd4RrRIMdSA+I3QxSRWiHRWBA==",
    "_ym_d": "1726767605",
    "_ym_isad": "1",
    "_ym_uid": "1729937361852471791",
    "_ym_visorc": "w",
    "_ymab_param": "Xe7XqxVwyiFGGWalAe8jKmgy0vFErMxzL7MMDHV8u60k_2UycTpm-Lbc_v8iu2gVZzT2u9yI1iB43ue9cwORLH5IFSo",
    "cf_clearance": "LraEgpjYWKTlIUOFxqP8qzPf1hRdIs8NEeanvf0wFvM-1736588683-1.2.1.1-yoUUXBTfLrBxnUze.Z3lOMxVmDU8DoiSeZTY.p3wm7_uOrwowHRsssqHk0lscuJREQR3StUzfZck3T0047DwRwGM6BXm_j3U3oQzKKgToGSlMtdKOCCwCjQvD7pB2PiPg6xKi6iDH_RWt9NP6Q2eZfIDPB9GY6NWFmXAX9orMW8XPn4tvdQPgxE344QISBlMc1AARc3UVTNgYhzaUxmeROdTHGQQnRWEYqIiKUokT5lzLi1aICzMIZq3gt_6zo2_lUD7dxhIy6wCTYKHuBiKeU.wYkjdE9D3evF0dnY2xEAlRlZYcRc_qcVcRcnYWICz6bTFAm_wBmaj4D.sPAs87tj0bhKwgkdYHtKQ1l5TaPDWydwqUPyKqOSJlj2lzzxBVK3HgzNDFNk_eUPwpDPcnwRl80j5IgoGWKCnIBTjKOkLGRogxXl5YZkIxTtPggPc",
    "city": "moskow",
    "cityconfirmed": "true",
    "client": "75ae26a2a6c6937b2788f1d384c4a88cfc3f195c",
    "count": "120",
    "sort": "newtimedown",
}

BASE_URL = "https://leonardo.ru"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
BLOCKED_CATEGORY = ["Тематические подборки", "Подарочные сертификаты", "Распродажа",
                    "Новогодний ассортимент", "Идеи подарков", "Только онлайн"]
DB_URL = os.getenv("DB_URL", "postgresql://postgres:2525@localhost/leonardo_parser")
