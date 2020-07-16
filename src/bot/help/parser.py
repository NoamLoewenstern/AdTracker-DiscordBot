import argparse
import re
import sys

from errors import MyArgparseArgumentError


class ArgumentParser(argparse.ArgumentParser):

    def _fix_format_usage(self, usage_msg):
        fixed_usage = usage_msg
        pattern_usage_with_sub_command = re.compile(r'(.*)( .+? \[-h\])(?=.+\[-h\])',
                                                    re.DOTALL | re.IGNORECASE)
        replace_space_in_usage = re.compile(r'\n +( \[-h])', re.DOTALL | re.IGNORECASE)
        fixed_usage = pattern_usage_with_sub_command.sub(r'\1', fixed_usage)
        fixed_usage = replace_space_in_usage.sub(r'\1', fixed_usage)

        return fixed_usage

    def format_usage(self):
        orig_usage = super().format_usage()
        if orig_usage.count('[-h]') != 2:
            return orig_usage
        return self._fix_format_usage(orig_usage)

    def format_help(self):
        orig_help = super().format_help()
        if orig_help.count('[-h]') != 2:
            return orig_help
        return self._fix_format_usage(orig_help)

    def _get_action_from_name(self, name):
        """Given a name, get the Action instance registered with this parser.
        If only it were made available in the ArgumentError object. It is
        passed as it's first arg...
        """
        container = self._actions
        if name is None:
            return None
        for action in container:
            if '/'.join(action.option_strings) == name:
                return action
            elif action.metavar == name:
                return action
            elif action.dest == name:
                return action

    def _print_message(self, message, file=None):
        # super()._print_message(message, file)  # just prints to file
        raise MyArgparseArgumentError(message)

    def exit(self, status=0, message=None):
        pass

    def error(self, message):
        exc = sys.exc_info()[1]
        if exc:
            exc.argument = self._get_action_from_name(exc.argument_name)
            raise exc
        if message:
            invalid_command_message = message + '\n\n' + self.format_help()
            raise MyArgparseArgumentError(invalid_command_message)

    # def parse_args(self, *args, **kwargs):
    #     try:
    #         args = super().parse_args(*args, **kwargs)
    #     except (MyArgparseArgumentError, argparse.ArgumentError) as e:
    #         e.message += '\n' + self.format_help()

    def parse_known_args(self, *args, **kwargs):
        super_result = super().parse_known_args(*args, **kwargs)
        if super_result is None:
            super_result = (None, None)
        return super_result

    def _parse_known_args(self, *args, **kwargs):
        super_result = super()._parse_known_args(*args, **kwargs)
        if super_result is None:
            super_result = (None, None)
        return super_result
