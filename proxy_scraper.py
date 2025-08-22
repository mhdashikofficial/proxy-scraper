import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
from colorama import Fore, Style, init

init(autoreset=True)

class ProxyScraper:
    def __init__(self, max_proxies=200):
        self.max_proxies = max_proxies
        self.proxies = []
        self.sources = [
            "https://www.sslproxies.org/",
            "https://free-proxy-list.net/",
            "https://www.us-proxy.org/"
        ]
    
    def fetch_proxies(self):
        print(Fore.CYAN + "Starting proxy scraping..." + Style.RESET_ALL)
        for source in self.sources:
            try:
                print(Fore.YELLOW + "Fetching from: " + source + Style.RESET_ALL)
                response = requests.get(source, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                table = soup.find('table', {'id': 'proxylisttable'})
                if not table:
                    continue
                rows = table.find_all('tr')[1:]
                for row in rows:
                    if len(self.proxies) >= self.max_proxies:
                        break
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        proxy_type = "https" if "ssl" in source else "http"
                        country = cols[3].text.strip() if len(cols) > 3 else "Unknown"
                        anonymity = cols[4].text.strip() if len(cols) > 4 else "Unknown"
                        self.proxies.append({'ip': ip, 'port': port, 'type': proxy_type, 'country': country, 'anonymity': anonymity, 'source': source})
                print(Fore.GREEN + "Found " + str(len(self.proxies)) + " proxies so far" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + "Error fetching from " + source + ": " + str(e) + Style.RESET_ALL)
        return self.proxies
    
    def check_proxy(self, proxy, timeout=3):
        try:
            proxies = {"http": proxy['type'] + "://" + proxy['ip'] + ":" + proxy['port'], "https": proxy['type'] + "://" + proxy['ip'] + ":" + proxy['port']}
            test_url = "http://httpbin.org/ip"
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            if response.status_code == 200:
                return True, proxy
            else:
                return False, proxy
        except:
            return False, proxy
    
    def validate_proxies(self):
        print(Fore.CYAN + "Validating proxies..." + Style.RESET_ALL)
        valid_proxies = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.check_proxy, proxy) for proxy in self.proxies]
            for future in concurrent.futures.as_completed(futures):
                is_valid, proxy = future.result()
                if is_valid:
                    valid_proxies.append(proxy)
                    print(Fore.GREEN + "Valid proxy: " + proxy['ip'] + ":" + proxy['port'] + " (" + proxy['country'] + ")" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Invalid proxy: " + proxy['ip'] + ":" + proxy['port'] + Style.RESET_ALL)
        self.proxies = valid_proxies
        return valid_proxies
    
    def save_to_file(self, filename="proxies.txt"):
        if not self.proxies:
            print(Fore.RED + "No proxies to save!" + Style.RESET_ALL)
            return False
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("HIGH-QUALITY PROXY LIST\n")
                f.write("=" * 80 + "\n")
                f.write("Generated on: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
                f.write("Total proxies: " + str(len(self.proxies)) + "\n")
                f.write("=" * 80 + "\n\n")
                countries = {}
                for proxy in self.proxies:
                    country = proxy['country']
                    if country not in countries:
                        countries[country] = []
                    countries[country].append(proxy)
                for country, proxies in countries.items():
                    f.write("\n" + "-" * 40 + "\n")
                    f.write("Country: " + country.upper() + " (" + str(len(proxies)) + " proxies)\n")
                    f.write("-" * 40 + "\n")
                    for proxy in proxies:
                        f.write(proxy['type'].upper().ljust(8) + " " + proxy['ip'].ljust(15) + ":" + proxy['port'].ljust(6) + " Anonymity: " + proxy['anonymity'].ljust(10) + " Source: " + proxy['source'] + "\n")
                f.write("\n" + "=" * 80 + "\n")
                f.write("SUMMARY\n")
                f.write("=" * 80 + "\n")
                f.write("Total countries: " + str(len(countries)) + "\n")
                country_counts = sorted([(country, len(proxies)) for country, proxies in countries.items()], key=lambda x: x[1], reverse=True)
                for country, count in country_counts:
                    f.write(country + ": " + str(count) + " proxies\n")
                f.write("=" * 80 + "\n")
            print(Fore.GREEN + "Successfully saved " + str(len(self.proxies)) + " proxies to " + filename + Style.RESET_ALL)
            return True
        except Exception as e:
            print(Fore.RED + "Error saving to file: " + str(e) + Style.RESET_ALL)
            return False
    
    def display_stats(self):
        if not self.proxies:
            print(Fore.RED + "No proxies to display!" + Style.RESET_ALL)
            return
        countries = {}
        types = {}
        anonymity_levels = {}
        for proxy in self.proxies:
            country = proxy['country']
            countries[country] = countries.get(country, 0) + 1
            proxy_type = proxy['type']
            types[proxy_type] = types.get(proxy_type, 0) + 1
            anonymity = proxy['anonymity']
            anonymity_levels[anonymity] = anonymity_levels.get(anonymity, 0) + 1
        print(Fore.CYAN + "\n" + "=" * 50)
        print("PROXY STATISTICS")
        print("=" * 50 + Style.RESET_ALL)
        print(Fore.YELLOW + "Total proxies: " + str(len(self.proxies)))
        print(Fore.GREEN + "\nBy Country:" + Style.RESET_ALL)
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
            print("  " + country + ": " + str(count))
        print(Fore.GREEN + "\nBy Type:" + Style.RESET_ALL)
        for proxy_type, count in types.items():
            print("  " + proxy_type + ": " + str(count))
        print(Fore.GREEN + "\nBy Anonymity:" + Style.RESET_ALL)
        for anonymity, count in anonymity_levels.items():
            print("  " + anonymity + ": " + str(count))

def main():
    print(Fore.MAGENTA + "")
    print("================================================")
    print("      HIGH-QUALITY PROXY SCRAPER")
    print("           WITH COUNTRY INFO")
    print("================================================")
    print(Style.RESET_ALL)
    scraper = ProxyScraper(max_proxies=200)
    proxies = scraper.fetch_proxies()
    if not proxies:
        print(Fore.RED + "No proxies were found!" + Style.RESET_ALL)
        return
    valid_proxies = scraper.validate_proxies()
    if not valid_proxies:
        print(Fore.RED + "No valid proxies found!" + Style.RESET_ALL)
        return
    scraper.display_stats()
    filename = "proxies_" + time.strftime("%Y%m%d_%H%M%S") + ".txt"
    scraper.save_to_file(filename)
    print(Fore.GREEN + "\nDone! Check " + filename + " for your proxy list." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
