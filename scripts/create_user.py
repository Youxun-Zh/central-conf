import argparse
import os
import sys

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PARDIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PARDIR)

from libs.mysql_client import MysqlClient
from utils.helper import create_user

m_client = MysqlClient(using=False)


def main(email, nickname, password, role):
    data, no = create_user(email, nickname, password, role)

    msg = "success"
    if not no:
        msg = "failure"
    print(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The user")
    parser.add_argument("--email", type=str, help="the user's email", required=True)
    parser.add_argument("--nickname", type=str, help="the user's nickname", required=True)
    parser.add_argument("--password", type=str, help="the user's password", required=True)
    parser.add_argument("--role", type=str, help="the user's role (1 superadmin, 2 admin, 3 member)", required=True)
    args = parser.parse_args()

    email, nickname, password, role = [getattr(args, attr) for attr in ("email", "nickname", "password", "role")]
    main(email, nickname, password, role)