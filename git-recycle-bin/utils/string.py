import re
import urllib.parse

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    if v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    raise ValueError('Boolean value expected.')

def trim_all_lines(input_string: str) -> str:
    """ Trim leading and trailing whitespaces from every line """
    lines = input_string.split('\n')
    trimmed_lines = [line.strip() for line in lines]
    return '\n'.join(trimmed_lines)

def remove_empty_lines(input_string: str) -> str:
    """ Remove empty lines, but preserve leading and trailing whitespaces """
    lines = input_string.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def prefix_lines(lines: str, prefix: str) -> str:
    """ Prepend the same string to start of every line """
    return "\n".join(f"{prefix}{line}" for line in lines.split("\n") if line)

def string_trunc_ellipsis(maxlen: int, longstr: str) -> str:
    if len(longstr) <= maxlen:
        return longstr

    shortstr = longstr[:maxlen]
    if len(shortstr) == maxlen:
        return shortstr[:(maxlen-3)] + "..."
    else:
        return shortstr

def sanitize_slashes(name: str) -> str:
    # replace / with _
    return re.sub(r'/', '_', name)

def sanitize_branch_name(name: str) -> str:
    """
        Git branch names cannot contain: whitespace characters, ~, ^, :, [, ? or *.
        Also they cannot start with / or -, end with ., or contain multiple consecutive /
        Finally, they cannot be @, @{, or have two consecutive dots ..
    """

    # replace unsafe characters with _
    sanitized_name = re.sub(r'[\s~^:\[\]?*]', '_', name)

    # replace starting / or - with _
    sanitized_name = re.sub(r'^[-/]', '_', sanitized_name)

    # replace ending . with _
    sanitized_name = re.sub(r'\.$', '_', sanitized_name)

    # replace // with /
    sanitized_name = re.sub(r'//', '/', sanitized_name)

    # replace .. with .
    sanitized_name = re.sub(r'\.\.', '.', sanitized_name)

    # replace @ and @{ with _
    if sanitized_name in ('@', '@{'):
        sanitized_name = '_'

    return sanitized_name

def url_redact(url: str, replacement: str = 'REDACTED'):
    """ Replace sensitive password/api-token from URL with a string """
    parsed = urllib.parse.urlparse(url)

    # If there is no password, return the original URL
    if not parsed.password:
        return url

    # Redact the password/token
    new_netloc = parsed.netloc.replace(parsed.password, replacement)

    # Reconstruct the URL
    redacted_url = urllib.parse.urlunparse((
        parsed.scheme,
        new_netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))

    return redacted_url
