from argparse import ArgumentParser
from tw_shopee_coin import runBot

parser = ArgumentParser()
parser.add_argument(
    "-u", "--username", dest="username", help="Login username", metavar="STRING"
)
parser.add_argument(
    "-p", "--password", dest="password", help="Login password", metavar="STRING"
)
parser.add_argument(
    "-t", "--ghtoken", dest="GH_TOKEN", help="GH_TOKEN", metavar="STRING"
)

parser.add_argument(
    "-cp", "--cookiepath", dest="cookiepath", help="cookie path", metavar="STRING"
)

parser.add_argument(
    "-wd", "--webdriver", dest="webdriver", help="webdriver", metavar="STRING"
)

parser.add_argument(
    "-rp", "--remoteip", dest="remoteip", help="remote ip", metavar="STRING"
)

args = parser.parse_args()

if __name__ == "__main__":
    print("result %s" % runBot(args))
