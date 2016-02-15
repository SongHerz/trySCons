#!/usr/bin/env python

import StringIO


def text_box(msg, border='#'):
    """
    Return a string which is a text box.
    """
    assert isinstance(border, str) and len(border) == 1
    msg_line = '{} {} {}'.format(border, msg, border)
    top_bot_line = border * len(msg_line)

    sio = StringIO.StringIO()
    print >> sio, top_bot_line
    print >> sio, msg_line
    print >> sio, top_bot_line
    return sio.getvalue()
