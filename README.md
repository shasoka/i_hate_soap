## 🧼 Мыло, mtom/xop и прочие радости жизни

![nu_prosto_k_slovu](readme_imgs/img.png)

---

### Как это развернуть?

> [!WARNING]
> Это чудо писалось на `Python 3.10`. Заведется ли на чем-то моложе? - не знаю.

1. Клиент и сервер пользуются общим окружением
2. В файлах `.env`, `.\server\core\config.py` и `.\client\config.py` указаны переменные, с которыми можно (и нужно) играться
3. Файл `.\scripts\sql\tables.sql` говорит сам за себя
4. Открытый и закрытый ключи получаем при помощи `openssl`:
    - Закрытый ключ:
        ```shell
        openssl genrsa -out .\certs\jwt_private.pem 2048
        ```
    - Открытый ключ:
        ```shell
        openssl rsa -in .\certs\jwt_private.pem -outform PEM -pubout -out .\certs\jwt_public.pem
        ```
5. Создаем виртуальное окружение `python -m venv venv`
6. Активируем его `.\venv\Scripts\activate`

> [!IMPORTANT]
> Далее магия 🪄: единственная живая библиотека для поднятия SOAP-сервиса на `Python` - это [Spyne](http://spyne.io/#inprot=HttpRpc&outprot=JsonDocument&s=rpc&tpt=WsgiApplication&validator=true).
> Но! Оно очень плохо умеет в `MTOM`. Поэтому пришлось поковырять исходники, и заставить его работать.

7. Создаем директорию для моего форка `Spyne`: `cd .\venv\Lib\site-packages\ && mkdir spyne`
8. Находясь в новоиспеченной директории: `git clone https://github.com/shasoka/spyne -b fixing-mtom-xop .`
9. Билдим библиотеку: `python setup.py install`
10. Поздравляю 🤝 Устанавливаем остальные зависимости: `pip install -r .\requirements.txt`
11. Ну, все, победа!
    - Запуск сервера: `python .\server\main.py`
    - Запуск клиента: `python .\client\main.py`

### Что-то про аптайм

Формула для вычисления процента времени работы сервера:

```math
\text{uptime\_percentage} = \frac{\sum (t_{\text{death\_i}} - t_{\text{start\_i}}) + (t_{\text{now}} - t_{\text{start\_n}})}{t_{\text{now}} - t_{\text{start\_0}}}
```

### И еще

Кому интересно `pull request` в `Spyne` [тут](https://github.com/arskom/spyne/pull/716)
