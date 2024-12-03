# Alpaca Bot

Alpaca Bot is a trading bot that uses a simple momentum signal to buy and rebalance stocks based on the momentum indicator. This bot is built using Python and managed with Miniconda.

## Features

- Uses momentum indicator to make trading decisions
- Automatically buys and rebalances stocks
- Built with Python
- Managed with Miniconda

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/alpaca-bot.git
    cd alpaca-bot
    ```

2. Create and activate a new conda environment:
    ```sh
    conda create --name alpaca-bot python=3.8
    conda activate alpaca-bot
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Configure your Alpaca APCA-API-KEY-ID and SECRET KEY in a `.env` file.
2. Run the bot:
    ```sh
    APCA-API-KEY-ID=[KEY HERE]
    APCA-API-SECRET-KEY=[KEY HERE]
    ```

# NOTE
This bot will not guarantee to make you any money! Don't use it in a live trading environment! Use in Paper account only!
