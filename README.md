
# Установка

1. Создать папку и скопировать путь до нее
2. Открыть cmd
3. Прописать команду
cd путькпапке
4. Скачать репозиторий в папку командой
```
git clone https://github.com/vaddos689/monad-arbuz-dao.git
```
5. 
```
cd monad-arbuz-dao
```
6. Создать виртуальное окружение Python (нужен питон 3.12)
```
py -3.12 -m venv .venv
```
7. Активируем виртуальное окружение (windows):
```
.venv\Scripts\activate
```
8. Скачать нужные библиотеки:
```
pip install -r requirements.txt
```
# Настройка
1. В .env файл требуется добавить api ключ для решения капчи от Capsolver (https://www.capsolver.com/)
2. После первого запуска будет создана папка import с файлами:
evm_pks.txt - приватные ключи кошельков
proxies.txt - прокси формата http://user:password@ip:port

# Запуск:
```
python main.py
```
