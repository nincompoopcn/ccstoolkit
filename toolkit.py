#!/usr/bin/python
# -*- coding: utf-8 -*-

import webchat
import arguments

def main():
    webchat.create_opener()

    args = arguments.extract()

    arguments.action(args)

    return

if __name__ == "__main__":
    main()
