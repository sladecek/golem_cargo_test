"""Argument parser."""
import argparse


def build_parser(description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--subnet-tag", default="community.3", help="Subnet name; default: %(default)s")
    parser.add_argument("--log-file", default=None, help="Log file for YAPAPI; default: %(default)s")
    parser.add_argument("--time-out", default=30, type=int, help="Overall timeout in minutes; default: %(default)d")
    parser.add_argument("--plan", default=300, help="Planned runtime in seconds; default: %(default)d")
    parser.add_argument("--test-avg", default=60, help="Expected average runtime for one new test; default: %(default)d")
    return parser
