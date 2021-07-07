# pylint: disable=global-statement,redefined-outer-name
""" Script used to list AWS Cognito users """
import argparse
from dataclasses import asdict, dataclass

import pandas
import yaml

import cognito  # type: ignore


@dataclass()
class User:
    """ Class for AWS Cognito user """

    email: str
    name: str
    committee: str = ""

    # def name(self) -> str:
    #     """ Generate the name field """
    #     return f"{self.first_name} {self.last_name}"


def find_duplicate(client, profile, is_debug=False):
    result = []
    users = []
    groups = cognito.list_groups(client, profile)
    for group in groups:
        if is_debug:
            print(f"{group.name}:\t{group.description}")
        group_users = cognito.list_group_users(client, profile, group.name)
        for group_user in group_users:
            if is_debug:
                print(group_user)
            user = next((u for u in users if u.email == group_user.email), None)
            if user:
                user.committee = f"{user.committee}|{group.name}"
            else:
                users.append(
                    User(
                        name=group_user.name(),
                        email=group_user.email,
                        committee=group.name,
                    )
                )
    for user in users:
        groups = user.committee.split("|")
        if len(groups) > 1:
            # User in multiple groups
            result.append(user)

    return result


def load_data(args):
    """ Load the profile data and get pool users """
    aws_profile = args.aws_profile
    check_duplicate = args.duplicate
    group = args.group
    is_debug = args.debug

    profile = yaml.load(open(aws_profile).read(), Loader=yaml.SafeLoader)
    client = cognito.init_client(profile)
    result = []

    if group:
        users = cognito.list_group_users(client, profile, group)
    elif check_duplicate:
        users = find_duplicate(client, profile, is_debug)
    else:
        users = cognito.list_users(client, profile)
    for user in users:
        if is_debug:
            if check_duplicate is False:
                print(
                    f"user: {user.name()} <{user.email}>, "
                    + f"enabled: {user.enabled}, "
                    + f"email_verified: {user.email_verified}, "
                    + f"user_status: {user.user_status}"
                )
        if group:
            result.append(User(name=user.name(), email=user.email, committee=group))
        elif check_duplicate:
            result.append(user)
        else:
            result.append(User(name=user.name(), email=user.email))

    return result


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
        help="Show the users is enabled or not",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-d",
        "--duplicate",
        action="store_true",
        default=False,
        help="Find the users in multiple groups",
    )
    group.add_argument(
        "-g",
        "--group",
        action="store",
        default=False,
        help="Get the users from the specified group only",
    )
    parser.add_argument("aws_profile", help="The file contains AWS profile")

    return parser.parse_args()


def save_file(users, file_path):
    """ Save user information to the csv file """
    dataframe = pandas.DataFrame([asdict(x) for x in users])
    dataframe.to_csv(file_path, index=False)
    print(f"User information is written to {file_path}")


if __name__ == "__main__":
    args = parse_arguments()
    users = load_data(args)

    if args.group:
        file_name = f"all_{args.group}.csv"
    elif args.duplicate:
        file_name = "duplicate.csv"
    else:
        file_name = "all_users.csv"
    save_file(users, file_name)