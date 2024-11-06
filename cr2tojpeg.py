import rawpy
import imageio
import os
import configparser
from tqdm import tqdm
from colorama import init, Fore, Style

# Colorama ve TQDM için başlangıç ayarları
init(autoreset=True)

# Configparser kullanarak ini dosyasını oku
config = configparser.ConfigParser()
config.read('config.ini')

input_dir = config['PATHS']['input_dir']
output_dir = config['PATHS']['output_dir']
log_file = config['PATHS']['log_file']

# Program başlığı
print(Style.BRIGHT + Fore.CYAN + """
  ____  ____   _     
 / ___||  _ \ / \    
 \___ \| | | / _ \   
  ___) | |_| / ___ \ 
 |____/|____/_/   \_\\
         CR2 to JPG Dönüştürücü - Seyrani Demirel
""")

# Toplam dosya sayısını bulmak için dosyaları say
total_files = sum([len(files) for r, d, files in os.walk(input_dir) if any(f.lower().endswith('.cr2') for f in files)])

# İstatistikler
converted_files = 0
failed_files = 0
failed_files_list = []

with open(log_file, 'w') as log:
    log.write("Dönüştürme Logları\n")
    log.write("==================\n")

    with tqdm(total=total_files, desc="Dönüştürme işlemi", unit="dosya", colour='green') as pbar:
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.cr2'):
                    cr2_path = os.path.join(root, file)
                    jpg_path = os.path.join(output_dir, os.path.relpath(cr2_path, input_dir))
                    jpg_path = os.path.splitext(jpg_path)[0] + '.jpg'

                    try:
                        os.makedirs(os.path.dirname(jpg_path), exist_ok=True)
                        with rawpy.imread(cr2_path) as raw:
                            rgb = raw.postprocess()
                            imageio.imsave(jpg_path, rgb)
                        converted_files += 1
                    except Exception as e:
                        print(Fore.RED + f"Hata oluştu: {e}, dosya atlandı: {cr2_path}")
                        failed_files += 1
                        failed_files_list.append(cr2_path)
                        log.write(f"Hata oluştu: {e}, dosya atlandı: {cr2_path}\n")

                    pbar.update(1)

# İstatistikleri ve logları kullanıcıya göster
print(Style.BRIGHT + Fore.CYAN + f"\nDönüştürme işlemi tamamlandı.\nToplam dosya: {total_files}\nDönüştürülen dosya: {converted_files}\nHata veren dosya: {failed_files}")

with open(log_file, 'a') as log:
    log.write("\nDönüştürme İstatistikleri\n")
    log.write("=========================\n")
    log.write(f"Toplam dosya: {total_files}\n")
    log.write(f"Dönüştürülen dosya: {converted_files}\n")
    log.write(f"Hata veren dosya: {failed_files}\n")

    if failed_files_list:
        log.write("\nHata Veren Dosyalar\n")
        log.write("===================\n")
        for failed_file in failed_files_list:
            log.write(f"{failed_file}\n")

print(Style.BRIGHT + Fore.CYAN + f"Log dosyası kaydedildi: {log_file}")
