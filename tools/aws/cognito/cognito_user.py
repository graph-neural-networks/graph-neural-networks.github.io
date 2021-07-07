# pylint: disable=global-statement,redefined-outer-name
""" Script used to create|disable AWS Cognito user """
import argparse
import sys
from dataclasses import dataclass
from typing import Any, Dict

import pandas
import yaml

import cognito  # type: ignore


@dataclass(frozen=True)
class User:
    """ Class for AWS Cognito user """

    email: str


def load_data(user_file, aws_profile):
    """ Load the profile data and user data """
    data: Dict[str, Any] = {}
    data["profile"] = yaml.load(open(aws_profile).read(), Loader=yaml.SafeLoader)
    data["client"] = cognito.init_client(data["profile"])

    # Prepare the user information
    failed, users, message = parse_file(user_file)
    if failed is True:
        print(message)
        if isinstance(users, pandas.DataFrame):
            print(users)
        sys.exit(2)

    data["users"] = users
    return data


def parse_arguments():
    """ Parse Arguments """
    parser = argparse.ArgumentParser(
        description="AWS Cognito User (dry-run format) Command Line",
        # usage="cognito_user.py [-h] [--check] [-d|-e] user_file aws_profile",
    )
    group = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "--check",
        action="store_true",
        default=False,
        help="Check the files without actually making the reqeust",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Show error details if there is any",
    )
    group.add_argument(
        "-a",
        "--assign-group",
        action="store",
        dest="group",
        default=False,
        help="Assign users listed in the file to specified group",
    )
    group.add_argument(
        "-d",
        "--disable",
        action="store_true",
        default=False,
        help="Disable users listed in the file",
    )
    group.add_argument(
        "-e",
        "--enable",
        action="store_true",
        default=False,
        help="Enable users listed in the file",
    )
    group.add_argument(
        "-r",
        "--remove",
        action="store",
        dest="remove_from_group",
        default=False,
        help="Remove users listed in the file from specified group",
    )
    group.add_argument(
        "-v",
        "--verified",
        action="store_true",
        default=False,
        help="Set email_verified for users listed in the file",
    )
    parser.add_argument(
        "user_file", help="The file contains user information for AWS Cognito",
    )
    parser.add_argument("aws_profile", help="The file contains AWS profile")

    return parser.parse_args()


def parse_file(path):
    """ Parse user file to read user information """
    has_error = False
    error_message = ""
    users = []

    _, ext = path.split("/")[-1].split(".")
    if ext == "xlsx":
        dataframe = pandas.read_excel(path)
    elif ext == "csv":
        dataframe = pandas.read_csv(path)
    else:
        has_error = True
        error_message = f"File {path} is not supported"

    if has_error is False:
        # Update column names
        dataframe.columns = [x.lower().replace(" ", "_") for x in dataframe.columns]

        # Change column headers to lowercase
        dataframe.columns = map(str.lower, dataframe.columns)

        # Check invalid rows/records
        no_email = dataframe["email"].isnull()
        invalid_rows = dataframe.loc[no_email]
        if len(invalid_rows.index) == 0:
            # No invalid records.  Let's go ahead
            # needs to clean up the Email field, sometimes it contains leading/ending spaces
            dataframe.loc[:, "email"] = dataframe.loc[:, "email"].apply(
                lambda x: x.strip()
            )
            users = [User(**kwargs) for kwargs in dataframe.to_dict(orient="records")]
        else:
            has_error = True
            error_message = "Invalid record(s) found"
            users = invalid_rows

    return has_error, users, error_message


if __name__ == "__main__":
    args = parse_arguments()
    data = load_data(args.user_file, args.aws_profile)

    # We can check, create, disable or enable user now
    if args.check:
        for user in data["users"]:
            print(user)
    elif args.disable:
        # Disable user
        for user in data["users"]:
            response = cognito.disable_user(data["client"], data["profile"], user)
            cognito.show_error_response(response, args.debug)
    elif args.enable:
        # Enable user
        for user in data["users"]:
            response = cognito.enable_user(data["client"], data["profile"], user)
            cognito.show_error_response(response, args.debug)
    elif args.remove_from_group:
        # Remove users from group
        for user in data["users"]:
            response = cognito.remove_from_group(
                data["client"], data["profile"], user, args.remove_from_group
            )
            cognito.show_error_response(response, args.debug)
    elif args.verified:
        # Enable user
        for user in data["users"]:
            response = cognito.update_user_attributes(
                data["client"], data["profile"], user, "email_verified", "true"
            )
            cognito.show_error_response(response, args.debug)
    else:
        # Create user
        for user in data["users"]:
            response = cognito.create_user(data["client"], data["profile"], user)
            cognito.show_error_response(response, args.debug)
            if args.group:
                response = cognito.add_to_group(
                    data["client"], data["profile"], user, args.group
                )
                cognito.show_error_response(response, args.debug)