# projects/templatetags/text_links.py
import re
from django import template
from django.urls import reverse, NoReverseMatch
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

def _parse_spec(spec):
    """
    Accepts either:
      - a dict mapping: {"Label A": "url_name_a", "Label B": "url_name_b"}
      - or a string: "Label A=>url_name_a; Label B=>url_name_b"
    Returns list[(label, target)].
    """
    if isinstance(spec, dict):
        return list(spec.items())

    pairs = []
    for part in str(spec).split(";"):
        part = part.strip()
        if not part or "=>" not in part:
            continue
        label, target = [p.strip() for p in part.split("=>", 1)]
        if label and target:
            pairs.append((label, target))
    return pairs

def _resolve_target(target):
    """
    If target looks like a Django URL name, reverse it.
    If reverse fails, allow absolute/relative URLs (http(s) or starting with '/').
    Otherwise return '' to skip.
    """
    try:
        return reverse(target)
    except NoReverseMatch:
        if target.startswith(("http://", "https://", "/")):
            return target
        return ""

def _smart_links(text, spec, replace_all=False, ignore_case=True, link_attrs=""):
    if not text:
        return ""
    pairs = _parse_spec(spec)
    out = escape(text)  # work on escaped text

    # Longest labels first to prevent partial overlaps
    pairs.sort(key=lambda t: len(t[0]), reverse=True)
    flags = re.IGNORECASE if ignore_case else 0

    for label, target in pairs:
        url = _resolve_target(target)
        if not url:
            continue

        label_escaped = escape(label)
        pattern = re.compile(re.escape(label_escaped), flags=flags)

        def repl(m):
            return f'<a href="{url}"{link_attrs}>{m.group(0)}</a>'

        if replace_all:
            out = pattern.sub(repl, out)
        else:
            out, _ = pattern.subn(repl, out, count=1)

    return mark_safe(out)

@register.filter
def smart_links(text, spec):
    """Replace the FIRST occurrence of each label with a link."""
    return _smart_links(text, spec, replace_all=False, ignore_case=True)

@register.filter
def smart_links_all(text, spec):
    """Replace ALL occurrences of each label with a link."""
    return _smart_links(text, spec, replace_all=True, ignore_case=True)

@register.filter
def smart_links_blank(text, spec):
    """First occurrences, opening in a new tab."""
    return _smart_links(
        text, spec,
        replace_all=False,
        ignore_case=True,
        link_attrs=' target="_blank" rel="noopener noreferrer"'
    )

@register.filter
def smart_links_all_blank(text, spec):
    """All occurrences, opening in a new tab."""
    return _smart_links(
        text, spec,
        replace_all=True,
        ignore_case=True,
        link_attrs=' target="_blank" rel="noopener noreferrer"'
    )
