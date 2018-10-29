#coding=utf-8
import os
import lineTool


def SendLineNotify(title,log):
    token = "FYlIk2GRllkEfh5M9FbiztML7YJAEbmfW7yu0RgghIu"
    msg = title+"\n---------------------\n"+log
    lineTool.lineNotify(token, msg)

