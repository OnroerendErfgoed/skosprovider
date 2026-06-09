import re

import responses


def init_responses():
    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES",
        body='{"notes": [], "labels": [], "uri": "urn:x-vioe:styles", "label": null, "id": "STYLES", "subject": [], "sources": [], "languages": []}',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES/c/1",
        body='{"subordinate_arrays": [], "matches": {}, "labels": [{"type": "prefLabel", "language": "nl", "label": "traditioneel"}, {"type": "altLabel", "language": "nl", "label": "bak- en zandsteenstijl"}, {"type": "altLabel", "language": "nl", "label": "Maasstijl"}], "narrower": [{"labels": [{"type": "prefLabel", "language": "nl", "label": "vakwerkbouw"}], "label": "vakwerkbouw", "type": "concept", "id": 2, "uri": "urn:x-vioe:styles:2"}], "related": [], "broader": [], "id": 1, "member_of": [{"labels": [{"type": "prefLabel", "language": "nl", "label": "stijlen"}], "label": "stijlen", "type": "collection", "id": 60, "uri": "urn:x-vioe:styles:60"}], "notes": [], "uri": "urn:x-vioe:styles:1", "label": "traditioneel", "type": "concept"}',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES/c/1/",
        body='{"subordinate_arrays": [], "matches": {}, "labels": [{"type": "prefLabel", "language": "nl", "label": "traditioneel"}, {"type": "altLabel", "language": "nl", "label": "bak- en zandsteenstijl"}, {"type": "altLabel", "language": "nl", "label": "Maasstijl"}], "narrower": [{"labels": [{"type": "prefLabel", "language": "nl", "label": "vakwerkbouw"}], "label": "vakwerkbouw", "type": "concept", "id": 2, "uri": "urn:x-vioe:styles:2"}], "related": [], "broader": [], "id": 1, "member_of": [{"labels": [{"type": "prefLabel", "language": "nl", "label": "stijlen"}], "label": "stijlen", "type": "collection", "id": 60, "uri": "urn:x-vioe:styles:60"}], "notes": [], "uri": "urn:x-vioe:styles:1", "label": "traditioneel", "type": "concept"}',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES/c/123",
        body='{"message": "The resource could not be found."}',
        status=404,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES/c/?type=concept&label=mod&language=en",
        match_querystring=True,
        body='[{"label": "modernisme", "type": "concept", "id": 23, "uri": "urn:x-vioe:styles:23"}, {"label": "postmodernisme", "type": "concept", "id": 26, "uri": "urn:x-vioe:styles:26"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES/c/?type=collection&language=en&sort=id",
        match_querystring=True,
        body='[{"label": "Stijlen en culturen", "type": "collection", "id": 0, "uri": "urn:x-vioe:styles:0"}, {"label": "stijlen", "type": "collection", "id": 60, "uri": "urn:x-vioe:styles:60"}, {"label": "culturen", "type": "collection", "id": 61, "uri": "urn:x-vioe:styles:61"}, {"label": "culturen uit de steentijd", "type": "collection", "id": 62, "uri": "urn:x-vioe:styles:62"}, {"label": "culturen uit de metaaltijden", "type": "collection", "id": 63, "uri": "urn:x-vioe:styles:63"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES/c/?type=collection&language=en&sort=-id",
        match_querystring=True,
        body='[{"label": "culturen uit de metaaltijden", "type": "collection", "id": 63, "uri": "urn:x-vioe:styles:63"}, {"label": "culturen uit de steentijd", "type": "collection", "id": 62, "uri": "urn:x-vioe:styles:62"}, {"label": "culturen", "type": "collection", "id": 61, "uri": "urn:x-vioe:styles:61"}, {"label": "stijlen", "type": "collection", "id": 60, "uri": "urn:x-vioe:styles:60"}, {"label": "Stijlen en culturen", "type": "collection", "id": 0, "uri": "urn:x-vioe:styles:0"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES/c/",
        body='[{"label": "acheuleaan", "type": "concept", "id": 64, "uri": "urn:x-vioe:styles:64"}, {"label": "ahrensburgiaan", "type": "concept", "id": 65, "uri": "urn:x-vioe:styles:65"}, {"label": "art deco", "type": "concept", "id": 22, "uri": "urn:x-vioe:styles:22"}, {"label": "art nouveau", "type": "concept", "id": 30, "uri": "urn:x-vioe:styles:30"}, {"label": "aurignaciaan", "type": "concept", "id": 66, "uri": "urn:x-vioe:styles:66"}, {"label": "barok", "type": "concept", "id": 7, "uri": "urn:x-vioe:styles:7"}, {"label": "beaux-artsstijl", "type": "concept", "id": 32, "uri": "urn:x-vioe:styles:32"}, {"label": "brutalisme", "type": "concept", "id": 28, "uri": "urn:x-vioe:styles:28"}, {"label": "classicerende barok", "type": "concept", "id": 8, "uri": "urn:x-vioe:styles:8"}, {"label": "classicisme", "type": "concept", "id": 10, "uri": "urn:x-vioe:styles:10"}, {"label": "cottagestijl", "type": "concept", "id": 31, "uri": "urn:x-vioe:styles:31"}, {"label": "creswelliaan", "type": "concept", "id": 67, "uri": "urn:x-vioe:styles:67"}, {"label": "culturen", "type": "collection", "id": 61, "uri": "urn:x-vioe:styles:61"}, {"label": "culturen uit de metaaltijden", "type": "collection", "id": 63, "uri": "urn:x-vioe:styles:63"}, {"label": "culturen uit de steentijd", "type": "collection", "id": 62, "uri": "urn:x-vioe:styles:62"}, {"label": "eclecticisme", "type": "concept", "id": 29, "uri": "urn:x-vioe:styles:29"}, {"label": "empire", "type": "concept", "id": 11, "uri": "urn:x-vioe:styles:11"}, {"label": "enkelgrafcultuur", "type": "concept", "id": 68, "uri": "urn:x-vioe:styles:68"}, {"label": "expo-stijl", "type": "concept", "id": 24, "uri": "urn:x-vioe:styles:24"}, {"label": "federmesser", "type": "concept", "id": 69, "uri": "urn:x-vioe:styles:69"}, {"label": "gotiek", "type": "concept", "id": 4, "uri": "urn:x-vioe:styles:4"}, {"label": "gravettiaan", "type": "concept", "id": 82, "uri": "urn:x-vioe:styles:82"}, {"label": "groupe de Blicquy", "type": "concept", "id": 87, "uri": "urn:x-vioe:styles:87"}, {"label": "Halstatt", "type": "concept", "id": 114, "uri": "urn:x-vioe:styles:114"}, {"label": "hamburgiaan", "type": "concept", "id": 88, "uri": "urn:x-vioe:styles:88"}, {"label": "hazendonkgroep", "type": "concept", "id": 89, "uri": "urn:x-vioe:styles:89"}, {"label": "high tech", "type": "concept", "id": 27, "uri": "urn:x-vioe:styles:27"}, {"label": "Hilversum-cultuur", "type": "concept", "id": 115, "uri": "urn:x-vioe:styles:115"}, {"label": "klokbekercultuur", "type": "concept", "id": 91, "uri": "urn:x-vioe:styles:91"}, {"label": "La Tène", "type": "concept", "id": 116, "uri": "urn:x-vioe:styles:116"}, {"label": "lineaire bandkeramiek", "type": "concept", "id": 93, "uri": "urn:x-vioe:styles:93"}, {"label": "magdaleniaan", "type": "concept", "id": 95, "uri": "urn:x-vioe:styles:95"}, {"label": "michelsbergcultuur", "type": "concept", "id": 97, "uri": "urn:x-vioe:styles:97"}, {"label": "micoquiaan", "type": "concept", "id": 98, "uri": "urn:x-vioe:styles:98"}, {"label": "modernisme", "type": "concept", "id": 23, "uri": "urn:x-vioe:styles:23"}, {"label": "mousteriaan", "type": "concept", "id": 100, "uri": "urn:x-vioe:styles:100"}, {"label": "Nederrijnse grafheuvelcultuur", "type": "concept", "id": 117, "uri": "urn:x-vioe:styles:117"}, {"label": "neo-Egyptisch", "type": "concept", "id": 34, "uri": "urn:x-vioe:styles:34"}, {"label": "neo-empire", "type": "concept", "id": 33, "uri": "urn:x-vioe:styles:33"}, {"label": "neobarok", "type": "concept", "id": 16, "uri": "urn:x-vioe:styles:16"}, {"label": "neobyzantijns", "type": "concept", "id": 18, "uri": "urn:x-vioe:styles:18"}, {"label": "neoclassicisme", "type": "concept", "id": 12, "uri": "urn:x-vioe:styles:12"}, {"label": "neogotiek", "type": "concept", "id": 13, "uri": "urn:x-vioe:styles:13"}, {"label": "neomoors", "type": "concept", "id": 17, "uri": "urn:x-vioe:styles:17"}, {"label": "neorenaissance", "type": "concept", "id": 14, "uri": "urn:x-vioe:styles:14"}, {"label": "neorococo", "type": "concept", "id": 19, "uri": "urn:x-vioe:styles:19"}, {"label": "neoromaans", "type": "concept", "id": 15, "uri": "urn:x-vioe:styles:15"}, {"label": "neostijl", "type": "concept", "id": 35, "uri": "urn:x-vioe:styles:35"}, {"label": "neotraditioneel", "type": "concept", "id": 21, "uri": "urn:x-vioe:styles:21"}, {"label": "organische architectuur", "type": "concept", "id": 25, "uri": "urn:x-vioe:styles:25"}, {"label": "Plainseaucultuur", "type": "concept", "id": 119, "uri": "urn:x-vioe:styles:119"}, {"label": "postmodernisme", "type": "concept", "id": 26, "uri": "urn:x-vioe:styles:26"}, {"label": "regionalisme", "type": "concept", "id": 20, "uri": "urn:x-vioe:styles:20"}, {"label": "renaissance", "type": "concept", "id": 5, "uri": "urn:x-vioe:styles:5"}, {"label": "Rhin-Suisse-France Oriental", "type": "concept", "id": 120, "uri": "urn:x-vioe:styles:120"}, {"label": "Rijnbekkengroep", "type": "concept", "id": 102, "uri": "urn:x-vioe:styles:102"}, {"label": "rococo", "type": "concept", "id": 9, "uri": "urn:x-vioe:styles:9"}, {"label": "romaans", "type": "concept", "id": 3, "uri": "urn:x-vioe:styles:3"}, {"label": "rössencultuur", "type": "concept", "id": 104, "uri": "urn:x-vioe:styles:104"}, {"label": "second empire", "type": "concept", "id": 36, "uri": "urn:x-vioe:styles:36"}, {"label": "Seine-Oise-Marne", "type": "concept", "id": 106, "uri": "urn:x-vioe:styles:106"}, {"label": "steingroep", "type": "concept", "id": 108, "uri": "urn:x-vioe:styles:108"}, {"label": "stijlen", "type": "collection", "id": 60, "uri": "urn:x-vioe:styles:60"}, {"label": "Stijlen en culturen", "type": "collection", "id": 0, "uri": "urn:x-vioe:styles:0"}, {"label": "swifterbantcultuur", "type": "concept", "id": 109, "uri": "urn:x-vioe:styles:109"}, {"label": "tardenoisiaan", "type": "concept", "id": 110, "uri": "urn:x-vioe:styles:110"}, {"label": "traditioneel", "type": "concept", "id": 1, "uri": "urn:x-vioe:styles:1"}, {"label": "trechterbekercultuur", "type": "concept", "id": 112, "uri": "urn:x-vioe:styles:112"}, {"label": "urnenveldencultuur", "type": "concept", "id": 121, "uri": "urn:x-vioe:styles:121"}, {"label": "vakwerkbouw", "type": "concept", "id": 2, "uri": "urn:x-vioe:styles:2"}, {"label": "vlaardingencultuur", "type": "concept", "id": 113, "uri": "urn:x-vioe:styles:113"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES/displaytop",
        body='[{"label": "Stijlen en culturen", "type": "collection", "id": 0, "uri": "urn:x-vioe:styles:0"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES/topconcepts",
        body='[{"label": "acheuleaan", "type": "concept", "id": 64, "uri": "urn:x-vioe:styles:64"}, {"label": "ahrensburgiaan", "type": "concept", "id": 65, "uri": "urn:x-vioe:styles:65"}, {"label": "art deco", "type": "concept", "id": 22, "uri": "urn:x-vioe:styles:22"}, {"label": "art nouveau", "type": "concept", "id": 30, "uri": "urn:x-vioe:styles:30"}, {"label": "aurignaciaan", "type": "concept", "id": 66, "uri": "urn:x-vioe:styles:66"}, {"label": "barok", "type": "concept", "id": 7, "uri": "urn:x-vioe:styles:7"}, {"label": "brutalisme", "type": "concept", "id": 28, "uri": "urn:x-vioe:styles:28"}, {"label": "classicerende barok", "type": "concept", "id": 8, "uri": "urn:x-vioe:styles:8"}, {"label": "classicisme", "type": "concept", "id": 10, "uri": "urn:x-vioe:styles:10"}, {"label": "cottagestijl", "type": "concept", "id": 31, "uri": "urn:x-vioe:styles:31"}, {"label": "creswelliaan", "type": "concept", "id": 67, "uri": "urn:x-vioe:styles:67"}, {"label": "empire", "type": "concept", "id": 11, "uri": "urn:x-vioe:styles:11"}, {"label": "enkelgrafcultuur", "type": "concept", "id": 68, "uri": "urn:x-vioe:styles:68"}, {"label": "federmesser", "type": "concept", "id": 69, "uri": "urn:x-vioe:styles:69"}, {"label": "gotiek", "type": "concept", "id": 4, "uri": "urn:x-vioe:styles:4"}, {"label": "gravettiaan", "type": "concept", "id": 82, "uri": "urn:x-vioe:styles:82"}, {"label": "groupe de Blicquy", "type": "concept", "id": 87, "uri": "urn:x-vioe:styles:87"}, {"label": "Halstatt", "type": "concept", "id": 114, "uri": "urn:x-vioe:styles:114"}, {"label": "hamburgiaan", "type": "concept", "id": 88, "uri": "urn:x-vioe:styles:88"}, {"label": "hazendonkgroep", "type": "concept", "id": 89, "uri": "urn:x-vioe:styles:89"}, {"label": "high tech", "type": "concept", "id": 27, "uri": "urn:x-vioe:styles:27"}, {"label": "Hilversum-cultuur", "type": "concept", "id": 115, "uri": "urn:x-vioe:styles:115"}, {"label": "klokbekercultuur", "type": "concept", "id": 91, "uri": "urn:x-vioe:styles:91"}, {"label": "La Tène", "type": "concept", "id": 116, "uri": "urn:x-vioe:styles:116"}, {"label": "lineaire bandkeramiek", "type": "concept", "id": 93, "uri": "urn:x-vioe:styles:93"}, {"label": "magdaleniaan", "type": "concept", "id": 95, "uri": "urn:x-vioe:styles:95"}, {"label": "michelsbergcultuur", "type": "concept", "id": 97, "uri": "urn:x-vioe:styles:97"}, {"label": "micoquiaan", "type": "concept", "id": 98, "uri": "urn:x-vioe:styles:98"}, {"label": "modernisme", "type": "concept", "id": 23, "uri": "urn:x-vioe:styles:23"}, {"label": "mousteriaan", "type": "concept", "id": 100, "uri": "urn:x-vioe:styles:100"}, {"label": "Nederrijnse grafheuvelcultuur", "type": "concept", "id": 117, "uri": "urn:x-vioe:styles:117"}, {"label": "neostijl", "type": "concept", "id": 35, "uri": "urn:x-vioe:styles:35"}, {"label": "neotraditioneel", "type": "concept", "id": 21, "uri": "urn:x-vioe:styles:21"}, {"label": "organische architectuur", "type": "concept", "id": 25, "uri": "urn:x-vioe:styles:25"}, {"label": "Plainseaucultuur", "type": "concept", "id": 119, "uri": "urn:x-vioe:styles:119"}, {"label": "postmodernisme", "type": "concept", "id": 26, "uri": "urn:x-vioe:styles:26"}, {"label": "regionalisme", "type": "concept", "id": 20, "uri": "urn:x-vioe:styles:20"}, {"label": "renaissance", "type": "concept", "id": 5, "uri": "urn:x-vioe:styles:5"}, {"label": "Rhin-Suisse-France Oriental", "type": "concept", "id": 120, "uri": "urn:x-vioe:styles:120"}, {"label": "Rijnbekkengroep", "type": "concept", "id": 102, "uri": "urn:x-vioe:styles:102"}, {"label": "rococo", "type": "concept", "id": 9, "uri": "urn:x-vioe:styles:9"}, {"label": "romaans", "type": "concept", "id": 3, "uri": "urn:x-vioe:styles:3"}, {"label": "rössencultuur", "type": "concept", "id": 104, "uri": "urn:x-vioe:styles:104"}, {"label": "Seine-Oise-Marne", "type": "concept", "id": 106, "uri": "urn:x-vioe:styles:106"}, {"label": "steingroep", "type": "concept", "id": 108, "uri": "urn:x-vioe:styles:108"}, {"label": "swifterbantcultuur", "type": "concept", "id": 109, "uri": "urn:x-vioe:styles:109"}, {"label": "tardenoisiaan", "type": "concept", "id": 110, "uri": "urn:x-vioe:styles:110"}, {"label": "traditioneel", "type": "concept", "id": 1, "uri": "urn:x-vioe:styles:1"}, {"label": "trechterbekercultuur", "type": "concept", "id": 112, "uri": "urn:x-vioe:styles:112"}, {"label": "urnenveldencultuur", "type": "concept", "id": 121, "uri": "urn:x-vioe:styles:121"}, {"label": "vlaardingencultuur", "type": "concept", "id": 113, "uri": "urn:x-vioe:styles:113"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/TREES/topconcepts",
        body='{"message": "The resource could not be found."}',
        status=404,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/MATERIALS/c/",
        body='[{"label": "aardewerk", "type": "concept", "id": 1, "uri": "urn:x-vioe:materials:1"}, {"label": "aluminium", "type": "concept", "id": 48, "uri": "urn:x-vioe:materials:48"}, {"label": "amber", "type": "concept", "id": 33, "uri": "urn:x-vioe:materials:33"}, {"label": "concrete", "type": "concept", "id": 38, "uri": "urn:x-vioe:materials:38"}, {"label": "bladgoud", "type": "concept", "id": 10, "uri": "urn:x-vioe:materials:10"}, {"label": "fur", "type": "concept", "id": 23, "uri": "urn:x-vioe:materials:23"}, {"label": "botmateriaal", "type": "concept", "id": 24, "uri": "urn:x-vioe:materials:24"}, {"label": "bronze", "type": "concept", "id": 14, "uri": "urn:x-vioe:materials:14"}, {"label": "cement", "type": "concept", "id": 49, "uri": "urn:x-vioe:materials:49"}, {"label": "dierlijk botmateriaal", "type": "concept", "id": 25, "uri": "urn:x-vioe:materials:25"}, {"label": "reinforced concrete", "type": "concept", "id": 39, "uri": "urn:x-vioe:materials:39"}, {"label": "gewei", "type": "concept", "id": 27, "uri": "urn:x-vioe:materials:27"}, {"label": "glas", "type": "concept", "id": 7, "uri": "urn:x-vioe:materials:7"}, {"label": "gold", "type": "concept", "id": 9, "uri": "urn:x-vioe:materials:9"}, {"label": "hoorn/hoornpitten", "type": "concept", "id": 28, "uri": "urn:x-vioe:materials:28"}, {"label": "hout", "type": "concept", "id": 35, "uri": "urn:x-vioe:materials:35"}, {"label": "houtskool", "type": "concept", "id": 36, "uri": "urn:x-vioe:materials:36"}, {"label": "huid", "type": "concept", "id": 29, "uri": "urn:x-vioe:materials:29"}, {"label": "ijzer", "type": "concept", "id": 11, "uri": "urn:x-vioe:materials:11"}, {"label": "koper", "type": "concept", "id": 12, "uri": "urn:x-vioe:materials:12"}, {"label": "koperlegeringen", "type": "concept", "id": 13, "uri": "urn:x-vioe:materials:13"}, {"label": "kunststof", "type": "concept", "id": 20, "uri": "urn:x-vioe:materials:20"}, {"label": "kwartsiet van Tienen", "type": "concept", "id": 44, "uri": "urn:x-vioe:materials:44"}, {"label": "kwartsitisch lithisch materiaal", "type": "concept", "id": 43, "uri": "urn:x-vioe:materials:43"}, {"label": "leer", "type": "concept", "id": 30, "uri": "urn:x-vioe:materials:30"}, {"label": "lithisch materiaal", "type": "concept", "id": 42, "uri": "urn:x-vioe:materials:42"}, {"label": "lood", "type": "concept", "id": 16, "uri": "urn:x-vioe:materials:16"}, {"label": "Materiaal", "type": "collection", "id": 0, "uri": "urn:x-vioe:materials:0"}, {"label": "menselijk botmateriaal", "type": "concept", "id": 26, "uri": "urn:x-vioe:materials:26"}, {"label": "messing", "type": "concept", "id": 15, "uri": "urn:x-vioe:materials:15"}, {"label": "metaal", "type": "concept", "id": 8, "uri": "urn:x-vioe:materials:8"}, {"label": "natuursteen", "type": "concept", "id": 41, "uri": "urn:x-vioe:materials:41"}, {"label": "organisch materiaal", "type": "concept", "id": 21, "uri": "urn:x-vioe:materials:21"}, {"label": "pijpaarde", "type": "concept", "id": 2, "uri": "urn:x-vioe:materials:2"}, {"label": "plantaardig materiaal", "type": "concept", "id": 32, "uri": "urn:x-vioe:materials:32"}, {"label": "pleister", "type": "concept", "id": 50, "uri": "urn:x-vioe:materials:50"}, {"label": "porselein", "type": "concept", "id": 5, "uri": "urn:x-vioe:materials:5"}, {"label": "schelp", "type": "concept", "id": 31, "uri": "urn:x-vioe:materials:31"}, {"label": "silex", "type": "concept", "id": 46, "uri": "urn:x-vioe:materials:46"}, {"label": "staal", "type": "concept", "id": 17, "uri": "urn:x-vioe:materials:17"}, {"label": "steen", "type": "concept", "id": 40, "uri": "urn:x-vioe:materials:40"}, {"label": "steengoed", "type": "concept", "id": 6, "uri": "urn:x-vioe:materials:6"}, {"label": "textiel", "type": "concept", "id": 37, "uri": "urn:x-vioe:materials:37"}, {"label": "tin", "type": "concept", "id": 18, "uri": "urn:x-vioe:materials:18"}, {"label": "grès quartzite de Wommersom", "type": "concept", "id": 45, "uri": "urn:x-vioe:materials:45"}, {"label": "silver", "type": "concept", "id": 19, "uri": "urn:x-vioe:materials:19"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/MATERIALS/c/?type=all",
        match_querystring=True,
        body='[{"label": "aardewerk", "type": "concept", "id": 1, "uri": "urn:x-vioe:materials:1"}, {"label": "aluminium", "type": "concept", "id": 48, "uri": "urn:x-vioe:materials:48"}, {"label": "amber", "type": "concept", "id": 33, "uri": "urn:x-vioe:materials:33"}, {"label": "concrete", "type": "concept", "id": 38, "uri": "urn:x-vioe:materials:38"}, {"label": "bladgoud", "type": "concept", "id": 10, "uri": "urn:x-vioe:materials:10"}, {"label": "fur", "type": "concept", "id": 23, "uri": "urn:x-vioe:materials:23"}, {"label": "botmateriaal", "type": "concept", "id": 24, "uri": "urn:x-vioe:materials:24"}, {"label": "bronze", "type": "concept", "id": 14, "uri": "urn:x-vioe:materials:14"}, {"label": "cement", "type": "concept", "id": 49, "uri": "urn:x-vioe:materials:49"}, {"label": "dierlijk botmateriaal", "type": "concept", "id": 25, "uri": "urn:x-vioe:materials:25"}, {"label": "reinforced concrete", "type": "concept", "id": 39, "uri": "urn:x-vioe:materials:39"}, {"label": "gewei", "type": "concept", "id": 27, "uri": "urn:x-vioe:materials:27"}, {"label": "glas", "type": "concept", "id": 7, "uri": "urn:x-vioe:materials:7"}, {"label": "gold", "type": "concept", "id": 9, "uri": "urn:x-vioe:materials:9"}, {"label": "hoorn/hoornpitten", "type": "concept", "id": 28, "uri": "urn:x-vioe:materials:28"}, {"label": "hout", "type": "concept", "id": 35, "uri": "urn:x-vioe:materials:35"}, {"label": "houtskool", "type": "concept", "id": 36, "uri": "urn:x-vioe:materials:36"}, {"label": "huid", "type": "concept", "id": 29, "uri": "urn:x-vioe:materials:29"}, {"label": "ijzer", "type": "concept", "id": 11, "uri": "urn:x-vioe:materials:11"}, {"label": "koper", "type": "concept", "id": 12, "uri": "urn:x-vioe:materials:12"}, {"label": "koperlegeringen", "type": "concept", "id": 13, "uri": "urn:x-vioe:materials:13"}, {"label": "kunststof", "type": "concept", "id": 20, "uri": "urn:x-vioe:materials:20"}, {"label": "kwartsiet van Tienen", "type": "concept", "id": 44, "uri": "urn:x-vioe:materials:44"}, {"label": "kwartsitisch lithisch materiaal", "type": "concept", "id": 43, "uri": "urn:x-vioe:materials:43"}, {"label": "leer", "type": "concept", "id": 30, "uri": "urn:x-vioe:materials:30"}, {"label": "lithisch materiaal", "type": "concept", "id": 42, "uri": "urn:x-vioe:materials:42"}, {"label": "lood", "type": "concept", "id": 16, "uri": "urn:x-vioe:materials:16"}, {"label": "Materiaal", "type": "collection", "id": 0, "uri": "urn:x-vioe:materials:0"}, {"label": "menselijk botmateriaal", "type": "concept", "id": 26, "uri": "urn:x-vioe:materials:26"}, {"label": "messing", "type": "concept", "id": 15, "uri": "urn:x-vioe:materials:15"}, {"label": "metaal", "type": "concept", "id": 8, "uri": "urn:x-vioe:materials:8"}, {"label": "natuursteen", "type": "concept", "id": 41, "uri": "urn:x-vioe:materials:41"}, {"label": "organisch materiaal", "type": "concept", "id": 21, "uri": "urn:x-vioe:materials:21"}, {"label": "pijpaarde", "type": "concept", "id": 2, "uri": "urn:x-vioe:materials:2"}, {"label": "plantaardig materiaal", "type": "concept", "id": 32, "uri": "urn:x-vioe:materials:32"}, {"label": "pleister", "type": "concept", "id": 50, "uri": "urn:x-vioe:materials:50"}, {"label": "porselein", "type": "concept", "id": 5, "uri": "urn:x-vioe:materials:5"}, {"label": "schelp", "type": "concept", "id": 31, "uri": "urn:x-vioe:materials:31"}, {"label": "silex", "type": "concept", "id": 46, "uri": "urn:x-vioe:materials:46"}, {"label": "staal", "type": "concept", "id": 17, "uri": "urn:x-vioe:materials:17"}, {"label": "steen", "type": "concept", "id": 40, "uri": "urn:x-vioe:materials:40"}, {"label": "steengoed", "type": "concept", "id": 6, "uri": "urn:x-vioe:materials:6"}, {"label": "textiel", "type": "concept", "id": 37, "uri": "urn:x-vioe:materials:37"}, {"label": "tin", "type": "concept", "id": 18, "uri": "urn:x-vioe:materials:18"}, {"label": "grès quartzite de Wommersom", "type": "concept", "id": 45, "uri": "urn:x-vioe:materials:45"}, {"label": "silver", "type": "concept", "id": 19, "uri": "urn:x-vioe:materials:19"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/MATERIALS/c/?type=concept",
        match_querystring=True,
        body='[{"label": "aardewerk", "type": "concept", "id": 1, "uri": "urn:x-vioe:materials:1"}, {"label": "aluminium", "type": "concept", "id": 48, "uri": "urn:x-vioe:materials:48"}, {"label": "amber", "type": "concept", "id": 33, "uri": "urn:x-vioe:materials:33"}, {"label": "concrete", "type": "concept", "id": 38, "uri": "urn:x-vioe:materials:38"}, {"label": "bladgoud", "type": "concept", "id": 10, "uri": "urn:x-vioe:materials:10"}, {"label": "fur", "type": "concept", "id": 23, "uri": "urn:x-vioe:materials:23"}, {"label": "botmateriaal", "type": "concept", "id": 24, "uri": "urn:x-vioe:materials:24"}, {"label": "bronze", "type": "concept", "id": 14, "uri": "urn:x-vioe:materials:14"}, {"label": "cement", "type": "concept", "id": 49, "uri": "urn:x-vioe:materials:49"}, {"label": "dierlijk botmateriaal", "type": "concept", "id": 25, "uri": "urn:x-vioe:materials:25"}, {"label": "reinforced concrete", "type": "concept", "id": 39, "uri": "urn:x-vioe:materials:39"}, {"label": "gewei", "type": "concept", "id": 27, "uri": "urn:x-vioe:materials:27"}, {"label": "glas", "type": "concept", "id": 7, "uri": "urn:x-vioe:materials:7"}, {"label": "gold", "type": "concept", "id": 9, "uri": "urn:x-vioe:materials:9"}, {"label": "hoorn/hoornpitten", "type": "concept", "id": 28, "uri": "urn:x-vioe:materials:28"}, {"label": "hout", "type": "concept", "id": 35, "uri": "urn:x-vioe:materials:35"}, {"label": "houtskool", "type": "concept", "id": 36, "uri": "urn:x-vioe:materials:36"}, {"label": "huid", "type": "concept", "id": 29, "uri": "urn:x-vioe:materials:29"}, {"label": "ijzer", "type": "concept", "id": 11, "uri": "urn:x-vioe:materials:11"}, {"label": "koper", "type": "concept", "id": 12, "uri": "urn:x-vioe:materials:12"}, {"label": "koperlegeringen", "type": "concept", "id": 13, "uri": "urn:x-vioe:materials:13"}, {"label": "kunststof", "type": "concept", "id": 20, "uri": "urn:x-vioe:materials:20"}, {"label": "kwartsiet van Tienen", "type": "concept", "id": 44, "uri": "urn:x-vioe:materials:44"}, {"label": "kwartsitisch lithisch materiaal", "type": "concept", "id": 43, "uri": "urn:x-vioe:materials:43"}, {"label": "leer", "type": "concept", "id": 30, "uri": "urn:x-vioe:materials:30"}, {"label": "lithisch materiaal", "type": "concept", "id": 42, "uri": "urn:x-vioe:materials:42"}, {"label": "lood", "type": "concept", "id": 16, "uri": "urn:x-vioe:materials:16"}, {"label": "menselijk botmateriaal", "type": "concept", "id": 26, "uri": "urn:x-vioe:materials:26"}, {"label": "messing", "type": "concept", "id": 15, "uri": "urn:x-vioe:materials:15"}, {"label": "metaal", "type": "concept", "id": 8, "uri": "urn:x-vioe:materials:8"}, {"label": "natuursteen", "type": "concept", "id": 41, "uri": "urn:x-vioe:materials:41"}, {"label": "organisch materiaal", "type": "concept", "id": 21, "uri": "urn:x-vioe:materials:21"}, {"label": "pijpaarde", "type": "concept", "id": 2, "uri": "urn:x-vioe:materials:2"}, {"label": "plantaardig materiaal", "type": "concept", "id": 32, "uri": "urn:x-vioe:materials:32"}, {"label": "pleister", "type": "concept", "id": 50, "uri": "urn:x-vioe:materials:50"}, {"label": "porselein", "type": "concept", "id": 5, "uri": "urn:x-vioe:materials:5"}, {"label": "schelp", "type": "concept", "id": 31, "uri": "urn:x-vioe:materials:31"}, {"label": "silex", "type": "concept", "id": 46, "uri": "urn:x-vioe:materials:46"}, {"label": "staal", "type": "concept", "id": 17, "uri": "urn:x-vioe:materials:17"}, {"label": "steen", "type": "concept", "id": 40, "uri": "urn:x-vioe:materials:40"}, {"label": "steengoed", "type": "concept", "id": 6, "uri": "urn:x-vioe:materials:6"}, {"label": "textiel", "type": "concept", "id": 37, "uri": "urn:x-vioe:materials:37"}, {"label": "tin", "type": "concept", "id": 18, "uri": "urn:x-vioe:materials:18"}, {"label": "grès quartzite de Wommersom", "type": "concept", "id": 45, "uri": "urn:x-vioe:materials:45"}, {"label": "silver", "type": "concept", "id": 19, "uri": "urn:x-vioe:materials:19"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES/c/1/expand",
        body="[1, 2]",
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/MATERIALS/c/8/expand",
        body="[16, 8, 9, 10, 11, 12, 13, 14, 15, 48, 17, 18, 19]",
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/MATERIALS/c/0/expand",
        body="[1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 48, 49, 50]",
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/TREES/c/3/expand",
        body="[1, 2]",
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES/c/invalid/expand",
        body='{"message": "unexpected server error"}',
        status=500,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES/c/invalid/displaychildren",
        body='{"message": "unexpected server error"}',
        status=500,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/MATERIALS/c/12/displaychildren",
        body='[{"label": "koperlegeringen", "type": "concept", "id": 13, "uri": "urn:x-vioe:materials:13"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/MATERIALS/c/13/displaychildren",
        body='[{"label": "messing", "type": "concept", "id": 15, "uri": "urn:x-vioe:materials:15"}, {"label": "bronze", "type": "concept", "id": 14, "uri": "urn:x-vioe:materials:14"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/MATERIALS/c/8/displaychildren",
        body='[{"label": "koper", "type": "concept", "id": 12, "uri": "urn:x-vioe:materials:12"}, {"label": "staal", "type": "concept", "id": 17, "uri": "urn:x-vioe:materials:17"}, {"label": "ijzer", "type": "concept", "id": 11, "uri": "urn:x-vioe:materials:11"}, {"label": "lood", "type": "concept", "id": 16, "uri": "urn:x-vioe:materials:16"}, {"label": "aluminium", "type": "concept", "id": 48, "uri": "urn:x-vioe:materials:48"}, {"label": "gold", "type": "concept", "id": 9, "uri": "urn:x-vioe:materials:9"}, {"label": "silver", "type": "concept", "id": 19, "uri": "urn:x-vioe:materials:19"}, {"label": "tin", "type": "concept", "id": 18, "uri": "urn:x-vioe:materials:18"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/MATERIALS/c/0/displaychildren",
        body='[{"label": "koper", "type": "concept", "id": 12, "uri": "urn:x-vioe:materials:12"}, {"label": "staal", "type": "concept", "id": 17, "uri": "urn:x-vioe:materials:17"}, {"label": "ijzer", "type": "concept", "id": 11, "uri": "urn:x-vioe:materials:11"}, {"label": "lood", "type": "concept", "id": 16, "uri": "urn:x-vioe:materials:16"}, {"label": "aluminium", "type": "concept", "id": 48, "uri": "urn:x-vioe:materials:48"}, {"label": "gold", "type": "concept", "id": 9, "uri": "urn:x-vioe:materials:9"}, {"label": "silver", "type": "concept", "id": 19, "uri": "urn:x-vioe:materials:19"}, {"label": "tin", "type": "concept", "id": 18, "uri": "urn:x-vioe:materials:18"}]',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    url_re = re.compile(
        r"http://localhost/conceptschemes/MATERIALS/c/\d+/displaychildren"
    )
    responses.add(
        responses.GET,
        url_re,
        body="[]",
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    url_re = re.compile(r"http://localhost/conceptschemes/STYLES/c/\d+/displaychildren")
    responses.add(
        responses.GET,
        url_re,
        body="[]",
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/TREES/c/2",
        body='{"subordinate_arrays": [], "matches": {"related": ["http://id.python.org/different/types/of/trees/nr/17/the/other/chestnut"]}, "labels": [{"type": "prefLabel", "language": "en", "label": "The Chestnut"}, {"type": "altLabel", "language": "nl", "label": "De Paardekastanje"}, {"type": "altLabel", "language": "fr", "label": "la châtaigne"}], "narrower": [], "related": [], "broader": [], "id": 2, "member_of": [{"labels": [{"type": "prefLabel", "language": "en", "label": "Trees by species"}, {"type": "prefLabel", "language": "nl", "label": "Bomen per soort"}], "label": "Bomen per soort", "type": "collection", "id": 3, "uri": "urn:x-skosprovider:trees/3"}], "notes": [{"note": "<h1>A different type of tree.</h1>", "type": "definition", "language": "en", "markup": "HTML"}], "uri": "urn:x-skosprovider:trees/2", "label": "The Chestnut", "type": "concept"}',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/TREES/c/100/expand",
        body='{"message": "The resource could not be found."}',
        status=404,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/ONBEKEND/c/100/displaychildren",
        body='{"message": "The resource could not be found."}',
        status=404,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/ONBEKEND",
        body='{"message": "The resource could not be found."}',
        status=404,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/ONBEKEND/c/",
        body='{"message": "The resource could not be found."}',
        status=404,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/TREES/c/",
        body='{"message": "The resource could not be found."}',
        status=404,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/ONBEKEND/topconcepts",
        body='{"message": "The resource could not be found."}',
        status=404,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/ONBEKEND/displaytop",
        body='{"message": "The resource could not be found."}',
        status=404,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/TREES/displaytop",
        body='{"message": "The resource could not be found."}',
        status=404,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/TREES/c/3/displaychildren",
        body='{"message": "The resource could not be found."}',
        status=404,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/no_encoding",
        body="no encoding",
        status=404,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "http://localhost/uris?uri=http://localhost/conceptschemes/STYLES/c/1",
        match_querystring=True,
        body='{"id": 1,"type": "concept","concept_scheme": {"id": "STYLES", "uri": "http://localhost/conceptschemes/STYLES"},"uri": "http://localhost/conceptschemes/STYLES/c/1"}',
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "http://localhost/uris?uri=http://localhost/conceptschemes/STYLES/c/1234",
        match_querystring=True,
        body='{"id": 1,"type": "concept","concept_scheme": {"id": "STIJLEN", "uri": "http://localhost/conceptschemes/STIJLEN"},"uri": "http://localhost/conceptschemes/STYLES/c/1234"}',
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "http://localhost/uris?uri=http://localhost/conceptschemes/STYLES/c/1234567",
        match_querystring=True,
        body='{"message": "The resource could not be found."}',
        status=404,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/STYLES",
        body='{"uri": "https://id.erfgoed.net/thesauri/stijlen_en_culturen", "label": "Styles and Cultures", "notes": [], "sources": [], "languages": [], "id": "STYLES", "labels": [{"type": "prefLabel", "label": "Stijlen en Culturen", "language": "nl"}, {"type": "prefLabel", "label": "Styles and Cultures", "language": "en"}], "subject": []}',
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/TREES",
        body='{"uri": "urn:x-skosprovider:trees", "label": "Different types of trees", "notes": [], "sources": [], "languages": [], "id": "TREES", "labels": [{"type": "prefLabel", "label": "Verschillende soorten bomen", "language": "nl"}, {"type": "prefLabel", "label": "Different types of trees", "language": "en"}], "subject": []}',
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/MATERIALS",
        body='{"uri": "https://id.erfgoed.net/thesauri/materialen", "label": "Materials", "notes": [{"type": "definition", "language": "en", "note": "Types of material", "markup": null}], "sources": [{"citation": "citation about materials"}], "languages": ["en"], "id": "MATERIALS", "labels": [{"type": "prefLabel", "label": "Materialen", "language": "nl"}, {"type": "prefLabel", "label": "Materials", "language": "en"}], "subject": []}',
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/ERFGOEDTYPES",
        body='{"notes": [], "labels": [], "uri": "https://id.erfgoed.net/thesauri/erfgoedtypes", "label": "Erfgoedtypes", "id": "ERFGOEDTYPES", "subject": [], "sources": [], "languages": []}',
        status=200,
        content_type="application/json; charset=UTF-8",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/ERFGOEDTYPES/c/?language=en&match=http%3A%2F%2Fvocab.getty.edu%2Faat%2F300004983",
        match_querystring=True,
        body='[{"label": "veekralen", "type": "concept", "id": 1314, "uri": "https://id.erfgoed.net/thesauri/erfgoedtypes/1314"}]',
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/ERFGOEDTYPES/c/?language=en&match=http%3A%2F%2Fvocab.getty.edu%2Faat%2F300004983&match_type=close",
        match_querystring=True,
        body='[{"label": "veekralen", "type": "concept", "id": 1314, "uri": "https://id.erfgoed.net/thesauri/erfgoedtypes/1314"}]',
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "http://localhost/conceptschemes/ERFGOEDTYPES/c/?type=concept&collection=2132&language=en",
        match_querystring=True,
        body='[{"label": "paleobodems", "type": "concept", "id": 2057, "uri": "https://id.erfgoed.net/thesauri/erfgoedtypes/2057"}, {"label": "organische bodems", "type": "concept", "id": 2040, "uri": "https://id.erfgoed.net/thesauri/erfgoedtypes/2040"}]',
        status=200,
        content_type="application/json",
    )
