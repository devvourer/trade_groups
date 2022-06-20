#  Проект по привлечению инвесторов
## Краткое описание:


Проект позволяет трейдерам собирать группы инвесторов для торгов на binance futures.

Трейдер создает группу, указывает необходимую сумму, дату старта и дату окончания группы

После окончания срока группы, подсчитывается прибыль от торгов и распределяется между инвесторами в соотношении какой процент от нужной суммы они инвестировали. 


## 🐳  Requirements
- [Docker Engine](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## ⚙️ Setup
В дериктории с проектом необходимо создать `.env` файл с содержимым:
- YOMONEY_POCKET=XXXXXXX [документация для взаимодествия с кошельком](https://yoomoney.ru/docs/payment-buttons/using-api/flow)
- YOMONEY_SECRET=XXXXXXX


- TELEGRAM_BOT_TOKEN=XXXXXXX `Бот отправляет уведомления`


- EMAIL_USER=XXXXXXX `Регистрация и активация аккаунта в проекте происходит по почте `
- EMAIL_PASSWORD=XXXXXXX


- DB_NAME=XXXXXXX
- DB_PASSWORD=XXXXXXX
- DB_PORT=XXXXXXX
- DB_USER=XXXXXXX
- DB_HOST=XXXXXXX


- BINANCE_API=XXXXXXX `Нужны для работы проекта, дать ключу права на вывод, перевод средств`
- BINANCE_SECRET=XXXXXXX


## 🚀 Deployment
Подключитесь к удаленному серверу:

    ssh root@host

Смените рабочую директорию на:

    cd trade_groups/


Клонируйте репозиторий:

    git clone https://github.com/devvourer/trade_groups.git

Запустите эти команды:

    docker-compose build
    docker-compose up -d
