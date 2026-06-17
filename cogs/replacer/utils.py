import re


URL_REGEX = re.compile(
    r"https?:\/\/\S+",
    re.I
)


def elongation_pattern(
    word: str
):

    return "".join(

        re.escape(c) + "+"

        for c in word

    )


def find_replacement(
    match: str,
    entries
):

    for (
        word,
        replacement
    ) in entries:

        pattern = re.compile(
            rf"^{elongation_pattern(word)}$",
            re.I
        )

        if pattern.match(
            match
        ):

            return replacement

    return None


def preserve_case(
    original,
    replacement
):

    if (
        original
        ==
        original.upper()
    ):

        return (
            replacement
            .upper()
        )

    if (
        original[0]
        ==
        original[0]
        .upper()
    ):

        return (
            replacement[0]
            .upper()
            +
            replacement[1:]
        )

    return replacement


def replace_text(
    text,
    entries
):

    if (
        not entries
    ):

        return text


    pattern = "|".join(

        rf"(?<!\w)"
        rf"{elongation_pattern(word)}"
        rf"(?!\w)"

        for (
            word,
            _
        )

        in entries

    )


    regex = re.compile(
        pattern,
        re.I
    )


    def repl(
        m
    ):

        match = (
            m.group()
        )

        replacement = (
            find_replacement(
                match,
                entries
            )
        )

        if (
            replacement
            is None
        ):

            return match

        return preserve_case(
            match,
            replacement
        )


    return regex.sub(
        repl,
        text
    )


def apply_replacements(
    content: str,
    replacements:
    dict[
        str,
        str
    ]
):

    entries = list(
        replacements
        .items()
    )

    if (
        not entries
    ):

        return content


    result = []

    last = 0


    for url in (
        URL_REGEX
        .finditer(
            content
        )
    ):

        result.append(

            replace_text(

                content[
                    last:
                    url.start()
                ],

                entries

            )

        )

        result.append(
            url.group()
        )

        last = (
            url.end()
        )


    result.append(

        replace_text(

            content[
                last:
            ],

            entries

        )

    )


    return "".join(
        result
    )


def has_mentions(
    text
):

    return bool(

        re.search(

            r"<@|<#|<@&",

            text

        )

    )


def validate_word(
    word,
    limit=100
):

    if (
        len(
            word
        )
        >
        limit
    ):

        raise ValueError(
            f"Maximum length is {limit}"
        )


    if has_mentions(
        word
    ):

        raise ValueError(
            "Mentions not allowed"
        )


def split_message(
    text,
    limit=1900
):

    if (
        len(text)
        <=
        limit
    ):

        return [
            text
        ]


    chunks = []

    current = ""


    for line in (
        text
        .split("\n")
    ):

        next_chunk = (

            current
            +
            "\n"
            +
            line

            if current

            else line

        )

        if (
            len(
                next_chunk
            )
            >
            limit
        ):

            chunks.append(
                current
            )

            current = (
                line
            )

        else:

            current = (
                next_chunk
            )


    if current:

        chunks.append(
            current
        )


    return chunks
