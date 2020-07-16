import argparse
from enum import Enum

from bot.controllers.command import Commands
from constants import Platforms
from errors import MyArgparseArgumentError, NotExpectedErrorParsing

from .formatters import ActionGroupFormatter, CommandActionFormatter
from .parser import ArgumentParser


class ArgsDoc(str, Enum):
    campaign_id = 'Defaults to All Campaigns'
    time_interval = '(int)d'
    filter_limit = '(int)'
    threshold = '(int|float)'


class FlagsDoc(str, Enum):
    # output_format
    filter_fields = 'Returns Fields in Specified List.     Example Format: /fields:id,name,spent'
    filter_limit = 'Returns Up to Given Limit of Results. Example Format: /limit:5'


PLATFORMS = [Platforms.MGID.value, Platforms.ZEROPARK.value]


class CommandHelpDocumentation:
    def __init__(self):
        prog = "/{}".format('|'.join(PLATFORMS))
        self.parser = ArgumentParser(prog=prog, usage=f"{{/help | {prog}}} <COMMAND> [-h]")
        self.subparser = self.parser.add_subparsers(title='Commands')
        self._add_commands_to_subparser(self.subparser)
        self.parser.add_argument(FlagsDoc.filter_fields.name, nargs='?', help=FlagsDoc.filter_fields.value)
        self.parser.add_argument(FlagsDoc.filter_limit.name, nargs='?', help=FlagsDoc.filter_limit.value)

        self._inject_positional_options_into_usage(self.parser)

        self.command_group_help = self.get_arg_group_help_formatter()

    def _add_commands_to_subparser(self, subparser):
        list_campaigns = subparser.add_parser(Commands.list_campaigns.value, help='List Campaigns Basic INFO')
        list_campaigns.add_argument(ArgsDoc.campaign_id.name, nargs='?', help=ArgsDoc.campaign_id.value)

        stats_campaign = subparser.add_parser(Commands.stats_campaign.value, help='List Campaigns STATS')
        stats_campaign.add_argument(ArgsDoc.campaign_id.name, nargs='?', help=ArgsDoc.campaign_id.value)
        stats_campaign.add_argument(ArgsDoc.time_interval.name, nargs='?',
                                    help=ArgsDoc.time_interval.value)

        spent_campaign = subparser.add_parser(
            Commands.spent_campaign.value, help='List Campaigns SPENT Stats')
        spent_campaign.add_argument(ArgsDoc.campaign_id.name, nargs='?', help=ArgsDoc.campaign_id.value)
        spent_campaign.add_argument(ArgsDoc.time_interval.name, nargs='?',
                                    help=ArgsDoc.time_interval.value)

        campaign_bot_traffic = subparser.add_parser(Commands.campaign_bot_traffic.value,
                                                    help='List Campaigns BOT TRAFFIC')
        campaign_bot_traffic.add_argument(ArgsDoc.campaign_id.name,
                                          nargs='?', help=ArgsDoc.campaign_id.value)
        campaign_bot_traffic.add_argument(ArgsDoc.time_interval.name, nargs='?',
                                          help=ArgsDoc.time_interval.value)

        widgets_top = subparser.add_parser(Commands.widgets_top.value,
                                           help="List Campaign's TOP Widgets CONVERSIONS")
        widgets_top.add_argument(ArgsDoc.campaign_id.name)
        widgets_top.add_argument(ArgsDoc.filter_limit.name, nargs='?',
                                 help=ArgsDoc.filter_limit.value)
        widgets_top.add_argument(ArgsDoc.time_interval.name, nargs='?',
                                 help=ArgsDoc.time_interval.value)

        widgets_high_cpa = subparser.add_parser(Commands.widgets_high_cpa.value,
                                                help="List Campaign's Widgets with HIGH CPA")
        widgets_high_cpa.add_argument(ArgsDoc.campaign_id.name)
        widgets_high_cpa.add_argument(ArgsDoc.threshold.name, help=ArgsDoc.threshold.value)
        widgets_high_cpa.add_argument(ArgsDoc.time_interval.name, nargs='?',
                                      help=ArgsDoc.time_interval.value)

        widgets_low_cpa = subparser.add_parser(Commands.widgets_low_cpa.value,
                                               help="List Campaign's Widgets with LOW CPA")
        widgets_low_cpa.add_argument(ArgsDoc.campaign_id.name)
        widgets_low_cpa.add_argument(ArgsDoc.threshold.name, help=ArgsDoc.threshold.value)
        widgets_low_cpa.add_argument(ArgsDoc.time_interval.name, nargs='?',
                                     help=ArgsDoc.time_interval.value)

        widgets_kill_longtail = subparser.add_parser(Commands.widgets_kill_longtail.value,
                                                     help=r"PAUSE Campaign's Widgets Where SPENT Under {threshold}")
        widgets_kill_longtail.add_argument(ArgsDoc.campaign_id.name)
        widgets_kill_longtail.add_argument(ArgsDoc.threshold.name, help=ArgsDoc.threshold.value)

        widgets_turn_on_all = subparser.add_parser(Commands.widgets_turn_on_all.value,
                                                   help="RESUME All Campaign's Widgets")
        widgets_turn_on_all.add_argument(ArgsDoc.campaign_id.name)

        widget_kill_bot_traffic = subparser.add_parser(Commands.widget_kill_bot_traffic.value,
                                                       help=r"PAUSE Campaign's Widgets with {threshold} Percent BOT-TRAFFIC")
        widget_kill_bot_traffic.add_argument(ArgsDoc.campaign_id.name)
        widget_kill_bot_traffic.add_argument(ArgsDoc.threshold.name, help=ArgsDoc.threshold.value)
        widget_kill_bot_traffic.add_argument(ArgsDoc.time_interval.name,
                                             help=ArgsDoc.time_interval.value)

        return subparser

    def _inject_positional_options_into_usage(self, parser):
        optional_names = []
        for positional_action in parser._get_positional_actions()[1:]:
            name = positional_action.dest
            optional_names.append(f'[{name}]')
        parser.usage += ' ' + ' '.join(optional_names)
        return parser

    def get_arg_group_help_formatter(self):
        commands_formatters = \
            [CommandActionFormatter(command=command,
                                    subactions=self.subparser.choices[command.dest]._actions[1:])
             for command in self.subparser._choices_actions]
        general_flags_actions = [action for action in self.parser._actions
                                 if isinstance(action, argparse._StoreAction)]
        flags_formatters = [CommandActionFormatter(command=action)
                            for action in general_flags_actions]
        action_group_formatter = ActionGroupFormatter('Ads-Discord-Bot',
                                                      #   usage=self.parser.format_usage(),
                                                      usage=self.parser.usage,
                                                      commands=commands_formatters,
                                                      general_flags=flags_formatters)
        commands_group_help = action_group_formatter.format_help()
        return commands_group_help

    def program_help(self):
        return self.command_group_help

    def parse_command(self, command: str):
        args = command.split(' ')
        if args[0] in ('/?', '/help'):
            return False, self.program_help()
        if len(args) == 1 or (len(args) == 2 and '-h' in args):
            return False, self.program_help()
        try:
            parsed_args = self.parser.parse_args(args[1:])
            return True, parsed_args
        except (MyArgparseArgumentError, argparse.ArgumentError) as e:
            return False, e.message
        except SystemExit:
            raise NotExpectedErrorParsing("[!] Unexpected Parsing Command, Needs to be Checked.")
