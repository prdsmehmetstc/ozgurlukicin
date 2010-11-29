#!/usr/bin/python
# -*- coding: utf-8 -*-

# important command: sed -i "s|op_podcast|oi_podcast|g" oi_podcast.log

import re

LOGPODCAST = "oi_podcast.log"
LOGEDERGI = "edergi.log"
EPISODELISTPODCAST = range(1, 18)
EPISODELISTEDERGI = range(1, 23)


def get_amount_list(log_file, regex):
    log_list = file(log_file).readlines()
    amount_list = []

    for line in log_list:
        m = re.search(regex, line)
        try:
            amount_list.append(m.group())
        except:
            # Example:
            #    78.174.192.97 - - [03/Apr/2010:19:55:49 +0300] "GET /media/podcasts/oi_podcast_E0/.ogg HTTP/1.1" 404 196
            #    78.174.241.181 - - [10/Apr/2010:19:13:30 +0300] "GET /media/podcasts/oi_podcast_E0*.ogg HTTP/1.1" 404 198
            pass

    return amount_list


def print_output():
    regex_podcast = '(?<=oi_podcast_E)\w+.(mp3|ogg)'
    regex_edergi = '(?<=oi_say)\w+_(buyuk|kucuk).pdf'

    # podcasts
    amount_list = get_amount_list(LOGPODCAST, regex_podcast)
    for episode in EPISODELISTPODCAST:
        if episode < 10: # dirty hacking
            episode = "0%s" % episode
        amount_ogg = amount_list.count('%s.ogg' % episode)
        amount_mp3 = amount_list.count('%s.mp3' % episode)

        print("podcast %s (toplam: %s)" % (episode, (amount_ogg + amount_mp3)))
        print("    ogg: %s" % amount_ogg)
        print("    mp3: %s\n" % amount_mp3)

    # edergis
    amount_list = get_amount_list(LOGEDERGI, regex_edergi)
    for episode in EPISODELISTEDERGI:
        if episode < 10: # still dirty hacking
            episode = "0%s" % episode
        amount_buyuk = amount_list.count('%s_buyuk.pdf' % episode)
        amount_kucuk = amount_list.count('%s_kucuk.pdf' % episode)

        print("edergi %s (toplam: %s)" % (episode, (amount_buyuk + amount_kucuk)))
        print("    buyuk: %s" % amount_buyuk)
        print("    küçük: %s\n" % amount_kucuk)


if __name__ == "__main__":
    print_output()
