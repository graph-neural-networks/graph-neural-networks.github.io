# pylint: disable=global-statement,redefined-outer-name
""" Module to wrap AWS Cognito APIs """
import json
import sys
from dataclasses import dataclass

import boto3


@dataclass(frozen=True)
class CognitoGroup:
    """ Class for AWS Cognito group """

    name: str
    description: str


@dataclass(frozen=True)
class CognitoUser:
    """ Class for AWS Cognito user """

    username: str
    email: str
    custom_name: str = ""
    user_status: str = ""
    email_verified: str = ""
    enabled: bool = True

    def name(self) -> str:
        """ Generate the name field """
        return self.custom_name or self.email


def __convert_aws_user__(aws_user):
    email: str = ""
    custom_name: str = ""
    email_verified: str = ""
    enabled = aws_user["Enabled"]
    username = aws_user["Username"]
    user_status = aws_user["UserStatus"]
    for attr in aws_user["Attributes"]:
        if attr["Name"] == "email":
            email = attr["Value"]
        elif attr["Name"] == "custom:name":
            custom_name = attr["Value"]
        elif attr["Name"] == "email_verified":
            email_verified = attr["Value"]

    user = CognitoUser(
        username=username,
        email=email,
        custom_name=custom_name,
        enabled=enabled,
        email_verified=email_verified,
        user_status=user_status,
    )
    return user


def add_to_group(client, profile, user, group_name):
    """ Adds the specified user to the specified group """
    try:
        response = client.admin_add_user_to_group(
            UserPoolId=profile["user_pool_id"],
            Username=user.email,
            GroupName=group_name,
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"User {user.email} added to group {group_name}")
        return response
    except client.exceptions.UserNotFoundException as error:
        print(f"User {user.email} does not exist")
        return error.response
    except client.exceptions.ResourceNotFoundException as error:
        print(f"Group {group_name} does not exist")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to add user {user.email} to group {group_name}")
        return error.response


def create_user(client, profile, user, resend=False):
    """ Creates a new user in the specified user pool """
    try:
        if resend:
            # Resend confirmation email for get back password
            response = client.admin_create_user(
                UserPoolId=profile["user_pool_id"],
                Username=user.email,
                MessageAction="RESEND",
            )
        else:
            response = client.admin_create_user(
                UserPoolId=profile["user_pool_id"],
                Username=user.email,
                UserAttributes=[
                    {"Name": "email", "Value": user.email},
                    {"Name": "email_verified", "Value": "true"},
                ],
            )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            if resend:
                print(f"Resend confirmation to user {user.email} successfully")
            else:
                print(f"User {user.email} was created successfully")
        return response
    except client.exceptions.UsernameExistsException as error:
        print(f"User {user.email} exists")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to create user {user.email}: {error.response}")
        return error.response


def delete_user(client, profile, user):
    """ Deletes a user from the pool """
    try:
        response = client.admin_delete_user(
            UserPoolId=profile["user_pool_id"], Username=user.email
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"User {user.email} was deleted successfully")
        return response
    except client.exceptions.UserNotFoundException as error:
        print(f"User {user.email} does not exist")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to delete user {user.email}")
        return error.response


def disable_user(client, profile, user):
    """ Disables the specified user """
    try:
        response = client.admin_disable_user(
            UserPoolId=profile["user_pool_id"], Username=user.email
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"User {user.email} was disabled successfully")
        return response
    except client.exceptions.UserNotFoundException as error:
        print(f"User {user.email} does not exist")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to disable user {user.email}")
        return error.response


def enable_user(client, profile, user):
    """ Enables the specified user """
    try:
        response = client.admin_enable_user(
            UserPoolId=profile["user_pool_id"], Username=user.email
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"User {user.email} was enabled successfully")
        return response
    except client.exceptions.UserNotFoundException as error:
        print(f"User {user.email} does not exist")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to disable user {user.email}")
        return error.response


def init_client(profile):
    client = boto3.client(
        "cognito-idp",
        aws_access_key_id=profile["access_key_id"],
        aws_secret_access_key=profile["secret_access_key"],
        region_name=profile["region_name"],
    )
    return client


def list_group_users(client, profile, group_name, token=""):
    """ Lists all user from the specified group """
    result = []
    try:
        if token:
            response = client.list_users_in_group(
                UserPoolId=profile["user_pool_id"],
                GroupName=group_name,
                NextToken=token,
            )
        else:
            response = client.list_users_in_group(
                UserPoolId=profile["user_pool_id"], GroupName=group_name,
            )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            aws_users = response["Users"]
            for aws_user in aws_users:
                result.append(__convert_aws_user__(aws_user))
            next_token = response.get("NextToken")
            if next_token:
                more = list_group_users(client, profile, group_name, next_token)
                result.extend(more)
    except client.exceptions.ResourceNotFoundException:
        print(f"Group {group_name} does not exist")
        sys.exit(2)
    except client.exceptions.ClientError as error:
        print(error.response)
        print("Fail to list groups")
        sys.exit(2)

    return result


def list_groups(client, profile):
    """ List existing groups from the pool """
    result = []
    try:
        response = client.list_groups(UserPoolId=profile["user_pool_id"])
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            groups = response["Groups"]
            for group in groups:
                result.append(
                    CognitoGroup(
                        name=group["GroupName"], description=group["Description"]
                    )
                )
    except client.exceptions.ClientError as error:
        print("Fail to list groups")
        print(error.response)
        sys.exit(2)

    return result


def list_users(client, profile, token=""):
    """ Lists all users from the pool """
    result = []
    try:
        if token:
            response = client.list_users(
                UserPoolId=profile["user_pool_id"], PaginationToken=token,
            )
        else:
            response = client.list_users(UserPoolId=profile["user_pool_id"],)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            aws_users = response["Users"]
            for aws_user in aws_users:
                result.append(__convert_aws_user__(aws_user))
            next_token = response.get("PaginationToken")
            if next_token:
                more = list_users(client, profile, next_token)
                result.extend(more)

    except client.exceptions.ClientError as error:
        print("Fail to list users")
        print(error)
        sys.exit(2)

    return result


def remove_from_group(client, profile, user, group_name):
    """ Removes the specified user from the specified group """
    try:
        response = client.admin_remove_user_from_group(
            UserPoolId=profile["user_pool_id"],
            Username=user.email,
            GroupName=group_name,
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"User {user.email} removed from the group {group_name}")
        return response
    except client.exceptions.UserNotFoundException as error:
        print(f"User {user.email} does not exist")
        return error.response
    except client.exceptions.ResourceNotFoundException as error:
        print(f"Group {group_name} does not exist")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to remove user {user.email} from group {group_name}")
        return error.response


def reset_user_password(client, profile, user):
    """ Resets the specified user's password """
    try:
        response = set_user_password(client, profile, user)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            # Resend confirmation
            response = create_user(client, profile, user, True)
            print(f"Password of user {user.email} was reset successfully")
        return response
    except client.exceptions.ClientError as error:
        print(f"Fail to reset password of user {user.email}")
        return error.response


def set_user_password(client, profile, user, password="N0t-permanent!"):
    """ Sets the specified user's password """
    try:
        response = client.admin_set_user_password(
            UserPoolId=profile["user_pool_id"],
            Username=user.email,
            Password=password,
            Permanent=False,
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"Password of user {user.email} was set successfully")
        return response
    except client.exceptions.UserNotFoundException as error:
        print(f"User {user.email} does not exist")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to reset password of user {user.email}")
        return error.response


def show_error_response(response, is_show=False):
    """ Show error message if any """
    if is_show:
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            # json_string = json.dumps(response, indent=4)
            json_string = json.dumps(response.get("Error"), indent=4)
            print(json_string)


def update_user_attributes(client, profile, user, attr_name, attr_value):
    """ Updates the specified user's attribute """
    try:
        response = client.admin_update_user_attributes(
            UserPoolId=profile["user_pool_id"],
            Username=user.email,
            UserAttributes=[{"Name": attr_name, "Value": attr_value}],
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"User {user.email} was updated successfully")
        return response
    except client.exceptions.UserNotFoundException as error:
        print(f"User {user.email} does not exist")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to disable user {user.email}")
        return error.response