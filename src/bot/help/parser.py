import argparse
import sys

from errors import MyArgparseArgumentError


class ArgumentParser(argparse.ArgumentParser):
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
        pass

    def exit(self, status=0, message=None):
        pass

    def error(self, message):
        exc = sys.exc_info()[1]
        if exc:
            exc.argument = self._get_action_from_name(exc.argument_name)
            raise exc
        if message:
            raise MyArgparseArgumentError(message)

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
