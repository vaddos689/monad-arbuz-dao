import inquirer
from termcolor import colored
from inquirer.themes import load_theme_from_dict as loadth


# MAIN MENU
def get_action() -> str:
    """Пользователь выбирает действие через меню"""

    theme = {
        'Question': {
            'brackets_color': 'bright_yellow'
        },
        'List': {
            'selection_color': 'bright_blue'
        },
    }

    question = [
        inquirer.List(
            "action",
            message=colored('Выберите ваше действие', 'light_yellow'),
            choices=[
                'Import data to db',
                'Monad',
                'Apriori',
                'OnChain stats',
                'Exit'
            ]
        )
    ]

    return inquirer.prompt(question, theme=loadth(theme))['action']


# Monad
def monad_menu() -> str:
    """Меню для Monad"""
    theme = {
        'Question': {
            'brackets_color': 'bright_yellow'
        },
        'List': {
            'selection_color': 'bright_blue'
        },
    }

    question = [
        inquirer.List(
            "swap_action",
            message=colored('Выберите действие для Monad', 'light_yellow'),
            choices=[
                "MON faucet",
                "Exit"
            ]
        )
    ]

    return inquirer.prompt(question, theme=loadth(theme))['swap_action']

# Apriori
def apriori_menu() -> str:
    """Меню для Apriori"""
    theme = {
        'Question': {
            'brackets_color': 'bright_yellow'
        },
        'List': {
            'selection_color': 'bright_blue'
        },
    }

    question = [
        inquirer.List(
            "swap_action",
            message=colored('Выберите действие для Monad', 'light_yellow'),
            choices=[
                "Stake MON",
                "Exit"
            ]
        )
    ]

    return inquirer.prompt(question, theme=loadth(theme))['swap_action']

# OnChain Stats
def onchain_stats_menu() -> str:
    """Пользователь выбирает действие через меню"""

    theme = {
        'Question': {
            'brackets_color': 'bright_yellow'
        },
        'List': {
            'selection_color': 'bright_blue'
        },
    }

    question = [
        inquirer.List(
            "action",
            message=colored('Выберите ваше действие', 'light_yellow'),
            choices=[
                'Update MON balance',
                'Exit'
            ]
        )
    ]

    return inquirer.prompt(question, theme=loadth(theme))['action']