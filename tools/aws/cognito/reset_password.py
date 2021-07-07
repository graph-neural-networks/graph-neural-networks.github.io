# pylint: disable=global-statement,redefined-outer-name
""" Script used to reset password of AWS Cognito users """
import argparse
from dataclasses import dataclass

import yaml

import cognito  # type: ignore


@dataclass(frozen=True)
class User:
    """ Class for AWS Cognito user """

    email: str

    def name(self) -> str:
        """ Generate the name field """
        return self.email


def parse_arguments():
    """ Parse Arguments """
    parser = argparse.ArgumentParser(
        description="AWS Cognito List Command Line",
        # usage="cognito_user.py [-h] aws_profile",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Show error details if there is any",
    )
    parser.add_argument(
        "-p",
        "--password",
        action="store",
        default=False,
        help="Set specified password to the users",
    )
    parser.add_argument("aws_profile", help="The file contains AWS profile")
    parser.add_argument(
        "emails",
        metavar="email",
        type=str,
        nargs="+",
        help="E-mail address of user to have password reset",
    )

    return parser.parse_args()


def reset_password(args):
    """ Load the profile data and reset password of users (by email address) """
    aws_profile = args.aws_profile
    emails = args.emails
    is_debug = args.debug
    password = args.password
    profile = yaml.load(open(aws_profile).read(), Loader=yaml.SafeLoader)
    client = cognito.init_client(profile)
    result = []

    for email in emails:
        if args.password:
            response = cognito.set_user_password(
                client, profile, User(email=email), password
            )
        else:
            response = cognito.reset_user_password(client, profile, User(email=email))
        cognito.show_error_response(response, is_debug)

    return result


if __name__ == "__main__":
    args = parse_arguments()
    users = reset_password(args)