import bleach

def sanitize_html(html: str) -> str:
    allowed_tags = bleach.sanitizer.ALLOWED_TAGS.union({"p","h1","h2","h3","h4","h5","h6","img","span","div","br","strong","em","ul","ol","li","a","table","thead","tbody","tr","th","td","blockquote","code","pre"})
    allowed_attrs = {**bleach.sanitizer.ALLOWED_ATTRIBUTES, "img": ["src","alt","title"], "a": ["href","title","target","rel"], "*": ["class","id","style"]}
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)
