import argparse
import re
from enum import Enum
from typing import List

from bot.controllers.command import Commands
from config import (DEFAULT_ALL_CAMPAIGNS_ALIAS,
                    DEFAULT_CPA_THRESHOLD_INTERVAL, DEFAULT_TIME_INTERVAL)
from constants import Platforms
from errors import MyArgparseArgumentError, NotExpectedErrorParsingError

from .formatters import ActionGroupFormatter, CommandActionFormatter
from .parser import ArgumentParser


class ArgsDoc(str, Enum):
    campaign_id = f"(default: '{DEFAULT_ALL_CAMPAIGNS_ALIAS}')"
    widget_id = f"(default: '{DEFAULT_ALL_CAMPAIGNS_ALIAS}') "
    time_interval = f'(int)d (default: {DEFAULT_TIME_INTERVAL}) (use as FLAG, e.g /time_interval:20d) (alias: /time)'
    filter_limit = '(int) (default: all) (use as FLAG, e.g /filter_limit:20) (alias: /filter)'
    threshold = '(int|float)'


class CommandDoc(str, Enum):
    list_campaigns = 'List Campaigns Basic INFO'
    stats_campaign = 'List Campaigns STATS'
    spent_campaign = 'List Campaigns SPENT Stats'
    bot_traffic = 'List Campaigns BOT TRAFFIC'
    widgets_stats = "List Campaign's Widgets STATS"
    widgets_top = "List Campaign's TOP Widgets CONVERSIONS"
    widgets_high_cpa = "List Campaign's Widgets with HIGH CPA"
    widgets_low_cpa = "List Campaign's Widgets with LOW CPA"
    widgets_kill_longtail = "PAUSE Campaign's Widgets Where SPENT Under {threshold}"
    widgets_turn_on_all = "RESUME All Campaign's Widgets"
    widget_kill_bot_traffic = "PAUSE Campaign's Widgets with {threshold} Percent BOT-TRAFFIC"


class FlagsDoc(str, Enum):
    # output_format
    # filter_fields = 'Returns Fields in Specified List.     Example Format: /fields:id,name,spent'
    fields = 'Returns Fields in Specified List.     Example Format: --fields id,name,spent'
    # filter_limit = 'Returns Up to Given Limit of Results. Example Format: /limit:5'
    limit = 'Returns Up to Given Limit of Results. Example Format: --limit 5'
    ignore_errors = 'Ignore Error Results (if any). Example: --ignore-erros'


PLATFORMS = [Platforms.MGID.value, Platforms.ZEROPARK.value]


class CommandHelpDocumentation:
    def __init__(self):
        prog = "/{}".format('|'.join(PLATFORMS))
        self.parser = ArgumentParser(prog=prog, usage=f"{{/help | {prog}}} <COMMAND> [-h]")
        self.subparser = self.parser.add_subparsers(title='Commands')
        self._add_commands_to_subparser(self.subparser)

        self.optional_flags: List[str] = [FlagsDoc.fields.name, FlagsDoc.limit.name]
        self.parser.add_argument('--' + FlagsDoc.fields.name, nargs='?', help=FlagsDoc.fields.value)
        self.parser.add_argument('--' + FlagsDoc.limit.name, nargs='?', help=FlagsDoc.limit.value)
        self.parser.add_argument('--' + FlagsDoc.ignore_errors.name,
                                 nargs='?', help=FlagsDoc.ignore_errors.value)

        self._inject_positional_options_into_usage(self.parser)

        self.command_group_help = self.get_arg_group_help_formatter()

    def _add_commands_to_subparser(self, subparser):
        list_campaigns = subparser.add_parser(Commands.list_campaigns.value,
                                              description=CommandDoc.list_campaigns, help=CommandDoc.list_campaigns)
        list_campaigns.add_argument(ArgsDoc.campaign_id.name, nargs='?', help=ArgsDoc.campaign_id.value)

        stats_campaign = subparser.add_parser(Commands.stats_campaign.value,
                                              description=CommandDoc.stats_campaign, help=CommandDoc.stats_campaign)
        stats_campaign.add_argument(ArgsDoc.campaign_id.name, nargs='?', help=ArgsDoc.campaign_id.value)
        stats_campaign.add_argument(ArgsDoc.time_interval.name, nargs='?', help=ArgsDoc.time_interval.value)

        spent_campaign = subparser.add_parser(Commands.spent_campaign.value,
                                              description=CommandDoc.spent_campaign, help=CommandDoc.spent_campaign)
        spent_campaign.add_argument(ArgsDoc.campaign_id.name, nargs='?', help=ArgsDoc.campaign_id.value)
        spent_campaign.add_argument(ArgsDoc.time_interval.name, nargs='?', help=ArgsDoc.time_interval.value)

        campaign_bot_traffic = subparser.add_parser(Commands.campaign_bot_traffic.value,
                                                    description=CommandDoc.bot_traffic, help=CommandDoc.bot_traffic)
        campaign_bot_traffic.add_argument(ArgsDoc.campaign_id.name, nargs='?', help=ArgsDoc.campaign_id.value)
        campaign_bot_traffic.add_argument(ArgsDoc.time_interval.name, nargs='?',
                                          help=ArgsDoc.time_interval.value)

        widgets_stats = subparser.add_parser(Commands.widgets_stats.value,
                                             description=CommandDoc.widgets_stats, help=CommandDoc.widgets_stats)
        widgets_stats.add_argument(ArgsDoc.campaign_id.name, help=ArgsDoc.campaign_id.value)
        widgets_stats.add_argument(ArgsDoc.widget_id.name, nargs='?', help=ArgsDoc.widget_id.value)
        widgets_stats.add_argument(ArgsDoc.filter_limit.name, nargs='?', help=ArgsDoc.filter_limit.value)
        widgets_stats.add_argument(ArgsDoc.time_interval.name, nargs='?', help=ArgsDoc.time_interval.value)

        widgets_top = subparser.add_parser(Commands.widgets_top.value,
                                           description=CommandDoc.widgets_top, help=CommandDoc.widgets_top)
        widgets_top.add_argument(ArgsDoc.campaign_id.name)
        widgets_top.add_argument(ArgsDoc.filter_limit.name, nargs='?', help=ArgsDoc.filter_limit.value)
        widgets_top.add_argument(ArgsDoc.time_interval.name, nargs='?', help=ArgsDoc.time_interval.value)

        widgets_high_cpa = subparser.add_parser(Commands.widgets_high_cpa.value,
                                                description=CommandDoc.widgets_high_cpa, help=CommandDoc.widgets_high_cpa)
        widgets_high_cpa.add_argument(ArgsDoc.campaign_id.name)
        widgets_high_cpa.add_argument(ArgsDoc.threshold.name, help=ArgsDoc.threshold.value)
        widgets_high_cpa.add_argument(ArgsDoc.time_interval.name, nargs='?', help=ArgsDoc.time_interval.value)

        widgets_low_cpa = subparser.add_parser(Commands.widgets_low_cpa.value,
                                               description=CommandDoc.widgets_low_cpa, help=CommandDoc.widgets_low_cpa)
        widgets_low_cpa.add_argument(ArgsDoc.campaign_id.name)
        widgets_low_cpa.add_argument(ArgsDoc.time_interval.name, nargs='?', help=ArgsDoc.time_interval.value)
        widgets_low_cpa.add_argument(ArgsDoc.threshold.name, nargs='?', default=DEFAULT_CPA_THRESHOLD_INTERVAL,
                                     help=ArgsDoc.threshold.value)

        widgets_kill_longtail = subparser.add_parser(Commands.widgets_kill_longtail.value,
                                                     description=CommandDoc.widgets_kill_longtail, help=CommandDoc.widgets_kill_longtail)
        widgets_kill_longtail.add_argument(ArgsDoc.campaign_id.name)
        widgets_kill_longtail.add_argument(ArgsDoc.threshold.name, help=ArgsDoc.threshold.value)

        widgets_turn_on_all = subparser.add_parser(Commands.widgets_turn_on_all.value,
                                                   description=CommandDoc.widgets_turn_on_all, help=CommandDoc.widgets_turn_on_all)
        widgets_turn_on_all.add_argument(ArgsDoc.campaign_id.name)

        widget_kill_bot_traffic = subparser.add_parser(Commands.widget_kill_bot_traffic.value,
                                                       description=CommandDoc.widget_kill_bot_traffic, help=CommandDoc.widget_kill_bot_traffic)
        widget_kill_bot_traffic.add_argument(ArgsDoc.campaign_id.name)
        widget_kill_bot_traffic.add_argument(ArgsDoc.threshold.name, help=ArgsDoc.threshold.value)
        widget_kill_bot_traffic.add_argument(ArgsDoc.time_interval.name, help=ArgsDoc.time_interval.value)

        # list_sources = subparser.add_parser(Commands.list_sources.value,
        #                                     help=r"List Sources no Platform (Tracker)")

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

    def _fixed_optional_flags_in_command(self, args: List[str]):
        # TODO  parse from 'patterns.py' to get actual optional flags,
        """for now - assuming this parse is just for positional-args,
        and now actually using this parser JUST FOR COMMAND-HELP-DOCS and NOT for getting data
        so for now - removing flag checks """
        return [arg for arg in args if not re.match(r'^(--|/)\w+[ :=]?', arg)]
        # fixed_args = []
        # for arg in args:
        #     if arg.startswith('/'):
        #         arg = '--' + arg[1:]
        #     if arg.startswith('--'):
        #         arg = re.sub('^(--\w+?):(.+)$', '\\1=\\2', arg)
        #     fixed_args.append(arg)
        # return fixed_args

    def parse_command(self, command: str):
        args = command.split(' ')
        if (platform := args[0]) in ('/?', '/help'):
            return False, self.program_help()
        if len(args) == 1 or (len(args) == 2 and '-h' in args):
            return False, self.program_help()
        elif len(args) > 2 and '-h' in args and (command := args[1]) in self.subparser.choices:
            command_help = self.subparser.choices[command].format_help()
            return False, ArgumentParser._fix_format_usage(command_help)
        try:
            new_args = self._fixed_optional_flags_in_command(args[1:])
            parsed_args = self.parser.parse_args(new_args)
            return True, parsed_args
        except (MyArgparseArgumentError, argparse.ArgumentError) as e:
            return False, e.message
        except (Exception, SystemExit) as e:
            raise NotExpectedErrorParsingError(
                f'[!] Unexpected Parsing Command, Needs to be Checked. Error: {e}')
