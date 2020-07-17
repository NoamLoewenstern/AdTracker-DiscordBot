from typing import List


class CommandActionFormatter:
    def __init__(self, command,  # argparse._SubParsersAction._ChoicesPseudoAction
                 subactions: List = []):
        self.command = command.dest
        self.help = command.help
        self.metavar = command.metavar
        self.subactions = subactions

    def basic_help(self, ljust: int = 16):
        return f'{self.command.ljust(ljust)}{self.help}'

    def format_help(self):
        return "test"


class ActionGroupFormatter:
    def __init__(self, title: str, usage: str = '', help: str = '',
                 commands: List[CommandActionFormatter] = [],
                 general_flags: List[CommandActionFormatter] = []):
        self.title = title
        self.usage = usage
        self.help = help
        self.commands = commands
        self.general_flags = general_flags

    def format_usage(self):
        # Originaly used to format the usage with the Optional-Flags, but it is done internaly
        # general_flags = ' '.join([f'[{flag.command}]' for flag in self.general_flags])
        # return f'Usage: {self.usage} {general_flags}'
        return f'Usage: {self.usage}'

    def format_commands(self):
        max_item_name_length = 4 + max([len(command.command) for command in self.commands])
        formated_commands = [(' '*4) + command.basic_help(ljust=max_item_name_length)
                             for command in self.commands]
        return "Commands:\n" + '\n'.join(formated_commands)

    def format_flags(self):
        max_item_name_length = 4 + max([len(flag.command) for flag in self.general_flags])
        formated_flags = [(' '*4) + flag.basic_help(ljust=max_item_name_length)
                          for flag in self.general_flags]
        return "Optional Flags:\n" + '\n'.join(formated_flags)

    def format_help(self):
        return f'{self.title}\n\n' + '\n\n'.join([self.format_usage(),
                                                  self.format_commands(),
                                                  self.format_flags(),
                                                  ])
